# Source Club — Case Study Project

## What This Is
A complete case study submission for the **Head of AI Powered Operations, Systems & RevOps** role at Source Club — a dental Group Purchasing Organization (GPO). Built as a working Streamlit multi-page web app.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501
```

## Project Structure
```
Source-Club/
├── app.py                              ← Main landing page (run this)
├── pages/
│   ├── 1_💰_Savings_Analysis.py       ← Live working savings analysis tool
│   ├── 2_🔗_Stripe_HubSpot.py        ← Stripe/HubSpot architecture doc
│   ├── 3_📋_Prioritization.py         ← Project prioritization framework
│   ├── 4_🎥_Video_Walkthrough.py      ← Video placeholder (add Loom URL here)
│   └── 5_🏗️_Architecture_Scope.py    ← 90-day architecture scope
├── assignment-1-savings-analysis/
│   ├── app.py                          ← Standalone savings app (also works solo)
│   ├── matcher.py                      ← 3-pass matching logic (SKU → fuzzy → AI)
│   ├── report_generator.py             ← CSV + summary output
│   ├── requirements.txt                ← Python deps for standalone run
│   ├── .env.example                    ← Copy to .env, add ANTHROPIC_API_KEY
│   └── sample_data/                    ← 28-row dental supply test data
├── assignment-2-stripe-hubspot/README.md
├── assignment-3-prioritization/README.md
├── assignment-4-video/README.md
├── docs/
│   └── 90-day-architecture-scope.md   ← Full platform + architecture document
├── Dockerfile                          ← Container (for future Azure deploy)
├── .github/workflows/deploy-azure.yml ← CI/CD to Azure Container Apps
└── deploy/azure-setup.md              ← Azure CLI setup commands
```

## Key Architecture Decisions
- **AI Platform:** Google Vertex AI (GCP) — Source Club uses Google Workspace; GCP gives $350K startup credits
- **Matching pipeline:** 3-pass: exact SKU → RapidFuzz fuzzy → Claude/Gemini AI
- **CRM/Billing sync:** n8n (self-hosted, free) — Stripe webhooks → HubSpot properties
- **Existing tools:** ZenOne (pricing catalog), Base86 (AI product matching)
- **File support:** CSV + Excel (.xlsx), auto-detects Benco/Patterson/Schein column headers

## Source Club's Tech Stack (confirmed)
| Tool | Role |
|------|------|
| Stripe | Billing / subscriptions |
| HubSpot | CRM |
| ZenOne | Procurement platform — 200K+ normalized dental SKUs |
| Base86 | AI-driven product matching |
| Google Workspace | Docs, Drive, Gmail (confirmed from SOP screenshot) |
| PandaDoc | Contracts / proposals |
| n8n | Proposed: Stripe ↔ HubSpot workflow automation |

## Assignment 1 — Savings Analysis (the live tool)
The core POC. Upload a prospect's dental supply purchase history (CSV or Excel) + the Source Club catalog → instant savings report with confidence tiers.

**Matching pipeline:**
1. Exact SKU lookup (dict, instant)
2. Fuzzy description match (RapidFuzz token_sort_ratio, threshold 72)
3. Claude AI semantic match (batched, optional — needs `ANTHROPIC_API_KEY`)

**Column auto-detection** handles real Benco/Patterson/Schein export headers automatically. Falls back to a manual mapping UI if headers aren't recognized.

**To demo without API key:** Load sample data → Run → works in fuzzy-only mode (~78% match rate on sample data).

## Assignment 4 — Video (one thing left to do)
Add your Loom URL to `pages/4_🎥_Video_Walkthrough.py`:
```python
LOOM_URL = "https://loom.com/share/YOUR_ACTUAL_ID_HERE"  # ← change this line
```

## Future: Azure Deploy (Phase 2)
Everything needed is already built:
1. `Dockerfile` — containerized Streamlit app
2. `.github/workflows/deploy-azure.yml` — GitHub Actions CI/CD
3. `deploy/azure-setup.md` — step-by-step `az` CLI commands

When ready: run the `az` commands in `deploy/azure-setup.md`, add 4 GitHub secrets, push to main → auto-deploys to Azure Container Apps.

## Environment Variables
```
ANTHROPIC_API_KEY=your_key_here   # Optional — enables AI matching pass
```

Copy `.env.example` → `.env` and fill in. App works without it.
