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
This app contains all four assignments for the Source Club case study, plus a bonus
**90-Day Architecture Scope** document covering platform selection and system design.
Navigate using the sidebar — or click any card below.
""")

# ── Assignment cards ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 💰 Assignment 1")
        st.markdown("**Savings Analysis Automation**")
        st.markdown(
            "Upload a prospect's purchase history → instant savings report. "
            "Three-pass matching: exact SKU → fuzzy → Gemini/Claude AI."
        )
        st.markdown("🟢 **Working demo — try it now**")
        st.page_link("pages/1_💰_Savings_Analysis.py", label="Open Savings Analyzer →")

    with st.container(border=True):
        st.markdown("### 🔗 Assignment 2")
        st.markdown("**Stripe × HubSpot Integration**")
        st.markdown(
            "Three options analyzed. Recommendation: n8n (free, self-hosted). "
            "Multi-location data model + HubSpot property schema."
        )
        st.page_link("pages/2_🔗_Stripe_HubSpot.py", label="View Architecture →")

with col2:
    with st.container(border=True):
        st.markdown("### 📋 Assignment 3")
        st.markdown("**Project Prioritization**")
        st.markdown(
            "Ranked 5 projects: Revenue Impact × Operational Leverage × Sequencing. "
            "90-day sprint plan with rationale."
        )
        st.page_link("pages/3_📋_Prioritization.py", label="View Prioritization →")

    with st.container(border=True):
        st.markdown("### 🎥 Assignment 4")
        st.markdown("**Video Walkthrough**")
        st.markdown(
            "3–5 minute Loom walkthrough covering all three assignments. "
            "Live demo of the savings analyzer."
        )
        st.page_link("pages/4_🎥_Video_Walkthrough.py", label="View Video →")

st.divider()

# ── Bonus: Architecture scope card ───────────────────────────────────────────
with st.container(border=True):
    st.markdown("### 🏗️ Bonus: 90-Day Architecture Scope")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(
            "Full platform decision (AWS Bedrock vs Azure AI Foundry vs **Google Vertex AI**), "
            "end-state system architecture diagram, phased build plan, tech stack, cost model, "
            "and Day 1 checklist. Informed by Source Club's confirmed use of Google Workspace, "
            "ZenOne, Base86, and their existing Stripe + HubSpot stack."
        )
        st.page_link("pages/5_🏗️_Architecture_Scope.py", label="View Architecture Scope →")
    with col_b:
        st.metric("GCP AI Track Credits", "$350K", "vs $150K Azure / $100K AWS")

st.divider()

# ── Approach note ────────────────────────────────────────────────────────────
with st.expander("📝 Approach & Assumptions"):
    st.markdown("""
**On the existing stack:** Source Club uses **Base86** (AI product matching) and **ZenOne**
(procurement, 200K+ normalized SKUs) — confirmed from their SOP documentation.
The savings analysis POC replicates Base86's core matching logic with open-source tools for this
demo; the production version integrates directly with ZenOne and Base86.

**On the AI platform:** Google Vertex AI is recommended. Source Club uses Google Docs (confirmed).
Vertex AI agents connect natively to Google Workspace — no custom connectors needed. GCP's
AI Track startup program provides up to $350K in credits vs $150K Azure / $100K AWS.

**On the production vision:** The full automation is a 5-agent Vertex AI pipeline:
intake form → Base86/ZenOne catalog lookup → savings calculation →
Google Doc report generation → HubSpot CRM sync. No founder involvement required.

**Assumptions:**
- Prospect purchase history = CSV/Excel export from dental supplier (Benco, Patterson, Schein)
- Source Club's catalog lives in ZenOne; static CSV used here as a stand-in for the POC
- The Stripe + HubSpot naming mismatch is solved with a one-time reconciliation script
- Project priorities would be refined with 30 min of conversation about ARR, churn rate, and team bandwidth
    """)
