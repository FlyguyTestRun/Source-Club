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

**On the existing stack (assumed, not confirmed):** the brief confirms only Stripe and HubSpot. I *assumed* Source Club uses **Base86** (AI product matching) and **ZenOne** (procurement catalog) and built around that — but I flag it as an assumption throughout, and verifying it is near the top of `docs/questions-i-would-ask-first.md`. The POC replicates the core matching capability with open-source tools so it stands on its own; *if* those platforms are in play, production integrates with them directly.

**On the production vision:** The full automation is a workflow wrapper: prospect submits purchase history via form → pipeline feeds it into Base86/ZenOne → formatted savings report goes back to the prospect automatically, no founder time required. The three-pass matching pipeline in this POC demonstrates the logic and data flow.

---

## Assumptions Made

- Prospect purchase history arrives as CSV or Excel export from their dental supplier (Benco, Patterson, Henry Schein)
- Source Club’s catalog data lives in ZenOne; static CSV used here as a stand-in
- “Annual quantity” in the prospect file = actual purchasing frequency, not a one-time order
- The Stripe + HubSpot naming mismatch is solved with a one-time reconciliation script + indexed `stripe_customer_id` custom property going forward
- The n8n integration (Assignment 2) can be extended to sync ZenOne and Base86 member data into HubSpot — not just billing
- Project prioritization is based on the case study brief context; I’d refine rankings with 30 min of conversation about current ARR, churn rate, and team bandwidth
