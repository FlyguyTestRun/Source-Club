"""
Assignment 4 — Video Walkthrough
"""
import streamlit as st

st.set_page_config(page_title="Video Walkthrough", page_icon="🎥", layout="wide")

with st.sidebar:
    st.page_link("app.py", label="← Back to Home")

st.title("🎥 Assignment 4 — Video Walkthrough")
st.caption("3–5 minute Loom walkthrough covering all three assignments")
st.divider()

LOOM_URL = "https://loom.com/share/PLACEHOLDER"  # ← replace with your Loom URL

if "PLACEHOLDER" in LOOM_URL:
    st.warning("🎬 Video coming soon — Loom link will be added here after recording.")
else:
    st.video(LOOM_URL)

st.divider()
st.markdown("""
### What's Covered

**Part 1 — Savings Analysis Demo (~2 min)**
- Launch the Streamlit app live (you're looking at it now)
- Load sample data with one click
- Walk through the match results: HIGH / MEDIUM / LOW confidence items
- Show the review queue
- Show the annual savings figure and download the CSV
- Explain the three-pass pipeline

**Part 2 — Stripe × HubSpot Architecture (~1 min)**
- Walk through the three options
- Explain why n8n is the recommendation: free, self-hosted, visual, no per-operation cost
- Cover the multi-location data model

**Part 3 — Project Prioritization (~1 min)**
- Core argument: savings analysis automation removes the hard cap on acquisition velocity
- Sequencing logic: integrations before portal, portal before referrals
- Meta point: top priorities remove the founder from the critical path on repeatable processes
""")
