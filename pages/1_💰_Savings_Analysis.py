"""
Assignment 1 — Savings Analysis Automation (multipage entry).
Thin wrapper around the shared savings UI in assignment-1-savings-analysis/savings_ui.py.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

A1 = os.path.join(os.path.dirname(__file__), "..", "assignment-1-savings-analysis")
sys.path.insert(0, A1)

from savings_ui import render_savings_app  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
load_dotenv(os.path.join(A1, ".env"), override=False)

SAMPLE_PROSPECT = os.path.join(A1, "sample_data", "prospect_purchase_history.csv")
SAMPLE_CATALOG = os.path.join(A1, "sample_data", "source_club_catalog.csv")

st.set_page_config(page_title="Savings Analysis", page_icon="💰", layout="wide")

render_savings_app(
    SAMPLE_PROSPECT,
    SAMPLE_CATALOG,
    title="💰 Assignment 1 — Savings Analysis Automation",
    caption="Upload a prospect's purchase history + the Source Club catalog → instant savings report.",
    show_back_link=True,
)
