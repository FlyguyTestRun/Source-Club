"""
Source Club — Savings Analysis POC
Streamlit app: upload prospect CSV + catalog CSV → instant savings report
"""

import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from matcher import ProductMatcher
from report_generator import generate_full_report, generate_summary

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Source Club — Savings Analyzer",
    page_icon="🦷",
    layout="wide",
)

st.title("🦷 Source Club — Savings Analyzer")
st.caption(
    "Upload a prospect's purchase history and the Source Club catalog to instantly calculate potential savings."
)

# ── Sidebar: settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    use_ai = st.toggle(
        "Use Claude AI for ambiguous matches",
        value=bool(os.getenv("ANTHROPIC_API_KEY")),
        help="Requires ANTHROPIC_API_KEY in .env. Falls back to fuzzy matching if disabled.",
    )
    fuzzy_threshold = st.slider("Fuzzy match threshold", 60, 95, 72)
    st.divider()
    st.markdown("**Match pipeline:**")
    st.markdown("1. Exact SKU lookup\n2. Fuzzy description match\n3. Claude AI (if enabled)")
    st.divider()
    st.markdown("**Confidence tiers:**")
    st.markdown("🟢 HIGH ≥ 90 &nbsp; 🟡 MEDIUM ≥ 70 &nbsp; 🔴 LOW < 70")

# ── File uploaders ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Prospect Purchase History")
    prospect_file = st.file_uploader(
        "Upload CSV", type=["csv"], key="prospect",
        help="Columns: supplier_sku, manufacturer_sku, description, quantity_per_year, unit_price, pack_size, unit_of_measure, annual_spend"
    )
    if st.button("Load sample data →", key="load_sample_prospect"):
        with open("sample_data/prospect_purchase_history.csv", "rb") as f:
            prospect_file = io.BytesIO(f.read())
            prospect_file.name = "prospect_purchase_history.csv"

with col2:
    st.subheader("📋 Source Club Catalog")
    catalog_file = st.file_uploader(
        "Upload CSV", type=["csv"], key="catalog",
        help="Columns: catalog_id, manufacturer_sku, supplier_sku, description, pack_size, unit_of_measure, source_club_price, category"
    )
    if st.button("Load sample catalog →", key="load_sample_catalog"):
        with open("sample_data/source_club_catalog.csv", "rb") as f:
            catalog_file = io.BytesIO(f.read())
            catalog_file.name = "source_club_catalog.csv"

# ── Run analysis ─────────────────────────────────────────────────────────────
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
            # Pass 1: exact SKU
            match, score, method = matcher.match_exact_sku(
                row.get("supplier_sku"), row.get("manufacturer_sku")
            )

            # Pass 2: fuzzy
            if match is None:
                match, score, method = matcher.match_fuzzy(
                    str(row.get("description", "")), threshold=fuzzy_threshold
                )

            if match is not None:
                sc_price = match["source_club_price"]
                prospect_price = float(row.get("unit_price", 0))
                qty = float(row.get("quantity_per_year", 1))
                line_savings = max(0.0, (prospect_price - sc_price) * qty)
                tier = matcher.confidence_tier(score)
                results.append({
                    "row_index": i,
                    "prospect_description": row.get("description", ""),
                    "matched_catalog_id": match["catalog_id"],
                    "matched_description": match["description"],
                    "match_method": method,
                    "match_score": score,
                    "confidence_tier": tier,
                    "prospect_price": prospect_price,
                    "source_club_price": sc_price,
                    "quantity_per_year": qty,
                    "line_savings": round(line_savings, 2),
                })
            else:
                # Queue for Claude or mark unresolved
                if use_ai and matcher.use_claude:
                    # Get top fuzzy candidates for context
                    from rapidfuzz import process as rfp, fuzz as rff
                    candidates_raw = rfp.extract(
                        str(row.get("description", "")),
                        [matcher.catalog.iloc[j]["description"] for j in range(len(matcher.catalog))],
                        scorer=rff.token_sort_ratio,
                        limit=3,
                    )
                    candidates = [{"description": c[0], "score": c[1]} for c in candidates_raw]
                    claude_batch.append({
                        "row_index": i,
                        "description": str(row.get("description", "")),
                        "supplier_sku": str(row.get("supplier_sku", "")),
                        "manufacturer_sku": str(row.get("manufacturer_sku", "")),
                        "candidates": candidates,
                        "_row": row,
                    })
                else:
                    results.append({
                        "row_index": i,
                        "prospect_description": row.get("description", ""),
                        "matched_catalog_id": "",
                        "matched_description": "",
                        "match_method": "none",
                        "match_score": 0,
                        "confidence_tier": "LOW",
                        "prospect_price": float(row.get("unit_price", 0)),
                        "source_club_price": 0.0,
                        "quantity_per_year": float(row.get("quantity_per_year", 1)),
                        "line_savings": 0.0,
                    })

        # Process Claude batch
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
                        match_row = cat_match.iloc[0]
                        sc_price = match_row["source_club_price"]
                        prospect_price = float(row.get("unit_price", 0))
                        qty = float(row.get("quantity_per_year", 1))
                        line_savings = max(0.0, (prospect_price - sc_price) * qty)
                        score = int(ai.get("confidence", 70))
                        results.append({
                            "row_index": i,
                            "prospect_description": row.get("description", ""),
                            "matched_catalog_id": ai["catalog_id"],
                            "matched_description": match_row["description"],
                            "match_method": "ai",
                            "match_score": score,
                            "confidence_tier": matcher.confidence_tier(score),
                            "prospect_price": prospect_price,
                            "source_club_price": sc_price,
                            "quantity_per_year": qty,
                            "line_savings": round(line_savings, 2),
                        })
                        continue

                # Fallback: unmatched
                results.append({
                    "row_index": i,
                    "prospect_description": row.get("description", ""),
                    "matched_catalog_id": "",
                    "matched_description": "",
                    "match_method": "none",
                    "match_score": 0,
                    "confidence_tier": "LOW",
                    "prospect_price": float(row.get("unit_price", 0)),
                    "source_club_price": 0.0,
                    "quantity_per_year": float(row.get("quantity_per_year", 1)),
                    "line_savings": 0.0,
                })

    results_df = pd.DataFrame(results).sort_values("row_index").reset_index(drop=True)
    summary = generate_summary(results_df)

    # ── Summary metrics ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Results Summary")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Est. Annual Savings", f"${summary['total_annual_savings']:,.0f}")
    m2.metric("✅ Match Rate", f"{summary['match_rate_pct']}%")
    m3.metric("🟢 High Confidence", summary["high_confidence"])
    m4.metric("🟡 Needs Review", summary["medium_confidence"] + summary["low_confidence"])
    m5.metric("❌ Unmatched", summary["unmatched_count"])

    # ── Results table ────────────────────────────────────────────────────────
    st.subheader("📋 Matched Items")

    def color_tier(val):
        colors = {"HIGH": "background-color: #d4edda", "MEDIUM": "background-color: #fff3cd", "LOW": "background-color: #f8d7da"}
        return colors.get(val, "")

    display_cols = [
        "prospect_description", "matched_description", "match_method",
        "confidence_tier", "prospect_price", "source_club_price",
        "quantity_per_year", "line_savings",
    ]
    display_df = results_df[display_cols].rename(columns={
        "prospect_description": "Prospect Item",
        "matched_description": "Matched Catalog Item",
        "match_method": "Method",
        "confidence_tier": "Confidence",
        "prospect_price": "Their Price",
        "source_club_price": "SC Price",
        "quantity_per_year": "Qty/Year",
        "line_savings": "Annual Savings",
    })

    styled = display_df.style.applymap(color_tier, subset=["Confidence"])
    st.dataframe(styled, use_container_width=True, height=420)

    # ── Top savings ──────────────────────────────────────────────────────────
    if summary["top_savings_items"]:
        st.subheader("🏆 Top 5 Savings Opportunities")
        top_df = pd.DataFrame(summary["top_savings_items"])
        st.dataframe(top_df, use_container_width=True)

    # ── Download ─────────────────────────────────────────────────────────────
    st.divider()
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="⬇️ Download Full Report (CSV)",
        data=csv_buffer.getvalue(),
        file_name="savings_analysis_report.csv",
        mime="text/csv",
    )

    # ── Review queue ─────────────────────────────────────────────────────────
    review_items = results_df[results_df["confidence_tier"].isin(["LOW"])]
    if not review_items.empty:
        with st.expander(f"⚠️ Review Queue ({len(review_items)} items need human review)"):
            st.dataframe(review_items[["prospect_description", "matched_description", "match_score", "match_method"]], use_container_width=True)

else:
    st.info("👆 Upload both files above — or click **Load sample data** to see a demo.")
    st.markdown("""
    **Expected columns:**

    | Prospect Purchase History | Source Club Catalog |
    |---|---|
    | `supplier_sku` | `catalog_id` |
    | `manufacturer_sku` | `manufacturer_sku` |
    | `description` | `supplier_sku` |
    | `quantity_per_year` | `description` |
    | `unit_price` | `pack_size` |
    | `pack_size` | `unit_of_measure` |
    | `unit_of_measure` | `source_club_price` |
    | `annual_spend` | `category` |
    """)
