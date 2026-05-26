# Assignment 4 — Video Walkthrough

## Loom Recording

🎥 **[View Walkthrough on Loom](https://loom.com/share/PLACEHOLDER)**

> *Link will be updated once recorded.*

---

## What's Covered (~3–5 minutes)

### Part 1 — Savings Analysis Demo (~2 min)
- Launch the Streamlit app live
- Load sample data with one click
- Walk through the match results table: show HIGH/MEDIUM/LOW confidence items
- Point out the review queue (LOW confidence items that need human eyes)
- Show the annual savings figure and download the CSV
- Explain the three-pass pipeline at a high level

### Part 2 — Stripe + HubSpot Architecture (~1 min)
- Share screen on `assignment-2-stripe-hubspot/README.md`
- Walk through the three options quickly
- Explain why n8n is the recommendation: free, self-hosted, visual, no per-operation cost
- Point out the multi-location data model and why it matters for practices with multiple offices

### Part 3 — Project Prioritization (~1 min)
- Share screen on `assignment-3-prioritization/README.md`
- Lead with the core argument: savings analysis automation removes the hard cap on acquisition velocity
- Explain the sequencing logic (integrations before portal, portal before referrals)
- Close with the meta point: the top priorities are about removing the founder from the critical path on repeatable processes

---

## Notes

The app in Part 1 runs in fuzzy-only mode for the demo (no API key required). To show the Claude AI pass working, set `ANTHROPIC_API_KEY` in `.env` and toggle the AI switch in the sidebar.
