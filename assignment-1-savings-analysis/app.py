"""
Source Club — Savings Analysis POC
Handles real-world supplier exports: CSV or Excel, any column names.
Run: streamlit run app.py
"""

import os
import io
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from matcher import ProductMatcher
from report_generator import generate_full_report, generate_summary

load_dotenv()

# ── Column aliases — maps common supplier export headers → internal names ────
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
    missing_required = [k for k, v in auto.items() if v is None
                        and k in ("description", "unit_price", "quantity_per_year",
                                  "source_club_price", "catalog_id")]
    mapping = dict(auto)
    with st.expander(
        f"{'⚠️' if missing_required else '✅'} Column mapping — {label}",
        expanded=bool(missing_required)
    ):
        if missing_required:
            st.warning(f"Could not auto-detect: **{', '.join(missing_required)}** — map them below.")
        else:
            st.success("All required columns auto-detected. Expand to override if needed.")
        cols_ui = st.columns(3)
        for i, (internal, candidates) in enumerate(aliases.items()):
            current = auto.get(internal)
            idx = all_cols.index(current) if current in all_cols else 0
            sel = cols_ui[i % 3].selectbox(
                internal.replace("_", " ").title(), all_cols, index=idx,
                key=f"{key_prefix}_{internal}"
            )
            mapping[internal] = None if sel == "(skip / not in file)" else sel
    return mapping


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Source Club — Savings Analyzer", page_icon="🦷", layout="wide")
st.title("🦷 Source Club — Savings Analyzer")
st.caption("Upload a prospect's purchase history and the Source Club catalog to calculate potential savings.")

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

# ── File upload ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Prospect Purchase History")
    st.caption("CSV or Excel — Benco, Patterson, Schein, any format")
    prospect_file = st.file_uploader("Upload", type=["csv", "xlsx", "xls"], key="prospect")
    if st.button("Load sample →", key="lp"):
        with open("sample_data/prospect_purchase_history.csv", "rb") as f:
            prospect_file = io.BytesIO(f.read())
            prospect_file.name = "prospect_purchase_history.csv"

with col2:
    st.subheader("📋 Source Club Catalog")
    st.caption("CSV or Excel — your negotiated pricing")
    catalog_file = st.file_uploader("Upload", type=["csv", "xlsx", "xls"], key="catalog")
    if st.button("Load sample →", key="lc"):
        with open("sample_data/source_club_catalog.csv", "rb") as f:
            catalog_file = io.BytesIO(f.read())
            catalog_file.name = "source_club_catalog.csv"

if prospect_file and catalog_file:
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
    if st.button("▶️ Run Savings Analysis", type="primary", use_container_width=True):
        with st.spinner("Matching…"):
            matcher = ProductMatcher(catalog_mapped, use_claude=use_ai)
            results, claude_batch = [], []

            for i, row in prospect_mapped.iterrows():
                match, score, method = matcher.match_exact_sku(row.get("supplier_sku"), row.get("manufacturer_sku"))
                if match is None:
                    match, score, method = matcher.match_fuzzy(str(row.get("description", "")), threshold=fuzzy_threshold)

                if match is not None:
                    sc = float(match.get("source_club_price", 0) or 0)
                    pp = float(row.get("unit_price", 0) or 0)
                    qty = float(row.get("quantity_per_year", 1) or 1)
                    results.append({
                        "row_index": i, "prospect_description": row.get("description", ""),
                        "matched_catalog_id": match.get("catalog_id", ""),
                        "matched_description": match.get("description", ""),
                        "match_method": method, "match_score": score,
                        "confidence_tier": matcher.confidence_tier(score),
                        "prospect_price": pp, "source_club_price": sc,
                        "quantity_per_year": qty, "line_savings": round(max(0.0, (pp - sc) * qty), 2),
                    })
                else:
                    if use_ai and matcher.use_claude:
                        from rapidfuzz import process as rfp, fuzz as rff
                        cands = rfp.extract(str(row.get("description", "")),
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
                        results.append({
                            "row_index": i, "prospect_description": row.get("description", ""),
                            "matched_catalog_id": "", "matched_description": "",
                            "match_method": "none", "match_score": 0, "confidence_tier": "LOW",
                            "prospect_price": float(row.get("unit_price", 0) or 0),
                            "source_club_price": 0.0, "quantity_per_year": float(row.get("quantity_per_year", 1) or 1),
                            "line_savings": 0.0,
                        })

            if claude_batch:
                ai_res = matcher.match_with_claude([{k: v for k, v in it.items() if k != "_row"} for it in claude_batch])
                ai_map = {r["row_index"]: r for r in ai_res}
                for item in claude_batch:
                    i, row, ai = item["row_index"], item["_row"], ai_map.get(item["row_index"])
                    if ai and ai.get("catalog_id") and ai["catalog_id"] != "null":
                        cm = catalog_mapped[catalog_mapped["catalog_id"] == ai["catalog_id"]]
                        if not cm.empty:
                            m = cm.iloc[0]
                            sc = float(m.get("source_club_price", 0) or 0)
                            pp = float(row.get("unit_price", 0) or 0)
                            qty = float(row.get("quantity_per_year", 1) or 1)
                            results.append({
                                "row_index": i, "prospect_description": row.get("description", ""),
                                "matched_catalog_id": ai["catalog_id"], "matched_description": m.get("description", ""),
                                "match_method": "ai", "match_score": int(ai.get("confidence", 70)),
                                "confidence_tier": matcher.confidence_tier(int(ai.get("confidence", 70))),
                                "prospect_price": pp, "source_club_price": sc, "quantity_per_year": qty,
                                "line_savings": round(max(0.0, (pp - sc) * qty), 2),
                            })
                            continue
                    results.append({
                        "row_index": i, "prospect_description": row.get("description", ""),
                        "matched_catalog_id": "", "matched_description": "", "match_method": "none",
                        "match_score": 0, "confidence_tier": "LOW",
                        "prospect_price": float(row.get("unit_price", 0) or 0),
                        "source_club_price": 0.0, "quantity_per_year": float(row.get("quantity_per_year", 1) or 1),
                        "line_savings": 0.0,
                    })

        st.session_state["res"] = pd.DataFrame(results).sort_values("row_index").reset_index(drop=True)

    if "res" in st.session_state:
        results_df = st.session_state["res"]
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
            return {"HIGH": "background-color:#d4edda","MEDIUM":"background-color:#fff3cd","LOW":"background-color:#f8d7da"}.get(val,"")

        tab1, tab2, tab3 = st.tabs(["All Results", "Needs Review", "Unmatched"])
        dcols = {"prospect_description":"Item","matched_description":"Matched","match_method":"Method",
                 "confidence_tier":"Confidence","prospect_price":"Their $","source_club_price":"SC $",
                 "quantity_per_year":"Qty/Yr","line_savings":"Savings $"}

        with tab1:
            st.dataframe(results_df[list(dcols)].rename(columns=dcols).style.applymap(ct,subset=["Confidence"]),
                         use_container_width=True, height=420)
        with tab2:
            rev = results_df[results_df["confidence_tier"].isin(["MEDIUM","LOW"])]
            if rev.empty: st.success("All HIGH confidence!")
            else: st.dataframe(rev[list(dcols)].rename(columns=dcols).style.applymap(ct,subset=["Confidence"]), use_container_width=True)
        with tab3:
            unm = results_df[results_df["matched_catalog_id"]==""]
            if unm.empty: st.success("All matched!")
            else: st.dataframe(unm[["prospect_description","prospect_price","quantity_per_year"]], use_container_width=True)

        st.divider()
        buf = io.StringIO()
        results_df.to_csv(buf, index=False)
        st.download_button("⬇️ Download Report (CSV)", buf.getvalue(), "savings_report.csv", "text/csv", use_container_width=True)

else:
    st.info("👆 Upload both files (CSV or Excel) — or click **Load sample** for a live demo.")
