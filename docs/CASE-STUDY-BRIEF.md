# Case Study Brief — Source of Truth (verbatim)

> **This is the authoritative scope.** Everything we build must trace back to *this* document.
> When the deliverables and this file disagree, **this file wins.** Captured from the official
> SourceClub Step-2 Case Study brief + the Assignment-1 Loom resources + the Assignment-3 project
> queue. Only facts stated here are confirmed; anything else (cloud platform, ZenOne, Base86,
> Google Workspace, PandaDoc) is an *assumption* and must be labeled as such.

---

## Role
**Head of AI Powered Operations, Systems, & RevOps** — owns the systems, automations, data, and AI
workflows that let a ~7-person team run like a much bigger one.

## Ground rules (load-bearing — read before building)
- **Timebox: 4–6 hours.** "Not a polished consulting deliverable — how you think and what you can
  actually build. **A rough working thing beats a beautiful description of one.**"
- **Tool-agnostic.** "Use whatever tools you would actually use — Claude, spreadsheets, scripts,
  no-code tools, anything." **Streamlit is NOT required or mentioned** — it was our choice.
- **Deliverables = "links or files."** A live hosted app is *not* required; a repo + files + a demo
  video satisfies "show us what you built."
- **Make assumptions, state them, keep moving.** "Where something is ambiguous, make a call, state
  your assumption." They may have left out details.
- **Confirmed company facts:** dental GPO; negotiates bulk pricing; flat monthly subscription; zero
  vendor kickbacks; members save **$10,000–$30,000/year**; ~7-person team. **Confirmed tools: Stripe
  (billing) + HubSpot (CRM) only.** Nothing else is confirmed by the brief.

## Pay & delivery logistics
- $50 via PayPal/Venmo on submission (include a valid PayPal **or** Venmo address or they can't pay).
- **Return within 2 business days** of receipt; earlier is better.
- **Email to:** `jpuhl@sourceclub.io` **AND** `cduarte@sourceclub.io`.
- Links must be **"anyone with the link can view."**
- Email must include: links for Assignments 1–3, a video link, PayPal/Venmo, **hours spent**, any
  comments/feedback, and optionally portfolio/GitHub links.
- Questions/issues → `jpuhl@sourceclub.io`.

---

## Assignment 1 — "Savings Analysis" Automation  *(suggested 2–3 hrs)*
**Situation.** Single biggest bottleneck. For a prospect, run a "savings analysis": take their
**purchase history** (export of everything they buy from their dental supplier) and compare each line
item against Source Club's negotiated pricing to show total potential savings. The founder does this
by hand — **~10 minutes per analysis, 20–40 times a month → 5–7+ hours a month.** Most-wanted to
automate.

**The hard part is matching:** prospect file vs. catalog rarely describe the same product the same
way — different manufacturer SKUs, descriptions, pack sizes, units of measure. A human can eyeball
"same box of gloves?"; software must be taught to.

**Task:**
- Design the end-to-end system. Pipeline? Where does AI work, where does a human stay in the loop?
  How are line items that don't cleanly match handled?
- Build as much of a working POC as reasonable in the time. A working prototype on a *slice* of data
  beats a polished doc. Use whatever tools you'd actually use.
- **Deliver:** architecture & approach, whatever you built (links/files), and a short "what's next."

### Assignment 1 resources (Jake's notes + Looms)
- **Two parts:** (1) **Collecting Purchase History**, (2) **Running Savings Analysis**.
- "Purchase History Cleanup Training" — videos ~8 months old; concepts mostly same, some data
  differences.
- Overview (where to find SA Looms): https://www.loom.com/share/25ae9f9f739c4f3cb54f22e3a4212660
- SA video folder: https://loom.com/share/folder/c10275d2ce8e47758d644180ae6f8efc
- **How to build Initial SA with Benco** (titled *"Benco Purchase History Manipulation and Savings
  Analysis Guide"*): https://www.loom.com/share/0ee5c4b27a5444188026882c49cabf25
- **Savings Analysis Training** (*"Step-by-Step Savings Analysis Process for Dental Supplies"*):
  https://www.loom.com/share/76e49312c83a4778b3ad10628c662aac

---

## Assignment 2 — Systems Architecture: Stripe ↔ HubSpot  *(suggested 30 min)*
**Situation.** Bill via Stripe, CRM in HubSpot. **One Stripe subscription = one practice location;
a multi-location company = one customer with several subscriptions.** Stripe company/subscription
names don't match HubSpot records, so nobody can see billing status in HubSpot without manual
cross-referencing. Want **subscription status, billing health, and revenue on the HubSpot company
record**.

**Task:** map 2–3 solution options (native integration / middleware / custom build — your call);
pick one and justify it (why over the others, cost, long-term success).

---

## Assignment 3 — Prioritizing Upcoming Projects  *(suggested 30 min)*
**Situation.** This role owns the project queue. Read the queue (below) and say how you'd prioritize:
**if this were your first 90 days, which 3–5 projects would you tackle first, in what order, and
why?** Less about a "right answer," more about reasoning on impact, sequencing, tradeoffs.

### Source Club — Project Queue (May 2026 snapshot; names → role labels; priority/status as-is)

**Category 1 — Infrastructure & Data Systems**
- **1.1 Stripe ↔ HubSpot Name Matching** — names must match exactly; complex due to multi-location;
  foundational for billing reporting, dashboards, health scoring. *Status: Next.*
- **1.2 ZenOne Data Integration** — ZenOne is the platform members order through; pull ordering &
  pricing data into one place. Data backbone for health score & lifecycle outreach. *Status: Idea.*
- **1.3 Unified Business Data Dashboard** — HubSpot + Google Analytics + Google Ads + Facebook Ads in
  one dashboard; full funnel from spend to closed revenue. *Status: Idea.*
- **1.4 Notion Project Management System** — automated project/task/weekly reporting. *Status: Idea.*

**Category 2 — Sales Pipeline**
- **2.1 Automate Savings Analysis — HIGHEST PRIORITY** — ~10 min × 20–40/month manual; purchase
  history → compare vs SC pricing → savings report. *Status: Not started.*
- **2.2 Sales Pipeline Automation (HubSpot)** — automate 2–3 pipeline stages; verify
  purchase-history request emails; automate post-close doc creation. *Status: Partially started.*
- **2.3 Communication Tools Integration** — phone/SMS in HubSpot; evaluate texting/calling tools.
  *Status: Not started.*
- **2.4 Automate PandaDoc Creation, Signing & Payment** — automate agreement generation/sending;
  frictionless member payment entry. *Status: Not started.*
- **2.5 Improve Sales Presentations** — rework discovery + savings-analysis-call decks. *Status: Not
  started.*

**Category 3 — Customer Success**
- **3.1 Consolidate Customer Service into HubSpot — HIGHEST PRIORITY** — requests scattered across
  email/phone/text, no ticketing; move into HubSpot with a proper ticket system. *Status: Not
  started.*
- **3.2 Onboarding Automation** — rework HubSpot onboarding pipeline; scheduler integration; date
  properties for metrics. *Status: Phase 1 complete.*
- **3.3 HubSpot Onboarding Calendar Integration** — connect onboarding-call calendar to HubSpot
  Meetings. *Status: Idea.*
- **3.4 CS KPI & Dashboard** — one HubSpot dashboard for daily CS performance. *Status: Idea.*
- **3.5 Customer Health Score** — score behavior/engagement post-onboarding; depends heavily on the
  ZenOne data integration. *Status: Discussion.*
- **3.6 45/90-Day Check-in & Lifecycle Engagement** — structured touchpoints; flag "missed savings";
  AI-assisted, low-lift. *Status: Discussion.*
- **3.7 Customer Referral & Advocacy Program** — systematized referral ask ~day 60–90; needs a
  referral landing page. *Status: Draft for review.*
- **3.8 Post-Onboarding Drip Campaign** — drip sequence in first two weeks post-onboarding. *Status:
  Next.*
- **3.9 Member Termination Process** — clean termination across billing, CRM, ordering platform,
  suppliers. *Status: Idea.*
- **3.10 Customer Service SLA & Onboarding Metrics** — response/resolution/escalation standards;
  onboarding metrics. *Status: Not started.*
- **3.11 Educational Product Offerings** — scalable self-serve member education. *Status:
  Discussion.*
- **3.12 Quotes Database** — reference DB of quotes CS can pull from. *Status: Idea.*
- **3.13 Monthly Vendor Roster** — current monthly vendor/supplier roster. *Status: Next.*

**Category 4 — Company-Wide AI Enablement**
- **4.1 Company AI Audit & Enablement Program** — interview everyone to find automation
  opportunities, build them, teach the team to use AI daily. *Status: Idea.*

---

## Assignment 4 — Video Walkthrough  *(3–5 min)*
Record a short video (≤5 min) walking through your answers to Assignments 1–3 — what you decided and
why. **Screen-share your work.** Figuring out the simplest way to record/share (Loom or similar) is
part of the assignment.

---

## What this means for our build (alignment guardrails)
- Streamlit is one valid choice, **not** a requirement; a hosted URL is optional. The public repo +
  demo video already satisfy "links or files" / "a rough working thing."
- Keep the savings-analysis metric correct: **~10 min/analysis, 20–40/mo, 5–7+ hrs/mo** (NOT per
  analysis).
- Only **Stripe + HubSpot** are confirmed. Label Google Workspace / GCP / ZenOne / Base86 / PandaDoc
  as assumptions; see `docs/questions-i-would-ask-first.md`.
- Assignment 1 is **two parts** (collect/clean → analyze); our POC is strong on Part 2, lighter on
  Part 1 cleanup — stated honestly.
- Assignment 3 must prioritize the **real queue above**, not invented projects.
