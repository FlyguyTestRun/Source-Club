"""
Shared Streamlit UI for the Source Club Savings Analyzer.

Both entry points call render_savings_app():
  - assignment-1-savings-analysis/app.py  (standalone)
  - pages/1_💰_Savings_Analysis.py        (multipage app)

Keeping the UI + run loop here means one source of truth for the matching logic.
"""

import io
import os
import pandas as pd
import streamlit as st

from matcher import ProductMatcher, normalize_text
from report_generator import generate_summary

# ── Column aliases — map common supplier export headers → internal names ──────
PROSPECT_ALIASES = {
    "supplier_sku":      ["supplier_sku", "supplier sku", "supplier#", "order#", "item number",
                          "item#", "item no", "item no.", "product number", "prod#", "order item"],
    "manufacturer_sku":  ["manufacturer_sku", "mfr sku", "mfr#", "manufacturer#",
                          "manufacturer item", "mfr item", "catalog#", "cat#"],
    "description":       ["description", "product description", "item description",
                          "product name", "item name", "name", "product", "desc"],
    "quantity_per_year": ["quantity_per_year", "qty per year", "annual qty", "annual quantity",
                          "qty ordered", "quantity ordered", "qty", "quantity", "units ordered",
                          "total qty", "total quantity"],
    "unit_price":        ["unit_price", "unit price", "price", "your price", "net price",
                          "cost", "unit cost", "price each", "each price", "contract price"],
    "pack_size":         ["pack_size", "pack size", "pkg size", "package size",
                          "uom qty", "quantity per pack", "units per pack"],
    "unit_of_measure":   ["unit_of_measure", "unit of measure", "uom", "sell unit",
                          "selling unit", "unit"],
    "annual_spend":      ["annual_spend", "annual spend", "total spend", "total cost",
                          "ext. price", "extended price", "total", "amount"],
}

CATALOG_ALIASES = {
    "catalog_id":        ["catalog_id", "catalog id", "sc id", "source club id", "id"],
    "manufacturer_sku":  ["manufacturer_sku", "mfr sku", "mfr#", "manufacturer item", "cat#"],
    "supplier_sku":      ["supplier_sku", "supplier sku", "supplier item", "item#"],
    "description":       ["description", "product description", "product name", "item name", "name"],
    "pack_size":         ["pack_size", "pack size", "pkg size", "quantity per pack"],
    "unit_of_measure":   ["unit_of_measure", "uom", "unit of measure", "unit"],
    "source_club_price": ["source_club_price", "sc price", "member price", "negotiated price",
                          "price", "cost", "unit price"],
    "category":          ["category", "product category", "dept", "department", "type"],
}

REQUIRED = ("description", "unit_price", "quantity_per_year", "source_club_price", "catalog_id")


# ── File / column helpers ─────────────────────────────────────────────────────
def _resolve_file(uploaded, sample_key):
    if uploaded is not None:
        return uploaded
    sample = st.session_state.get(sample_key)
    if sample:
        data, name = sample
        buf = io.BytesIO(data)
        buf.name = name
        return buf
    return None


def load_file(uploaded_file):
    name = getattr(uploaded_file, "name", "file.csv")
    if name.endswith((".xlsx", ".xls")):
        xl = pd.ExcelFile(uploaded_file)
        return xl, xl.sheet_names
    return pd.read_csv(uploaded_file), []


def auto_map_columns(df, aliases):
    cols_lower = {c.lower().strip(): c for c in df.columns}
    return {internal: next((cols_lower[c] for c in candidates if c in cols_lower), None)
            for internal, candidates in aliases.items()}


def apply_mapping(df, mapping):
    rename = {v: k for k, v in mapping.items() if v and v != k}
    df = df.rename(columns=rename)
    for col in mapping:
        if col not in df.columns:
            df[col] = ""
    return df


def render_column_mapper(df, aliases, label, key_prefix):
    auto = auto_map_columns(df, aliases)
    all_cols = ["(skip / not in file)"] + list(df.columns)
    missing_required = [k for k, v in auto.items() if v is None and k in REQUIRED]
    mapping = dict(auto)
    with st.expander(
        f"{'⚠️' if missing_required else '✅'} Column mapping — {label}",
        expanded=bool(missing_required),
    ):
        if missing_required:
            st.warning(f"Could not auto-detect: **{', '.join(missing_required)}** — map them below.")
        else:
            st.success("All required columns auto-detected. Expand to override if needed.")
        cols_ui = st.columns(3)
        for i, internal in enumerate(aliases):
            current = auto.get(internal)
            idx = all_cols.index(current) if current in all_cols else 0
            sel = cols_ui[i % 3].selectbox(
                internal.replace("_", " ").title(), all_cols, index=idx,
                key=f"{key_prefix}_{internal}",
            )
            mapping[internal] = None if sel == "(skip / not in file)" else sel
    return mapping


# ── Savings math (pack-size aware) ────────────────────────────────────────────
def _to_float(val, default=0.0):
    try:
        f = float(val)
        return f if pd.notna(f) else default
    except (TypeError, ValueError):
        return default


def compute_line_savings(prospect_price, sc_price, qty,
                         prospect_pack, sc_pack, prospect_uom, sc_uom):
    """
    Return (their_unit_price, sc_unit_price, line_savings, basis).

    When both pack sizes are present (>0) AND the units of measure match, prices
    are normalized to a per-single-item basis before comparison — so "100/box @ $18"
    vs "50/box @ $10" compares correctly. Otherwise (missing pack size, or mismatched
    units like grams vs pounds where per-unit division is meaningless) it falls back
    to the direct pack-price comparison.
    """
    pp = _to_float(prospect_price)
    sc = _to_float(sc_price)
    q = _to_float(qty, 1.0) or 1.0
    p_pack = _to_float(prospect_pack)
    c_pack = _to_float(sc_pack)
    uom_match = normalize_text(str(prospect_uom)) == normalize_text(str(sc_uom))

    if p_pack > 0 and c_pack > 0 and uom_match:
        their_unit = pp / p_pack
        sc_unit = sc / c_pack
        total_items = p_pack * q
        line = max(0.0, their_unit - sc_unit) * total_items
        return round(their_unit, 4), round(sc_unit, 4), round(line, 2), "per_unit"

    line = max(0.0, pp - sc) * q
    return round(pp, 4), round(sc, 4), round(line, 2), "per_pack"


# ── Main entry point ──────────────────────────────────────────────────────────
def render_savings_app(sample_prospect_path, sample_catalog_path, *,
                       title, caption, show_back_link=False):
    st.title(title)
    st.caption(caption)

    with st.sidebar:
        st.header("⚙️ Settings")
        use_ai = st.toggle(
            "Use Claude AI for ambiguous matches",
            value=bool(os.getenv("ANTHROPIC_API_KEY")),
            help="Requires ANTHROPIC_API_KEY in .env",
        )
        fuzzy_threshold = st.slider("Fuzzy match threshold", 60, 95, 72)
        st.divider()
        st.markdown("**Match pipeline:**\n1. Exact SKU lookup\n2. Fuzzy (RapidFuzz)\n3. Claude AI (if on)")
        st.divider()
        st.markdown("**Confidence:**\n🟢 HIGH ≥ 90 &nbsp; 🟡 MED ≥ 70 &nbsp; 🔴 LOW < 70")
        if show_back_link:
            st.divider()
            st.page_link("app.py", label="← Back to Home")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Prospect Purchase History")
        st.caption("CSV or Excel — Benco, Patterson, Schein, any format")
        prospect_upload = st.file_uploader("Upload", type=["csv", "xlsx", "xls"], key="prospect")
        if st.button("Load sample →", key="lp"):
            with open(sample_prospect_path, "rb") as f:
                st.session_state["sample_prospect"] = (f.read(), os.path.basename(sample_prospect_path))
    with col2:
        st.subheader("📋 Source Club Catalog")
        st.caption("CSV or Excel — your negotiated pricing")
        catalog_upload = st.file_uploader("Upload", type=["csv", "xlsx", "xls"], key="catalog")
        if st.button("Load sample →", key="lc"):
            with open(sample_catalog_path, "rb") as f:
                st.session_state["sample_catalog"] = (f.read(), os.path.basename(sample_catalog_path))

    # Uploaded files take priority; otherwise fall back to a loaded sample (persisted
    # in session_state so it survives the rerun and the Run button can use it).
    prospect_file = _resolve_file(prospect_upload, "sample_prospect")
    catalog_file = _resolve_file(catalog_upload, "sample_catalog")

    if not (prospect_file and catalog_file):
        st.info("👆 Upload both files (CSV or Excel) — or click **Load sample** for a live demo.")
        return

    raw_p, p_sheets = load_file(prospect_file)
    raw_c, c_sheets = load_file(catalog_file)

    c1, c2 = st.columns(2)
    prospect_df = raw_p.parse(c1.selectbox("Sheet", p_sheets, key="sp")) if p_sheets else raw_p
    catalog_df = raw_c.parse(c2.selectbox("Sheet", c_sheets, key="sc")) if c_sheets else raw_c

    prospect_df = prospect_df.dropna(how="all").reset_index(drop=True)
    catalog_df = catalog_df.dropna(how="all").reset_index(drop=True)
    st.markdown(f"**Prospect:** {len(prospect_df)} rows &nbsp;|&nbsp; **Catalog:** {len(catalog_df)} items")

    st.divider()
    p_map = render_column_mapper(prospect_df, PROSPECT_ALIASES, "Purchase History", "p")
    c_map = render_column_mapper(catalog_df, CATALOG_ALIASES, "Catalog", "c")
    prospect_mapped = apply_mapping(prospect_df.copy(), p_map)
    catalog_mapped = apply_mapping(catalog_df.copy(), c_map)

    st.divider()
    if st.button("▶️ Run Savings Analysis", type="primary", width="stretch"):
        with st.spinner("Matching…"):
            st.session_state["results_df"] = _run_pipeline(
                prospect_mapped, catalog_mapped, use_ai, fuzzy_threshold
            )

    if "results_df" in st.session_state:
        _render_results(st.session_state["results_df"])


def _row_result(i, row, match, score, method, matcher):
    their_unit, sc_unit, line, basis = compute_line_savings(
        row.get("unit_price", 0), match.get("source_club_price", 0),
        row.get("quantity_per_year", 1),
        row.get("pack_size", 0), match.get("pack_size", 0),
        row.get("unit_of_measure", ""), match.get("unit_of_measure", ""),
    )
    return {
        "row_index": i,
        "prospect_description": row.get("description", ""),
        "matched_catalog_id": match.get("catalog_id", ""),
        "matched_description": match.get("description", ""),
        "match_method": method,
        "match_score": score,
        "confidence_tier": matcher.confidence_tier(score),
        "prospect_price": _to_float(row.get("unit_price", 0)),
        "source_club_price": _to_float(match.get("source_club_price", 0)),
        "their_unit_price": their_unit,
        "sc_unit_price": sc_unit,
        "savings_basis": basis,
        "quantity_per_year": _to_float(row.get("quantity_per_year", 1), 1.0),
        "line_savings": line,
    }


def _unmatched_result(i, row):
    return {
        "row_index": i,
        "prospect_description": row.get("description", ""),
        "matched_catalog_id": "", "matched_description": "",
        "match_method": "none", "match_score": 0, "confidence_tier": "LOW",
        "prospect_price": _to_float(row.get("unit_price", 0)),
        "source_club_price": 0.0, "their_unit_price": 0.0, "sc_unit_price": 0.0,
        "savings_basis": "none",
        "quantity_per_year": _to_float(row.get("quantity_per_year", 1), 1.0),
        "line_savings": 0.0,
    }


def _run_pipeline(prospect_mapped, catalog_mapped, use_ai, fuzzy_threshold):
    matcher = ProductMatcher(catalog_mapped, use_claude=use_ai)
    results, claude_batch = [], []

    for i, row in prospect_mapped.iterrows():
        match, score, method = matcher.match_exact_sku(
            row.get("supplier_sku"), row.get("manufacturer_sku"))
        if match is None:
            match, score, method = matcher.match_fuzzy(
                str(row.get("description", "")), threshold=fuzzy_threshold)

        if match is not None:
            results.append(_row_result(i, row, match, score, method, matcher))
        elif use_ai and matcher.use_claude:
            from rapidfuzz import process as rfp, fuzz as rff
            cands = rfp.extract(
                str(row.get("description", "")),
                [matcher.catalog.iloc[j]["description"] for j in range(len(matcher.catalog))],
                scorer=rff.token_sort_ratio, limit=3)
            claude_batch.append({
                "row_index": i, "description": str(row.get("description", "")),
                "supplier_sku": str(row.get("supplier_sku", "")),
                "manufacturer_sku": str(row.get("manufacturer_sku", "")),
                "candidates": [{"description": c[0], "score": c[1]} for c in cands],
                "_row": row,
            })
        else:
            results.append(_unmatched_result(i, row))

    if claude_batch:
        ai_res = matcher.match_with_claude(
            [{k: v for k, v in it.items() if k != "_row"} for it in claude_batch])
        ai_map = {r["row_index"]: r for r in ai_res}
        for item in claude_batch:
            i, row, ai = item["row_index"], item["_row"], ai_map.get(item["row_index"])
            if ai and ai.get("catalog_id") and ai["catalog_id"] != "null":
                cm = catalog_mapped[catalog_mapped["catalog_id"] == ai["catalog_id"]]
                if not cm.empty:
                    results.append(_row_result(
                        i, row, cm.iloc[0], int(ai.get("confidence", 70)), "ai", matcher))
                    continue
            results.append(_unmatched_result(i, row))

    return pd.DataFrame(results).sort_values("row_index").reset_index(drop=True)


def _render_results(results_df):
    summary = generate_summary(results_df)
    st.divider()
    st.subheader("📊 Results")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Annual Savings", f"${summary['total_annual_savings']:,.0f}")
    m2.metric("Match Rate", f"{summary['match_rate_pct']}%")
    m3.metric("🟢 High", summary["high_confidence"])
    m4.metric("🟡 Review", summary["medium_confidence"] + summary["low_confidence"])
    m5.metric("❌ Unmatched", summary["unmatched_count"])

    def ct(val):
        return {"HIGH": "background-color:#d4edda", "MEDIUM": "background-color:#fff3cd",
                "LOW": "background-color:#f8d7da"}.get(val, "")

    dcols = {"prospect_description": "Item", "matched_description": "Matched",
             "match_method": "Method", "confidence_tier": "Confidence",
             "their_unit_price": "Their $/unit", "sc_unit_price": "SC $/unit",
             "quantity_per_year": "Qty/Yr", "line_savings": "Savings $"}

    tab1, tab2, tab3 = st.tabs(["All Results", "Needs Review", "Unmatched"])
    with tab1:
        st.dataframe(results_df[list(dcols)].rename(columns=dcols)
                     .style.map(ct, subset=["Confidence"]),
                     width="stretch", height=420)
    with tab2:
        rev = results_df[results_df["confidence_tier"].isin(["MEDIUM", "LOW"])
                         & (results_df["matched_catalog_id"] != "")]
        if rev.empty:
            st.success("All matched items are HIGH confidence!")
        else:
            st.caption("Lower-confidence matches — a quick human review confirms or corrects.")
            st.dataframe(rev[list(dcols)].rename(columns=dcols)
                         .style.map(ct, subset=["Confidence"]), width="stretch")
    with tab3:
        unm = results_df[results_df["matched_catalog_id"] == ""]
        if unm.empty:
            st.success("All items matched!")
        else:
            st.caption("Couldn't be matched — Source Club may not carry these, or they need manual review.")
            st.dataframe(unm[["prospect_description", "prospect_price", "quantity_per_year"]],
                         width="stretch")

    st.divider()
    buf = io.StringIO()
    results_df.to_csv(buf, index=False)
    st.download_button("⬇️ Download Report (CSV)", buf.getvalue(),
                       "savings_report.csv", "text/csv", width="stretch")
