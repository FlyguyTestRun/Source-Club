"""
Source Club Case Study — Landing Page
"""
import streamlit as st

st.set_page_config(
    page_title="Source Club — Case Study",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🦷 Source Club — Case Study Submission")
st.caption("Head of AI Powered Operations, Systems & RevOps")
st.divider()

# ── Intro ────────────────────────────────────────────────────────────────────
st.markdown("""
This app contains all four assignments for the Source Club case study.
Navigate using the sidebar — or click any card below to jump to an assignment.
""")

# ── Assignment cards ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 💰 Assignment 1")
        st.markdown("**Savings Analysis Automation**")
        st.markdown(
            "Upload a prospect's purchase history → get an instant savings report. "
            "Three-pass matching: exact SKU → fuzzy → Claude AI."
        )
        st.markdown("🟢 Working demo — try it now")
        st.page_link("pages/1_💰_Savings_Analysis.py", label="Open Savings Analyzer →")

    with st.container(border=True):
        st.markdown("### 🔗 Assignment 2")
        st.markdown("**Stripe × HubSpot Integration**")
        st.markdown(
            "Three integration options analyzed. Recommendation: n8n (free, self-hosted). "
            "Includes multi-location data model + HubSpot property schema."
        )
        st.page_link("pages/2_🔗_Stripe_HubSpot.py", label="View Architecture →")

with col2:
    with st.container(border=True):
        st.markdown("### 📋 Assignment 3")
        st.markdown("**Project Prioritization**")
        st.markdown(
            "Ranked 5 projects using a Revenue Impact × Operational Leverage × Sequencing "
            "framework. Includes a 90-day sprint plan."
        )
        st.page_link("pages/3_📋_Prioritization.py", label="View Prioritization →")

    with st.container(border=True):
        st.markdown("### 🎥 Assignment 4")
        st.markdown("**Video Walkthrough**")
        st.markdown(
            "3–5 minute Loom walkthrough covering all three assignments. "
            "Screen-share of the live app + architecture decisions."
        )
        st.page_link("pages/4_🎥_Video_Walkthrough.py", label="View Video →")

st.divider()

# ── Approach note ────────────────────────────────────────────────────────────
with st.expander("📝 Approach & Assumptions"):
    st.markdown("""
**On the stack:** Everything here is free and open-source — pandas, RapidFuzz, Streamlit, n8n.
Tools a small team can actually run and maintain, not enterprise overhead.

**On the production vision:** The right long-term architecture for product matching at scale
is a **knowledge graph with Graph RAG** — dental supply items as nodes, semantic edges across
supplier naming conventions, continuous learning from confirmed matches.
That's a multi-week build. This POC demonstrates the concept and gets the job done today.

**Assumptions made:**
- Prospect purchase history arrives as CSV (most common export from dental practice management software)
- Source Club's catalog is relatively stable — a static CSV or periodic refresh works for the POC
- Annual quantity in the prospect file = actual purchasing frequency, not a one-time order
- The Stripe + HubSpot naming mismatch is solved with a one-time reconciliation script + indexed
  `stripe_customer_id` property going forward
- Project prioritization is based on context in the case study brief; rankings would be refined
  with 30 minutes of conversation about current ARR, churn rate, and team bandwidth
    """)
