# Reviewer Guide — Source Club Case Study

Everything here runs locally in a couple of minutes. No accounts, no API key required for the demo.

---

## 60-second overview

This is a response to the **Head of AI Powered Operations, Systems & RevOps** case study. There are
four deliverables plus a bonus, all reachable from one Streamlit app:

| # | Deliverable | What it is |
|---|-------------|-----------|
| 1 | **Savings Analysis Automation** | **Live, working tool.** Upload a prospect's purchase history + the catalog → instant savings report with confidence tiers and a human-review queue. |
| 2 | Stripe × HubSpot Integration | Architecture decision doc — three options, recommendation (n8n), HubSpot schema, multi-location data model. |
| 3 | Project Prioritization | Ranked projects + 90-day sprint plan with rationale. |
| 4 | Video Walkthrough | Loom walkthrough (link in the page). |
| Bonus | 90-Day Architecture Scope | Platform decision (Vertex AI), end-state system diagram, phased plan, cost model. |

Assignment 1 is the one to actually *run*. The rest are documents you read inside the app (or in
each `assignment-*/README.md`).

---

## Run it (Windows / macOS / Linux)

```bash
# from the repo root
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**. You'll see the landing page; use the **sidebar** to move between the
five pages.

> No API key needed. The savings tool runs in fuzzy-matching mode out of the box. To enable the
> optional Claude AI matching pass, copy `assignment-1-savings-analysis/.env.example` to `.env`,
> set `ANTHROPIC_API_KEY=...`, restart, and flip the **"Use Claude AI"** toggle in the sidebar.

---

## The 2-minute demo (Assignment 1)

1. In the sidebar, open **💰 Savings Analysis**.
2. Click **Load sample →** under *both* the Prospect file and the Source Club Catalog.
3. Click **▶️ Run Savings Analysis**.
4. You should see:
   - **💰 Annual Savings ≈ $4,944**, **Match Rate 78.6%**, **19 HIGH**, **9 Review**, **6 Unmatched**
   - **All Results** tab — every line item, color-coded by confidence, with per-unit prices
   - **Needs Review** tab — the MEDIUM/LOW matches a human should confirm
   - **Unmatched** tab — items Source Club doesn't carry (intentional in the sample)
5. Click **⬇️ Download Report (CSV)** to get the full output.

**What to notice:**
- The matcher runs three passes — exact SKU → fuzzy description → (optional) Claude AI — so cheap
  matches happen instantly and only genuinely ambiguous items cost an API call.
- Prices are compared on a **per-unit basis** when pack sizes and units line up (so "100/box @ $18"
  vs "50/box @ $10" is correct), and fall back safely when units differ (e.g. grams vs pounds).
- Column headers from Benco / Patterson / Henry Schein exports are auto-detected; unknown headers
  drop into a manual mapping UI.

You can also try **your own files** — drop any supplier CSV/Excel into the uploaders instead of the
samples.

---

## If you only have 5 minutes

1. Run the demo above (Assignment 1) — that's the working artifact.
2. Skim **🏗️ Architecture Scope** (bonus) — it shows the end-state system and why Vertex AI / ZenOne /
   Base86 / n8n, grounded in Source Club's confirmed stack.
3. Skim **📋 Prioritization** — the sequencing argument (automation + integration first, portal/
   referrals later) is the core operating thesis.

---

## Running the savings tool on its own

The analyzer is self-contained and also runs without the multi-page shell:

```bash
cd assignment-1-savings-analysis
streamlit run app.py
```

Both entry points call the same code (`savings_ui.py`), so behavior is identical.

---

## Notes for reviewers

- **Sample numbers are deterministic** in fuzzy-only mode: $4,944 / 78.6% every run. Enabling Claude
  AI will resolve some of the currently-unmatched/ambiguous rows, raising the match rate.
- **Assignment 2** is a decision doc, not running code, by design — the recommendation (n8n) is about
  what to *operate*, and the doc is enough to act on.
- **Assignment 4**'s Loom link lives in `pages/4_🎥_Video_Walkthrough.py` (`LOOM_URL`).
- Deploy artifacts (`Dockerfile`, `.github/workflows/`, `deploy/`) are the Phase-2 "how it ships"
  story — not needed to evaluate the case study.
