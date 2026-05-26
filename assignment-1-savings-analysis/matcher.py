"""
Product matcher: 3-pass pipeline
Pass 1: Exact SKU lookup
Pass 2: Fuzzy description match (RapidFuzz)
Pass 3: Claude AI semantic match for ambiguous cases
"""

import os
import re
import json
import pandas as pd
from rapidfuzz import process, fuzz

# ── optional Claude import ──────────────────────────────────────────────────
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


# ── abbreviation expansions ─────────────────────────────────────────────────
ABBREVIATIONS = {
    r"\bbx\b": "box", r"\bpk\b": "pack", r"\bpkg\b": "package",
    r"\bea\b": "each", r"\bcs\b": "case", r"\bct\b": "count",
    r"\bcnt\b": "count", r"\bsyr\b": "syringe", r"\bjar\b": "jar",
    r"\btube\b": "tube", r"\bbag\b": "bag", r"\bbtl\b": "bottle",
    r"\blg\b": "large", r"\bsm\b": "small", r"\bmed\b": "medium",
    r"\bxl\b": "xlarge", r"\bw/\b": "with ", r"\bw\/epi\b": "with epinephrine",
    r"\bepi\b": "epinephrine", r"\bgm\b": "gram", r"\bmg\b": "milligram",
    r"\bml\b": "ml", r"\blb\b": "pound",
}


def normalize_text(text: str) -> str:
    """Lowercase, expand abbreviations, strip punctuation."""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = text.lower().strip()
    for pattern, replacement in ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_sku(sku) -> str:
    """Strip non-alphanumerics, uppercase."""
    if pd.isna(sku) or not isinstance(sku, str):
        return ""
    return re.sub(r"[^A-Z0-9]", "", sku.upper())


class ProductMatcher:
    def __init__(self, catalog_df: pd.DataFrame, use_claude: bool = True, model: str = "claude-haiku-4-5-20251001"):
        self.catalog = catalog_df.copy()
        self.use_claude = use_claude and CLAUDE_AVAILABLE
        self.model = model
        self.client = None

        if self.use_claude:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key, max_retries=3)
            else:
                print("⚠️  ANTHROPIC_API_KEY not set — running fuzzy-only mode")
                self.use_claude = False

        # Build SKU lookup dicts
        self._sku_index: dict[str, int] = {}
        for idx, row in self.catalog.iterrows():
            for sku_col in ["supplier_sku", "manufacturer_sku"]:
                norm = normalize_sku(row.get(sku_col, ""))
                if norm:
                    self._sku_index[norm] = idx

        # Build normalized description list for fuzzy search
        self._desc_list = [
            normalize_text(row["description"]) for _, row in self.catalog.iterrows()
        ]

    # ── Pass 1: Exact SKU ────────────────────────────────────────────────────
    def match_exact_sku(self, supplier_sku, manufacturer_sku):
        for raw in [supplier_sku, manufacturer_sku]:
            norm = normalize_sku(raw)
            if norm and norm in self._sku_index:
                idx = self._sku_index[norm]
                return self.catalog.loc[idx], 100, "exact_sku"
        return None, 0, None

    # ── Pass 2: Fuzzy description ────────────────────────────────────────────
    def match_fuzzy(self, description: str, threshold: int = 72):
        norm = normalize_text(description)
        if not norm:
            return None, 0, None
        result = process.extractOne(
            norm,
            self._desc_list,
            scorer=fuzz.token_sort_ratio,
        )
        if result and result[1] >= threshold:
            idx = result[2]
            return self.catalog.iloc[idx], result[1], "fuzzy"
        return None, 0, None

    # ── Pass 3: Claude AI (batched) ──────────────────────────────────────────
    def match_with_claude(self, unresolved: list[dict]) -> list[dict]:
        """
        Takes a list of dicts: {row_index, description, supplier_sku, manufacturer_sku, candidates}
        Returns a list of dicts: {row_index, catalog_id, confidence, reasoning}
        """
        if not self.client or not unresolved:
            return []

        # Build catalog summary for context (top-level categories + sample items)
        catalog_summary = self.catalog[["catalog_id", "description", "category"]].to_dict(orient="records")

        prompt_items = []
        for item in unresolved:
            prompt_items.append({
                "row_index": item["row_index"],
                "prospect_description": item["description"],
                "prospect_supplier_sku": str(item.get("supplier_sku", "")),
                "prospect_manufacturer_sku": str(item.get("manufacturer_sku", "")),
                "fuzzy_candidates": item.get("candidates", []),
            })

        system = (
            "You are a dental supply product matching expert. "
            "Match prospect purchase history items to the closest Source Club catalog items. "
            "Consider product type, size, unit, and pack size when matching. "
            "Return ONLY valid JSON — no markdown, no explanation outside the JSON."
        )

        user = f"""Match each prospect item to the best Source Club catalog entry.

Source Club Catalog:
{json.dumps(catalog_summary, indent=2)}

Items to match:
{json.dumps(prompt_items, indent=2)}

Return a JSON array, one object per item:
[
  {{
    "row_index": <number>,
    "catalog_id": "<SC-XXX or null if no match>",
    "confidence": <0-100>,
    "reasoning": "<one sentence>"
  }}
]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            raw = response.content[0].text.strip()
            # Strip markdown code fences if present
            raw = re.sub(r"^```(?:json)?\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
            return json.loads(raw)
        except Exception as e:
            print(f"⚠️  Claude API error: {e} — falling back to fuzzy results")
            return []

    # ── Confidence tier ──────────────────────────────────────────────────────
    @staticmethod
    def confidence_tier(score: int) -> str:
        if score >= 90:
            return "HIGH"
        if score >= 70:
            return "MEDIUM"
        return "LOW"
