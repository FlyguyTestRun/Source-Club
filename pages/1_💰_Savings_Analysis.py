"""
Assignment 1 — Savings Analysis Automation
"""

import sys
import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Allow imports from the assignment-1 subfolder regardless of where Streamlit runs from
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

st.set_page_config(page_title="Savings Analysis", page_icon="💰", layout="wide")

st.title("💰 Assignment 1 — Savings Analysis Automation")
st.caption(
    "Upload a prospect's purchase history + the Source Club catalog → instant savings report."
)

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

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Prospect Purchase History")
    prospect_file = st.file_uploader("Upload CSV", type=["csv"], key="prospect")
    if st.button("Load sample data →", key="load_prospect"):
        with open(SAMPLE_PROSPECT, "rb") as f:
            prospect_file = io.BytesIO(f.read())
            prospect_file.name = "prospect_purchase_history.csv"
        st.session_state["prospect_loaded"] = True

with col2:
    st.subheader("📋 Source Club Catalog")
    catalog_file = st.file_uploader("Upload CSV", type=["csv"], key="catalog")
    if st.button("Load sample catalog →", key="load_catalog"):
        with open(SAMPLE_CATALOG, "rb") as f:
            catalog_file = io.BytesIO(f.read())
            catalog_file.name = "source_club_catalog.csv"
        st.session_state["catalog_loaded"] = True

# Auto-load both samples if either button was clicked this run
if st.session_state.get("prospect_loaded") and prospect_file is None:
    with open(SAMPLE_PROSPECT, "rb") as f:
        prospect_file = io.BytesIO(f.read())
if st.session_state.get("catalog_loaded") and catalog_file is None:
    with open(SAMPLE_CATALOG, "rb") as f:
        catalog_file = io.BytesIO(f.read())

if prospect_file and catalog_file:
    try:
        prospect_df = pd.read_csv(prospect_file)
        catalog_df = pd.read_csv(catalog_file)
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")
        st.stop()

    with st.spinner("Running matching pipeline…"):
        matcher = ProductMatcher(catalog_df, use_claude=use_ai)
        results = []
        claude_batch = []

        for i, row in prospect_df.iterrows():
            match, score, method = matcher.match_exact_sku(
                row.get("supplier_sku"), row.get("manufacturer_sku")
            )
            if match is None:
                match, score, method = matcher.match_fuzzy(
                    str(row.get("description", "")), threshold=fuzzy_threshold
                )

            if match is not None:
                sc_price = match["source_club_price"]
                pp = float(row.get("unit_price", 0))
                qty = float(row.get("quantity_per_year", 1))
                line_savings = max(0.0, (pp - sc_price) * qty)
                tier = matcher.confidence_tier(score)
                results.append({
                    "row_index": i,
                    "prospect_description": row.get("description", ""),
                    "matched_catalog_id": match["catalog_id"],
                    "matched_description": match["description"],
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
                        "prospect_price": float(row.get("unit_price", 0)),
                        "source_club_price": 0.0,
                        "quantity_per_year": float(row.get("quantity_per_year", 1)),
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
                    cat_match = catalog_df[catalog_df["catalog_id"] == ai["catalog_id"]]
                    if not cat_match.empty:
                        m = cat_match.iloc[0]
                        sc_price = m["source_club_price"]
                        pp = float(row.get("unit_price", 0))
                        qty = float(row.get("quantity_per_year", 1))
                        score = int(ai.get("confidence", 70))
                        results.append({
                            "row_index": i,
                            "prospect_description": row.get("description", ""),
                            "matched_catalog_id": ai["catalog_id"],
                            "matched_description": m["description"],
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
                    "prospect_price": float(row.get("unit_price", 0)),
                    "source_club_price": 0.0,
                    "quantity_per_year": float(row.get("quantity_per_year", 1)),
                    "line_savings": 0.0,
                })

    results_df = pd.DataFrame(results).sort_values("row_index").reset_index(drop=True)
    summary = generate_summary(results_df)

    st.divider()
    st.subheader("📊 Results Summary")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Est. Annual Savings", f"${summary['total_annual_savings']:,.0f}")
    m2.metric("✅ Match Rate", f"{summary['match_rate_pct']}%")
    m3.metric("🟢 High Confidence", summary["high_confidence"])
    m4.metric("🟡 Needs Review", summary["medium_confidence"] + summary["low_confidence"])
    m5.metric("❌ Unmatched", summary["unmatched_count"])

    st.subheader("📋 Matched Items")

    def color_tier(val):
        return {
            "HIGH": "background-color: #d4edda",
            "MEDIUM": "background-color: #fff3cd",
            "LOW": "background-color: #f8d7da",
        }.get(val, "")

    display_df = results_df[[
        "prospect_description", "matched_description", "match_method",
        "confidence_tier", "prospect_price", "source_club_price",
        "quantity_per_year", "line_savings",
    ]].rename(columns={
        "prospect_description": "Prospect Item",
        "matched_description": "Matched Catalog Item",
        "match_method": "Method",
        "confidence_tier": "Confidence",
        "prospect_price": "Their Price",
        "source_club_price": "SC Price",
        "quantity_per_year": "Qty/Year",
        "line_savings": "Annual Savings",
    })

    st.dataframe(
        display_df.style.applymap(color_tier, subset=["Confidence"]),
        use_container_width=True, height=420,
    )

    if summary["top_savings_items"]:
        st.subheader("🏆 Top 5 Savings Opportunities")
        st.dataframe(pd.DataFrame(summary["top_savings_items"]), use_container_width=True)

    st.divider()
    csv_buf = io.StringIO()
    results_df.to_csv(csv_buf, index=False)
    st.download_button(
        "⬇️ Download Full Report (CSV)",
        csv_buf.getvalue(), "savings_analysis_report.csv", "text/csv",
    )

    review = results_df[results_df["confidence_tier"] == "LOW"]
    if not review.empty:
        with st.expander(f"⚠️ Review Queue ({len(review)} items need human review)"):
            st.dataframe(
                review[["prospect_description", "matched_description", "match_score", "match_method"]],
                use_container_width=True,
            )

else:
    st.info("👆 Upload both files above — or click **Load sample data** to see a live demo.")
    st.markdown("""
**Expected columns — Prospect Purchase History:**
`supplier_sku`, `manufacturer_sku`, `description`, `quantity_per_year`, `unit_price`, `pack_size`, `unit_of_measure`, `annual_spend`

**Expected columns — Source Club Catalog:**
`catalog_id`, `manufacturer_sku`, `supplier_sku`, `description`, `pack_size`, `unit_of_measure`, `source_club_price`, `category`
""")
