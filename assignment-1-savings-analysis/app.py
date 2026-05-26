"""
Source Club — Savings Analysis POC (standalone).
Handles real-world supplier exports: CSV or Excel, any column names.
Run: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

from savings_ui import render_savings_app

load_dotenv()

HERE = os.path.dirname(__file__)
SAMPLE_PROSPECT = os.path.join(HERE, "sample_data", "prospect_purchase_history.csv")
SAMPLE_CATALOG = os.path.join(HERE, "sample_data", "source_club_catalog.csv")

st.set_page_config(page_title="Source Club — Savings Analyzer", page_icon="🦷", layout="wide")

render_savings_app(
    SAMPLE_PROSPECT,
    SAMPLE_CATALOG,
    title="🦷 Source Club — Savings Analyzer",
    caption="Upload a prospect's purchase history and the Source Club catalog to calculate potential savings.",
)
