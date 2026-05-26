# Questions I'd Ask First

**Why this document exists.** The brief says to make reasonable assumptions and keep moving — so I built a working POC on a clearly-labeled set of assumptions. But the highest-leverage move in this role isn't to *guess* the architecture; it's to ask a handful of sharp questions, then build the right thing once. A few examples: I deliberately did **not** hard-wire the AI matching layer or commit to a single cloud in the prototype, because both decisions hinge on answers I don't have yet. Below is what I'd want to know on day one, and what each answer would change.

Only **Stripe** and **HubSpot** are confirmed in the brief. Everything else below (Google Workspace, GCP, ZenOne, Base86, PandaDoc) is my working assumption — flagged as such throughout the deliverables — and the first thing I'd verify.

---

## 1. Platform & infrastructure

- **Are you only on GCP — or even on Google at all?** My Vertex AI recommendation rests entirely on the assumption that Source Club lives in Google Workspace. *If that's wrong* (e.g. you're on Microsoft 365, or cloud-agnostic), the platform call flips to Azure AI Foundry or a provider-neutral build. This is the single assumption I'd confirm before anything else.
- **Is there any existing cloud footprint already paid for?** An existing AWS/Azure account with committed spend can outweigh credit programs.
- **Who administers infrastructure today, and how much appetite is there for self-hosting** (e.g. n8n on a server) vs. fully managed tools? With ~7 people, "who babysits it at 2am" is a real constraint.
- **Any compliance constraints?** Dental purchasing is healthcare-adjacent — is there PHI in these files, and does HIPAA/BAA factor into which AI vendors we can use?

## 2. Company & project scale

- **How many members today, and what's the growth target for the next 12 months?** This sets whether I optimize for "remove the founder bottleneck" or "scale to thousands of analyses."
- **Analysis volume:** the brief says 20–40/month today — what's the projected volume after this is automated and sales pushes harder? That drives the build-vs-buy and cost model.
- **How big is the pricing catalog, and how often does it change?** Hundreds vs. hundreds-of-thousands of SKUs changes the matching strategy (in-memory fuzzy vs. a vector index / knowledge graph), and update cadence changes caching.
- **Who's on the team and who's technical?** Determines how much of this can be maintained by non-engineers (favoring no-code/visual tools) vs. owned in code.

## 3. The matching problem (Assignment 1)

- **Do you actually use ZenOne and Base86** (my assumption), or is the catalog somewhere else (a spreadsheet, a supplier portal)? Where the catalog lives — and whether it has an API — decides whether the pipeline reads live data or a periodic export.
- **What do real prospect files look like?** Which suppliers (Benco, Patterson, Henry Schein, others), and are they clean CSVs or messy multi-tab Excel? I built against a synthetic sample; real exports would refine the column auto-detection.
- **What's the acceptable accuracy bar, and who reviews uncertain matches?** A false "this is the same product" is worse than a miss. The confidence-tier thresholds and who staffs the review queue depend on your risk tolerance.
- **How are pack-size and unit-of-measure differences handled today by the founder?** The POC normalizes per-unit when units match and falls back otherwise; real edge cases (g↔lb conversions) would tell me whether to invest in a units table.

## 4. AI layer — why I deferred it in the POC

- The prototype ships with **deterministic fuzzy matching** ($4,944 / 78.6% on the sample, no API key). I left the AI pass *optional and off by default* on purpose: choosing **Gemini (Vertex) vs. Claude (Anthropic/Bedrock) vs. something else** depends on the platform answer (Q1), the accuracy bar (Q3), and cost at your real volume (Q2). I'd rather demo a reliable floor and pick the AI vendor with the facts in hand than bake in a choice I'd have to unwind.

## 5. Billing ↔ CRM (Assignment 2)

- **How many multi-location customers are there, and how deep do they go?** A handful vs. dozens changes whether the Company→Deal rollup is worth automating now.
- **What's the current HubSpot Company property structure?** Tells me what to add vs. reuse, and whether there's already a join key to Stripe.
- **Stripe event volume and how fast billing health must surface** — near-real-time vs. a nightly sync changes the tool choice (n8n vs. native vs. custom).

## 6. Prioritization (Assignment 3)

- **What's actually in the project queue, and what does each item mean to you?** I'd anchor sequencing to the real list and your sense of impact rather than a generic ranking.
- **What's the current biggest pain beyond savings analysis** — churn, onboarding, reporting? That reorders everything after the top one or two.

---

**Bottom line.** I made calls and built a working thing, as the brief asked. But I'd treat the architecture as a *hypothesis*: the answers above would either confirm it in a day or redirect it before I've sunk time into the wrong platform. Knowing which questions to ask — and which decisions are cheap to defer — is the core of the job.
