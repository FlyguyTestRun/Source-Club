"""
90-Day Architecture Scope — platform decision + full system design
"""
import os
import streamlit as st

st.set_page_config(page_title="Architecture Scope", page_icon="🏗️", layout="wide")

with st.sidebar:
    st.page_link("app.py", label="← Back to Home")

st.title("🏗️ 90-Day Architecture Scope")
st.caption("Platform decision + full system design for Weeks 1–12")
st.divider()

st.info(
    "**Assumption check:** the brief confirms only Stripe + HubSpot. The platform pick below is "
    "*conditional* on Source Club being on Google Workspace (assumed, not confirmed). What I'd "
    "verify first is in `docs/questions-i-would-ask-first.md`."
)

# ── Platform decision callout ─────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("#### AWS Bedrock")
        st.markdown("Amazon's managed AI API — Claude, Llama, Mistral, 40+ models via one endpoint")
        st.markdown("**Credits:** Up to $100K")
        st.markdown("**Workspace:** No Google integration")
        st.error("Not recommended for Source Club")

with col2:
    with st.container(border=True):
        st.markdown("#### Azure AI Foundry")
        st.markdown("Microsoft's AI platform — GPT-4o, Claude, tightly woven into Microsoft 365")
        st.markdown("**Credits:** Up to $150K")
        st.markdown("**Workspace:** Best if on Microsoft 365")
        st.warning("Only if migrating away from Google")

with col3:
    with st.container(border=True):
        st.markdown("#### ✅ Google Vertex AI")
        st.markdown("Google's AI platform — Gemini, Claude via Model Garden, native Google Workspace")
        st.markdown("**Credits: Up to $350K** (AI Track)")
        st.markdown("**Workspace:** Assumed (would confirm Day 1)")
        st.success("Recommended *if* on Google Workspace")

st.divider()

# ── Render the full doc ───────────────────────────────────────────────────────
doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "90-day-architecture-scope.md")
with open(doc_path, "r") as f:
    content = f.read()

# Strip the H1 (already shown as page title) and first few lines
lines = content.split("\n")
# Find the "Platform Decision" section and start from there
start = next((i for i, l in enumerate(lines) if l.startswith("## Platform Decision")), 2)
body = "\n".join(lines[start:])
st.markdown(body)
