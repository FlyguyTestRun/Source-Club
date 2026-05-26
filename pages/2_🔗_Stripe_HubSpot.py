"""
Assignment 2 — Stripe × HubSpot Integration Architecture
"""
import os
import streamlit as st

st.set_page_config(page_title="Stripe × HubSpot", page_icon="🔗", layout="wide")

with st.sidebar:
    st.page_link("app.py", label="← Back to Home")

st.title("🔗 Assignment 2 — Stripe × HubSpot Integration")
st.caption("Systems architecture: 3 options analyzed, 1 recommended")
st.divider()

readme_path = os.path.join(os.path.dirname(__file__), "..", "assignment-2-stripe-hubspot", "README.md")
with open(readme_path, "r") as f:
    content = f.read()

# Strip the H1 (already in page title) and render
lines = content.split("\n")
body = "\n".join(lines[2:]) if lines[0].startswith("#") else content
st.markdown(body)
