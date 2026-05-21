# Source Club — Case Study Submission

This repository contains my responses to the Source Club case study for the **Head of AI Powered Operations, Systems & RevOps** role.

---

## Deliverables

| # | Assignment | What’s Here | Folder |
|---|-----------|------------|--------|
| 1 | Savings Analysis Automation | Working Streamlit app + matching pipeline + sample data | [`assignment-1-savings-analysis/`](./assignment-1-savings-analysis/) |
| 2 | Stripe × HubSpot Integration | Architecture decision doc with 3 options + recommendation | [`assignment-2-stripe-hubspot/`](./assignment-2-stripe-hubspot/) |
| 3 | Project Prioritization | Ranked projects with framework + 90-day sprint plan | [`assignment-3-prioritization/`](./assignment-3-prioritization/) |
| 4 | Video Walkthrough | Loom recording (link in folder) | [`assignment-4-video/`](./assignment-4-video/) |

---

## Quick Start — Assignment 1 (the working POC)

```bash
cd assignment-1-savings-analysis

pip install -r requirements.txt

# Optional: add your Anthropic API key for AI-assisted matching
cp .env.example .env
# edit .env → set ANTHROPIC_API_KEY=your_key_here

streamlit run app.py
```

Open `http://localhost:8501` → click **Load sample data** on both uploaders → see results instantly.

The app works without an API key (fuzzy-only mode). The Claude AI pass is optional and handles ambiguous edge cases that fuzzy matching can’t resolve.

---

## Approach

The brief says *”a rough working thing beats a beautiful description.”* That’s the frame I used:

- **Assignment 1** has running code and sample data you can try right now
- **Assignments 2 and 3** are concise decision documents — enough to act on, not padded
- The architecture reflects what I’d actually build, including honest notes on what this POC skips and why

**On the stack:** Everything here is free and open-source — pandas, RapidFuzz, Streamlit, n8n. Tools a small team can actually run and maintain.

**On the production vision:** The right long-term architecture for product matching at scale is a knowledge graph with Graph RAG — dental supply items as nodes, semantic edges across supplier naming conventions, continuous learning from confirmed matches. That’s a multi-week build. This POC demonstrates the concept and gets the job done today.

---

## Assumptions Made

- Prospect purchase history arrives as a CSV (the most common export format from dental practice management software)
- Source Club’s catalog is relatively stable, so a static CSV or periodic refresh works for the POC
- “Annual quantity” in the prospect file = actual purchasing frequency, not a one-time order
- The Stripe + HubSpot naming mismatch problem is solved with a one-time reconciliation script + indexed `stripe_customer_id` property going forward
- Project prioritization is based on context in the job description and case study brief; I’d refine rankings with 30 minutes of conversation about current ARR, churn rate, and team bandwidth
