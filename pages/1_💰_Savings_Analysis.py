"""
Assignment 1 — Savings Analysis Automation
Handles real-world supplier exports: CSV or Excel, any column names.
"""

import sys
import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assignment-1-savings-analysis"))

from matcher import ProductMatcher
from report_generator import generate_full_report, generate_summary

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
load_dotenv(
    os.path.join(os.path.dirname(__file__), "..", "assignment-1-savings-analysis", ".env"),
    override=False,
)

SAMPLE_PROSPECT = os.path.join(
    os.path.dirname(__file__), "..", "assignment-1-savings-analysis",
    "sample_data", "prospect_purchase_history.csv"
)
SAMPLE_CATALOG = os.path.join(
    os.path.dirname(__file__), "..", "assignment-1-savings-analysis",
    "sample_data", "source_club_catalog.csv"
)

# ── Column name aliases — maps common supplier export headers → our internal names ──
# Add more aliases here as new supplier formats are discovered
PROSPECT_ALIASES = {
    "supplier_sku":        ["supplier_sku", "supplier sku", "supplier#", "order#", "item number",
                            "item#", "item no", "item no.", "product number", "prod#", "order item"],
    "manufacturer_sku":    ["manufacturer_sku", "mfr sku", "mfr#", "manufacturer#",
                            "manufacturer item", "mfr item", "catalog#", "cat#"],
    "description":         ["description", "product description", "item description",
                            "product name", "item name", "name", "product", "desc"],
    "quantity_per_year":   ["quantity_per_year", "qty per year", "annual qty", "annual quantity",
                            "qty ordered", "quantity ordered", "qty", "quantity", "units ordered",
                            "total qty", "total quantity"],
    "unit_price":          ["unit_price", "unit price", "price", "your price", "net price",
                            "cost", "unit cost", "price each", "each price", "contract price"],
    "pack_size":           ["pack_size", "pack size", "pkg size", "package size",
                            "uom qty", "quantity per pack", "units per pack"],
    "unit_of_measure":     ["unit_of_measure", "unit of measure", "uom", "sell unit",
                            "selling unit", "unit"],
    "annual_spend":        ["annual_spend", "annual spend", "total spend", "total cost",
                            "ext. price", "extended price", "total", "amount"],
}

CATALOG_ALIASES = {
    "catalog_id":          ["catalog_id", "catalog id", "sc id", "source club id", "id"],
    "manufacturer_sku":    ["manufacturer_sku", "mfr sku", "mfr#", "manufacturer item", "cat#"],
    "supplier_sku":        ["supplier_sku", "supplier sku", "supplier item", "item#"],
    "description":         ["description", "product description", "product name", "item name", "name"],
    "pack_size":           ["pack_size", "pack size", "pkg size", "quantity per pack"],
    "unit_of_measure":     ["unit_of_measure", "uom", "unit of measure", "unit"],
    "source_club_price":   ["source_club_price", "sc price", "member price", "negotiated price",
                            "price", "cost", "unit price"],
    "category":            ["category", "product category", "dept", "department", "type"],
}


def load_file(uploaded_file) -> tuple[pd.DataFrame, list[str]]:
    """Load CSV or Excel file; if Excel has multiple sheets, return sheet names for user selection."""
    name = getattr(uploaded_file, "name", "file.csv")
    if name.endswith((".xlsx", ".xls")):
        xl = pd.ExcelFile(uploaded_file)
        return xl, xl.sheet_names
    else:
        df = pd.read_csv(uploaded_file)
        return df, []


def auto_map_columns(df: pd.DataFrame, aliases: dict) -> dict:
    """Auto-detect column mappings based on alias list. Returns {internal_name: actual_col | None}."""
    cols_lower = {c.lower().strip(): c for c in df.columns}
    mapping = {}
    for internal, candidates in aliases.items():
        matched = next((cols_lower[c] for c in candidates if c in cols_lower), None)
        mapping[internal] = matched
    return mapping


def apply_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Rename columns per mapping; fill missing required columns with empty strings."""
    rename = {v: k for k, v in mapping.items() if v and v != k}
    df = df.rename(columns=rename)
    for col in mapping:
        if col not in df.columns:
            df[col] = ""
    return df


# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Savings Analysis", page_icon="💰", layout="wide")

st.title("💰 Assignment 1 — Savings Analysis Automation")
st.caption("Upload a prospect's purchase history + the Source Club catalog → instant savings report.")

with st.sidebar:
    st.header("⚙️ Settings")
    use_ai = st.toggle(
        "Use Claude AI for ambiguous matches",
        value=bool(os.getenv("ANTHROPIC_API_KEY")),
        help="Requires ANTHROPIC_API_KEY in .env",
    )
    fuzzy_threshold = st.slider("Fuzzy match threshold", 60, 95, 72)
    st.divider()
    st.markdown("**Match pipeline:**")
    st.markdown("1. Exact SKU lookup\n2. Fuzzy description (RapidFuzz)\n3. Claude AI (if enabled)")
    st.divider()
    st.markdown("**Confidence tiers:**")
    st.markdown("🟢 HIGH ≥ 90 &nbsp; 🟡 MEDIUM ≥ 70 &nbsp; 🔴 LOW < 70")
    st.divider()
    st.page_link("app.py", label="← Back to Home")


# ── File upload section ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Prospect Purchase History")
    st.caption("CSV or Excel — any supplier format (Benco, Patterson, Schein, etc.)")
    prospect_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"], key="prospect")
    if st.button("Load sample data →", key="load_prospect"):
        with open(SAMPLE_PROSPECT, "rb") as f:
            prospect_file = io.BytesIO(f.read())
            prospect_file.name = "prospect_purchase_history.csv"

with col2:
    st.subheader("📋 Source Club Catalog")
    st.caption("CSV or Excel — your negotiated pricing catalog")
    catalog_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"], key="catalog")
    if st.button("Load sample catalog →", key="load_catalog"):
        with open(SAMPLE_CATALOG, "rb") as f:
            catalog_file = io.BytesIO(f.read())
            catalog_file.name = "source_club_catalog.csv"


def render_column_mapper(df: pd.DataFrame, aliases: dict, label: str, key_prefix: str) -> dict:
    """Render an expander with column mapping dropdowns. Returns final mapping dict."""
    auto = auto_map_columns(df, aliases)
    all_cols = ["(skip / not in file)"] + list(df.columns)

    # Show expander only if any column was NOT auto-detected
    missing = [k for k, v in auto.items() if v is None]
    required_missing = [m for m in missing if m in ("description", "unit_price", "quantity_per_year",
                                                       "source_club_price", "catalog_id")]

    if required_missing:
        icon = "⚠️"
        default_open = True
    else:
        icon = "✅"
        default_open = False

    mapping = dict(auto)
    with st.expander(f"{icon} Column mapping — {label}", expanded=default_open):
        if not required_missing:
            st.success("All required columns auto-detected. Expand to override if needed.")
        else:
            st.warning(f"Could not auto-detect: **{', '.join(required_missing)}** — please map them below.")

        cols_ui = st.columns(3)
        for i, (internal, candidates) in enumerate(aliases.items()):
            current = auto.get(internal)
            default_idx = all_cols.index(current) if current in all_cols else 0
            selected = cols_ui[i % 3].selectbox(
                internal.replace("_", " ").title(),
                options=all_cols,
                index=default_idx,
                key=f"{key_prefix}_{internal}",
            )
            mapping[internal] = None if selected == "(skip / not in file)" else selected

    return mapping


# ── Process files once both are uploaded ─────────────────────────────────────
if prospect_file and catalog_file:

    # ── Load with sheet selection for Excel ──────────────────────────────────
    raw_prospect, p_sheets = load_file(prospect_file)
    raw_catalog, c_sheets = load_file(catalog_file)

    col_p, col_c = st.columns(2)
    if p_sheets:
        with col_p:
            sheet_p = st.selectbox("Select sheet — Purchase History", p_sheets, key="sheet_p")
            prospect_df = raw_prospect.parse(sheet_p)
    else:
        prospect_df = raw_prospect

    if c_sheets:
        with col_c:
            sheet_c = st.selectbox("Select sheet — Catalog", c_sheets, key="sheet_c")
            catalog_df = raw_catalog.parse(sheet_c)
    else:
        catalog_df = raw_catalog

    # Drop fully empty rows that Excel exports often include
    prospect_df = prospect_df.dropna(how="all").reset_index(drop=True)
    catalog_df = catalog_df.dropna(how="all").reset_index(drop=True)

    st.markdown(f"**Prospect:** {len(prospect_df)} rows &nbsp;|&nbsp; **Catalog:** {len(catalog_df)} items")

    # ── Column mapping ────────────────────────────────────────────────────────
    st.divider()
    p_mapping = render_column_mapper(prospect_df, PROSPECT_ALIASES, "Purchase History", "p")
    c_mapping = render_column_mapper(catalog_df, CATALOG_ALIASES, "Catalog", "c")

    prospect_mapped = apply_mapping(prospect_df.copy(), p_mapping)
    catalog_mapped = apply_mapping(catalog_df.copy(), c_mapping)

    # ── Run analysis button ───────────────────────────────────────────────────
    st.divider()
    run_btn = st.button("▶️ Run Savings Analysis", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Running matching pipeline…"):
            matcher = ProductMatcher(catalog_mapped, use_claude=use_ai)
            results = []
            claude_batch = []

            for i, row in prospect_mapped.iterrows():
                match, score, method = matcher.match_exact_sku(
                    row.get("supplier_sku"), row.get("manufacturer_sku")
                )
                if match is None:
                    match, score, method = matcher.match_fuzzy(
                        str(row.get("description", "")), threshold=fuzzy_threshold
                    )

                if match is not None:
                    sc_price = float(match.get("source_club_price", 0) or 0)
                    pp = float(row.get("unit_price", 0) or 0)
                    qty = float(row.get("quantity_per_year", 1) or 1)
                    line_savings = max(0.0, (pp - sc_price) * qty)
                    tier = matcher.confidence_tier(score)
                    results.append({
                        "row_index": i,
                        "prospect_description": row.get("description", ""),
                        "matched_catalog_id": match.get("catalog_id", ""),
                        "matched_description": match.get("description", ""),
                        "match_method": method,
                        "match_score": score,
                        "confidence_tier": tier,
                        "prospect_price": pp,
                        "source_club_price": sc_price,
                        "quantity_per_year": qty,
                        "line_savings": round(line_savings, 2),
                    })
                else:
                    if use_ai and matcher.use_claude:
                        from rapidfuzz import process as rfp, fuzz as rff
                        cands_raw = rfp.extract(
                            str(row.get("description", "")),
                            [matcher.catalog.iloc[j]["description"] for j in range(len(matcher.catalog))],
                            scorer=rff.token_sort_ratio, limit=3,
                        )
                        claude_batch.append({
                            "row_index": i,
                            "description": str(row.get("description", "")),
                            "supplier_sku": str(row.get("supplier_sku", "")),
                            "manufacturer_sku": str(row.get("manufacturer_sku", "")),
                            "candidates": [{"description": c[0], "score": c[1]} for c in cands_raw],
                            "_row": row,
                        })
                    else:
                        results.append({
                            "row_index": i,
                            "prospect_description": row.get("description", ""),
                            "matched_catalog_id": "", "matched_description": "",
                            "match_method": "none", "match_score": 0, "confidence_tier": "LOW",
                            "prospect_price": float(row.get("unit_price", 0) or 0),
                            "source_club_price": 0.0,
                            "quantity_per_year": float(row.get("quantity_per_year", 1) or 1),
                            "line_savings": 0.0,
                        })

            if claude_batch:
                ai_results = matcher.match_with_claude(
                    [{k: v for k, v in item.items() if k != "_row"} for item in claude_batch]
                )
                ai_map = {r["row_index"]: r for r in ai_results}
                for item in claude_batch:
                    i = item["row_index"]
                    row = item["_row"]
                    ai = ai_map.get(i)
                    if ai and ai.get("catalog_id") and ai["catalog_id"] != "null":
                        cat_match = catalog_mapped[catalog_mapped["catalog_id"] == ai["catalog_id"]]
                        if not cat_match.empty:
                            m = cat_match.iloc[0]
                            sc_price = float(m.get("source_club_price", 0) or 0)
                            pp = float(row.get("unit_price", 0) or 0)
                            qty = float(row.get("quantity_per_year", 1) or 1)
                            score = int(ai.get("confidence", 70))
                            results.append({
                                "row_index": i,
                                "prospect_description": row.get("description", ""),
                                "matched_catalog_id": ai["catalog_id"],
                                "matched_description": m.get("description", ""),
                                "match_method": "ai", "match_score": score,
                                "confidence_tier": matcher.confidence_tier(score),
                                "prospect_price": pp, "source_club_price": sc_price,
                                "quantity_per_year": qty,
                                "line_savings": round(max(0.0, (pp - sc_price) * qty), 2),
                            })
                            continue
                    results.append({
                        "row_index": i, "prospect_description": row.get("description", ""),
                        "matched_catalog_id": "", "matched_description": "",
                        "match_method": "none", "match_score": 0, "confidence_tier": "LOW",
                        "prospect_price": float(row.get("unit_price", 0) or 0),
                        "source_club_price": 0.0,
                        "quantity_per_year": float(row.get("quantity_per_year", 1) or 1),
                        "line_savings": 0.0,
                    })

        results_df = pd.DataFrame(results).sort_values("row_index").reset_index(drop=True)
        summary = generate_summary(results_df)
        st.session_state["results_df"] = results_df
        st.session_state["summary"] = summary

    # ── Show results (persists across reruns) ─────────────────────────────────
    if "results_df" in st.session_state:
        results_df = st.session_state["results_df"]
        summary = st.session_state["summary"]

        st.divider()
        st.subheader("📊 Results Summary")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💰 Est. Annual Savings", f"${summary['total_annual_savings']:,.0f}")
        m2.metric("✅ Match Rate", f"{summary['match_rate_pct']}%")
        m3.metric("🟢 High Confidence", summary["high_confidence"])
        m4.metric("🟡 Needs Review", summary["medium_confidence"] + summary["low_confidence"])
        m5.metric("❌ Unmatched", summary["unmatched_count"])

        # ── Tabs: All results / Needs review / Unmatched ────────────────────
        tab_all, tab_review, tab_unmatched = st.tabs([
            f"📋 All Matches ({len(results_df)})",
            f"🟡 Needs Review ({summary['medium_confidence'] + summary['low_confidence']})",
            f"❌ Unmatched ({summary['unmatched_count']})",
        ])

        def color_tier(val):
            return {
                "HIGH": "background-color: #d4edda",
                "MEDIUM": "background-color: #fff3cd",
                "LOW": "background-color: #f8d7da",
            }.get(val, "")

        display_cols = {
            "prospect_description": "Prospect Item",
            "matched_description": "Matched SC Item",
            "match_method": "Method",
            "confidence_tier": "Confidence",
            "prospect_price": "Their Price ($)",
            "source_club_price": "SC Price ($)",
            "quantity_per_year": "Qty/Yr",
            "line_savings": "Annual Savings ($)",
        }

        with tab_all:
            show_df = results_df[list(display_cols.keys())].rename(columns=display_cols)
            st.dataframe(
                show_df.style.applymap(color_tier, subset=["Confidence"]),
                use_container_width=True, height=450,
            )

        with tab_review:
            rev = results_df[results_df["confidence_tier"].isin(["MEDIUM", "LOW"])]
            if rev.empty:
                st.success("No items need review — all matches are HIGH confidence!")
            else:
                st.caption("These items matched but with lower confidence. A quick human review confirms or corrects.")
                show_rev = rev[list(display_cols.keys())].rename(columns=display_cols)
                st.dataframe(
                    show_rev.style.applymap(color_tier, subset=["Confidence"]),
                    use_container_width=True,
                )

        with tab_unmatched:
            unm = results_df[results_df["matched_catalog_id"] == ""]
            if unm.empty:
                st.success("All items matched!")
            else:
                st.caption("These items couldn't be matched — Source Club may not carry them, or the description needs manual review.")
                st.dataframe(
                    unm[["prospect_description", "prospect_price", "quantity_per_year"]].rename(columns={
                        "prospect_description": "Item",
                        "prospect_price": "Their Price ($)",
                        "quantity_per_year": "Qty/Yr",
                    }),
                    use_container_width=True,
                )

        # ── Top savings ──────────────────────────────────────────────────────
        if summary["top_savings_items"]:
            st.subheader("🏆 Top 5 Savings Opportunities")
            st.dataframe(pd.DataFrame(summary["top_savings_items"]), use_container_width=True)

        # ── Download ─────────────────────────────────────────────────────────
        st.divider()
        csv_buf = io.StringIO()
        results_df.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download Full Report (CSV)",
            csv_buf.getvalue(),
            "savings_analysis_report.csv",
            "text/csv",
            use_container_width=True,
        )

else:
    st.info("👆 Upload both files above (CSV or Excel) — or click **Load sample data** for an instant demo.")

    with st.expander("ℹ️ What column names does this accept?"):
        st.markdown("""
The app **auto-detects column names** from common supplier formats. If it can't detect a column,
you'll see a mapping UI to manually assign it.

**Purchase History — auto-detected aliases:**

| Field | Recognized as |
|-------|--------------|
| Description | `description`, `product name`, `item name`, `item description`, `product description` |
| Qty/Year | `qty`, `quantity`, `annual qty`, `qty ordered`, `units ordered` |
| Unit Price | `price`, `unit price`, `your price`, `net price`, `cost`, `contract price` |
| Supplier SKU | `item number`, `item#`, `supplier sku`, `order item` |
| Manufacturer SKU | `mfr sku`, `mfr#`, `manufacturer item`, `catalog#` |

**Real supplier formats known to work:**
- Benco Dental order history export
- Patterson Dental purchase report
- Henry Schein order history
- Generic CSV/Excel with any of the above headers
        """)
