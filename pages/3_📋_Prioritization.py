"""
Assignment 3 — Project Prioritization
"""
import os
import streamlit as st

st.set_page_config(page_title="Prioritization", page_icon="📋", layout="wide")

with st.sidebar:
    st.page_link("app.py", label="← Back to Home")

st.title("📋 Assignment 3 — Project Prioritization")
st.caption("Framework: Revenue Impact × Operational Leverage × Sequencing Dependency")
st.divider()

readme_path = os.path.join(os.path.dirname(__file__), "..", "assignment-3-prioritization", "README.md")
with open(readme_path, "r") as f:
    content = f.read()

lines = content.split("\n")
body = "\n".join(lines[2:]) if lines[0].startswith("#") else content
st.markdown(body)
