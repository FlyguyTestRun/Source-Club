# Source Club — Case Study Project

## What This Is
A case-study submission for the **Head of AI Powered Operations, Systems & RevOps** role at
Source Club — a dental Group Purchasing Organization (GPO). It is delivered as a working Streamlit
multi-page web app plus supporting decision documents.

**One deliverable is live code, three are documents:**

| # | Deliverable | Type | Where |
|---|-------------|------|-------|
| 1 | Savings Analysis Automation | **Working app** | `assignment-1-savings-analysis/` + `pages/1_*` |
| 2 | Stripe × HubSpot Integration | Decision doc | `assignment-2-stripe-hubspot/README.md` + `pages/2_*` |
| 3 | Project Prioritization | Decision doc | `assignment-3-prioritization/README.md` + `pages/3_*` |
| 4 | Video Walkthrough | Loom placeholder | `assignment-4-video/README.md` + `pages/4_*` |
| Bonus | 90-Day Architecture Scope | Strategy doc | `docs/90-day-architecture-scope.md` + `pages/5_*` |

For a reviewer-facing "how to run and what to look at" walkthrough, see `INTERVIEWER_GUIDE.md`.

> **Source of truth:** `docs/CASE-STUDY-BRIEF.md` holds the verbatim case-study brief + resources +
> the real project queue. It is authoritative — when anything here disagrees with it, the brief wins.
> Key reminders from it: the brief is **tool-agnostic** (Streamlit is our choice, not required; a
> hosted URL is optional — "links or files" suffices); only **Stripe + HubSpot** are confirmed
> (everything else is an assumption); savings analysis is **~10 min/analysis, 5–7+ hrs/month**.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501 — landing page with all 5 pages in the sidebar
```
The savings analyzer also runs standalone:
```bash
cd assignment-1-savings-analysis
streamlit run app.py   # http://localhost:8501
```
Both entry points share one implementation (`savings_ui.py`) — there is no duplicated logic.

## Project Structure
```
Source-Club/
├── app.py                              ← Landing page (run this)
├── INTERVIEWER_GUIDE.md                ← Cold-start run + review guide
├── pages/                              ← Multipage tabs (1 is live, 2–5 render docs)
│   ├── 1_💰_Savings_Analysis.py        ← Thin wrapper → savings_ui.render_savings_app()
│   ├── 2_🔗_Stripe_HubSpot.py
│   ├── 3_📋_Prioritization.py
│   ├── 4_🎥_Video_Walkthrough.py       ← add Loom URL here
│   └── 5_🏗️_Architecture_Scope.py
├── assignment-1-savings-analysis/
│   ├── savings_ui.py                    ← Shared UI + run loop + savings math (source of truth)
│   ├── app.py                           ← Standalone entry (thin wrapper)
│   ├── matcher.py                       ← 3-pass matching (SKU → fuzzy → Claude AI)
│   ├── report_generator.py              ← Summary + CSV output
│   ├── sample_data/                     ← 28-row prospect file + 28-item catalog
│   └── .env.example                     ← Copy to .env, add ANTHROPIC_API_KEY (optional)
├── assignment-2-stripe-hubspot/README.md
├── assignment-3-prioritization/README.md
├── assignment-4-video/README.md
├── docs/90-day-architecture-scope.md
├── Dockerfile / .github/ / deploy/      ← Phase-2 Azure deploy (not needed to review)
└── requirements.txt
```

## Assignment 1 — Savings Analysis (the live tool)
Upload a prospect's dental-supply purchase history (CSV or Excel) + the Source Club catalog →
instant savings report with confidence tiers.

**Matching pipeline (in `matcher.py`):**
1. **Exact SKU** — normalized dict lookup on supplier/manufacturer SKU (instant).
2. **Fuzzy description** — RapidFuzz `token_sort_ratio`, threshold 72 (adjustable in the sidebar).
3. **Claude AI** — batched semantic match for ambiguous items; needs `ANTHROPIC_API_KEY`,
   model `claude-haiku-4-5-20251001`. Optional — skipped if no key.

**Confidence tiers:** 🟢 HIGH ≥ 90 · 🟡 MEDIUM ≥ 70 · 🔴 LOW < 70. MEDIUM/LOW land in a review queue.

**Savings math (`compute_line_savings` in `savings_ui.py`):** prices are normalized to a
**per-single-item** basis when both pack sizes are present and the units of measure match — so
"100/box @ $18" vs "50/box @ $10" compares correctly. When pack size is missing or units differ
(e.g. grams vs pounds), it falls back to a direct pack-price comparison. Each result row records
which basis was used (`savings_basis`).

**Column auto-detection** handles real Benco/Patterson/Schein export headers; falls back to a manual
mapping UI when a header isn't recognized.

**Demo without an API key:** click **Load sample** on both uploaders → **Run** → works in
fuzzy-only mode. Sample data yields **~$4,944 savings at a 78.6% match rate** (19 HIGH, 3 MEDIUM,
6 unmatched).

## Key Architecture Decisions (production vision — see `docs/`)
These are **hypotheses built on assumptions**, not settled facts. See
`docs/questions-i-would-ask-first.md` for what I'd confirm before committing.
- **AI platform:** Google Vertex AI — *conditional on Source Club being on Google Workspace*
  (assumed, not confirmed in the brief). If they're not on Google, this flips to Azure/neutral.
- **AI matching pass:** intentionally optional and OFF by default in the POC — the vendor choice
  (Gemini vs. Claude) depends on the platform + accuracy + volume answers, so it's deferred.
- **Matching at scale:** integrate ZenOne (catalog) + Base86 (AI matching) *if those are in fact
  their tools* — assumed, would verify — rather than the static sample CSV used here.
- **CRM/billing sync:** n8n (self-hosted) — Stripe webhooks → HubSpot Company properties.

## Source Club's Tech Stack
| Tool | Role | Status |
|------|------|--------|
| Stripe | Billing / subscriptions | **Confirmed in brief** |
| HubSpot | CRM | **Confirmed in brief** |
| ZenOne | Procurement — assumed catalog source of truth | Assumed — verify |
| Base86 | AI-driven product matching | Assumed — verify |
| Google Workspace | Docs, Drive, Gmail | Assumed — verify |
| PandaDoc | Contracts / proposals | Assumed — verify |
| n8n | Proposed: Stripe ↔ HubSpot automation | My proposal |

## Known Limitations / Next Steps
- Pack-size unit normalization: **done** (per-unit comparison with safe fallback).
- Static CSV catalog → replace with live ZenOne API; pull Base86 normalized data as match input.
- No match cache yet — confirmed matches should be persisted so Claude calls trend toward zero.
- Cross-unit conversion (grams ↔ pounds) is intentionally *not* attempted; those rows fall back to
  pack-price comparison rather than guess a conversion.

## Assignment 4 — Video (one thing left to do)
Add the Loom URL in `pages/4_🎥_Video_Walkthrough.py`:
```python
LOOM_URL = "https://loom.com/share/YOUR_ACTUAL_ID_HERE"
```

## Environment Variables
```
ANTHROPIC_API_KEY=your_key_here   # Optional — enables the Claude AI matching pass
```
Copy `.env.example` → `.env` and fill in. The app works without it (fuzzy-only).

## Future: Azure Deploy (Phase 2)
`Dockerfile`, `.github/workflows/deploy-azure.yml`, and `deploy/azure-setup.md` contain a complete
containerized deploy to Azure Container Apps. Not required to review the case study — it's the
"how this ships" artifact.
