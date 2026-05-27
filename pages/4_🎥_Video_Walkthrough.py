"""
Assignment 4 — Video Walkthrough
"""
import os
import streamlit as st

st.set_page_config(page_title="Video Walkthrough", page_icon="🎥", layout="wide")

with st.sidebar:
    st.page_link("app.py", label="← Back to Home")

st.title("🎥 Assignment 4 — Video Walkthrough")
st.caption("3–5 minute walkthrough covering all three assignments")
st.divider()

LOOM_URL = "https://loom.com/share/PLACEHOLDER"  # ← replace with your Loom URL
_DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "demo", "output")
NARRATED_MP4 = os.path.join(_DEMO_DIR, "source-club-demo-narrated.mp4")     # H.264/AAC, voiceover
NARRATED_WEBM = os.path.join(_DEMO_DIR, "source-club-demo-narrated.webm")   # VP8/Opus, voiceover
SILENT_DEMO = os.path.join(_DEMO_DIR, "source-club-demo.webm")             # captions only

# Auto-generated product demo — the app driving itself end to end. Prefer the
# narrated MP4 (most compatible), then narrated WebM, then the silent run.
_demo = next((f for f in (NARRATED_MP4, NARRATED_WEBM, SILENT_DEMO) if os.path.exists(f)), None)
if _demo:
    narrated = _demo in (NARRATED_MP4, NARRATED_WEBM)
    st.subheader("▶️ Auto-generated product demo" + (" (with voiceover)" if narrated else ""))
    st.caption(("Self-narrating run of the Savings Analyzer — turn sound on."
                if narrated else
                "Hands-free run of the Savings Analyzer (silent; captions on screen)."))
    st.video(_demo)
    st.divider()

st.subheader("🎙️ Narrated Loom walkthrough")
if "PLACEHOLDER" in LOOM_URL:
    st.info("Loom link will be added here after recording — set `LOOM_URL` in this file. "
            "The auto-generated demo above already shows the live tool in action.")
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
