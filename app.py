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
            "and Day 1 checklist. Built on Stripe + HubSpot (confirmed in the brief) plus stated "
            "assumptions about Google Workspace, ZenOne, and Base86 — the things I'd confirm first."
        )
        st.page_link("pages/5_🏗️_Architecture_Scope.py", label="View Architecture Scope →")
    with col_b:
        st.metric("GCP AI Track Credits", "$350K", "vs $150K Azure / $100K AWS")

st.divider()

# ── Approach note ────────────────────────────────────────────────────────────
with st.expander("📝 Approach & Assumptions"):
    st.markdown("""
**What's confirmed vs. assumed.** The brief confirms only **Stripe** and **HubSpot**. Everything
else below — Google Workspace, GCP, **ZenOne**, **Base86**, PandaDoc — is my working assumption,
flagged as such throughout. The full list of what I'd verify is in
`docs/questions-i-would-ask-first.md`.

**On the existing stack (assumed):** *if* Source Club uses **ZenOne** (procurement catalog) and
**Base86** (AI product matching), the production version integrates with them directly. The POC
replicates the core matching logic with open-source tools so it can be evaluated independently.

**On the AI platform (conditional):** Google Vertex AI is recommended *only if* Source Club is on
Google Workspace — then Vertex connects natively to Docs/Drive/Gmail and GCP's AI Track offers up to
$350K credits. If they're on Microsoft 365 or cloud-agnostic, the choice flips.

**On the AI matching pass:** intentionally optional and OFF by default in the POC — the vendor
choice (Gemini vs. Claude) depends on the platform, accuracy bar, and real volume, so I deferred it
rather than bake in a decision I'd have to unwind.

**Assumptions I made (per the brief's "make a call and state it"):**
- Prospect purchase history = CSV/Excel export from a dental supplier (Benco, Patterson, Schein)
- A catalog source of truth exists (assumed ZenOne); static CSV used here as a stand-in
- The Stripe + HubSpot naming mismatch is solved with a one-time reconciliation script
- Project priorities would be refined against the real queue + a short ARR/churn/bandwidth conversation
    """)
