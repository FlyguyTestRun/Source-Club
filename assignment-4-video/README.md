# Assignment 4 — Video Walkthrough

## Loom Recording

🎥 **[View Walkthrough on Loom](https://loom.com/share/PLACEHOLDER)**

> *Link will be updated once recorded — also set `LOOM_URL` in `pages/4_🎥_Video_Walkthrough.py`.*

---

## How to record (the simplest path — part of the assignment)

1. Open **Loom** (free Chrome extension or desktop app) → choose **Screen + cam** (or screen only).
2. Have two things open: the **running app** (`streamlit run app.py` → http://localhost:8501, or your
   deployed `*.streamlit.app` URL) and the **GitHub repo** for the docs.
3. Hit record, read the script below, keep it **under 5 minutes**, stop, copy the share link.

---

## Script (~4 minutes — read it, don't memorize it)

### 0:00 – 0:30 · Intro
> "Hi, I'm Bryan. This is my Source Club case study for the Head of AI Powered Operations role.
> I built a working tool for Assignment 1 and decision docs for 2 and 3 — I leaned into a working
> prototype over a write-up, like the brief asked. Let me show you."

### 0:30 – 2:00 · Assignment 1 — Savings Analysis *(screen-share the running app)*
> "This is the savings analyzer. The real process has two parts — collecting and cleaning a prospect's
> purchase history, then running the analysis — and this focuses on the analysis engine."

*(Click **Load sample** on both, click **Run Savings Analysis**.)*
> "I upload the prospect's purchase history and our catalog, hit run, and in seconds I get the savings
> — about $4,944 on this sample slice — at a 78.6% match rate."

*(Point at the table / tabs.)*
> "Matching is the hard part, because suppliers name the same product completely differently. So it
> runs three passes: exact SKU first, then fuzzy description matching, then an optional AI pass for
> the genuinely ambiguous ones. Everything gets a confidence tier — high matches auto-accept, and
> anything uncertain drops into this review queue so a human makes the call. It also compares prices
> per-unit, so different pack sizes don't throw off the savings."

> "One deliberate choice: I left the AI pass off by default. Whether that's Gemini or Claude depends
> on which cloud Source Club is on and your accuracy bar — so I shipped a reliable floor and would
> pick the AI vendor once I had those answers."

### 2:00 – 2:50 · Assignment 2 — Stripe ↔ HubSpot *(screen-share the assignment-2 README)*
> "Stripe is billing truth, HubSpot is relationship truth, and today they don't talk — so nobody can
> see billing health on a company without cross-referencing by hand. I mapped three options — the
> native integration, a middleware tool, and a custom build — and I'd start with **n8n**: it's free,
> self-hosted, visual, and flexible enough to handle your multi-location case, where one company has
> several Stripe subscriptions. Stripe webhooks update custom HubSpot company properties — status,
> MRR, billing health — and it migrates cleanly to a custom service later if the logic outgrows it."

### 2:50 – 3:50 · Assignment 3 — Prioritization *(screen-share the assignment-3 README)*
> "I prioritized your actual project queue. My first 90 days: number one is automating the savings
> analysis — it's your highest priority, it's founder-only, and it's the front door to revenue.
> Two is the Stripe-HubSpot name matching, because your own queue calls it foundational for every
> dashboard and health score downstream. Three is consolidating customer service into HubSpot — the
> big retention lever. Then the ZenOne data integration, because it's the backbone that unlocks the
> health score and lifecycle work, and finishing the partially-built sales-pipeline automation, which
> closes the loop with number one. The thread is the same: get the founder out of the repeatable
> revenue paths first, then build the data layer that makes everything after it leverage."

### 3:50 – 4:20 · Close
> "Last thing — I treated the architecture as a hypothesis, not gospel. I made assumptions where the
> brief was open, like the cloud platform, and I wrote down exactly what I'd confirm first. Knowing
> which questions to ask before you build is the core of this job. Thanks — happy to go deeper on any
> of it."

---

## Notes
- There's also an **auto-generated demo recording** embedded on the in-app Video Walkthrough page
  (produced by `demo/record_demo.py`) if you'd rather show that than a live run.
- The app runs in fuzzy-only mode by default (no API key). To show the AI pass, set
  `ANTHROPIC_API_KEY` and toggle it on in the sidebar.
