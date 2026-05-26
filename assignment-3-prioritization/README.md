# Assignment 3 — Project Prioritization

This prioritizes Source Club's **actual** project queue (May 2026 snapshot). The brief's question:
*if this were my first 90 days, which 3–5 projects would I tackle first, in what order, and why?*

## Framework

I score each project on three axes:

- **Revenue impact** — does it add revenue or prevent churn in the near term?
- **Operational leverage** — does it remove a human (especially the founder) from a repeatable
  critical path, freeing time that gets reinvested in growth?
- **Sequencing** — does it *unblock* other high-value work, or is it blocked until something else exists?

**On the two "HIGHEST PRIORITY" tags** (2.1 Savings Analysis and 3.1 Customer Service): both make my
list. But "highest priority" isn't the same as "do literally first." With one systems owner and a
7-person team, I can't run four big builds at once — so I lead with the one I can ship fastest for
visible impact (2.1), overlap the cheap foundational unlock (1.1), then bring on the bigger build-outs.

---

## First 90 days — my top 5, in order

### 🥇 1. Automate Savings Analysis — `2.1` *(HIGHEST PRIORITY · Not started)*

The single biggest bottleneck and the front door to revenue. ~10 min per analysis × 20–40/month, and
it's **founder-only** — so the founder's calendar is the hard cap on acquisition velocity. Automating
it removes that cap and frees the person who can least afford the interruption.

- **Why first:** highest revenue + leverage, no upstream dependency, and I already have a working POC
  (see Assignment 1), so this is the fastest path to a visible win.
- **Estimate:** 2–4 weeks to a production workflow (intake → clean → match → report → review queue).

### 🥈 2. Stripe ↔ HubSpot Name Matching — `1.1` *(Status: Next)*

This is Assignment 2's subject. The queue itself calls it *"foundational for billing reporting,
dashboards, and health scoring."* Until Stripe and HubSpot share a clean join key, every reporting
and health-score project downstream is built on sand.

- **Why early:** it's a contained systems integration with outsized unlock value (1.3, 3.4, 3.5 all
  depend on it). High leverage per hour spent.
- **Estimate:** ~1 week (one-time reconciliation script + indexed `stripe_customer_id` + event sync).

### 🥉 3. Consolidate Customer Service into HubSpot — `3.1` *(HIGHEST PRIORITY · Not started)*

Service requests are scattered across email, phone, and text with no ticketing or queue. That's a
direct retention risk (dropped requests = churn) and a daily drag on the team. Moving it into HubSpot
with real ticketing is the biggest retention-side lever in the queue.

- **Why third, not first:** it's a build-out, and doing `1.1` first means I understand the HubSpot
  data model deeply before standing up ticketing on top of it. I'd still start this inside month one.
- **Estimate:** 3–4 weeks for a working ticket system + queue; SLAs (`3.10`) follow.

### 4. ZenOne Data Integration — `1.2` *(Status: Idea)*

The data backbone. Pulling ordering + pricing data into one place is what makes the **Customer Health
Score (`3.5`)**, **lifecycle outreach (`3.6`)**, and the **unified dashboard (`1.3`)** possible — and
it feeds the savings analysis at scale. It's only an "Idea" today, and likely has vendor-API unknowns,
so I'd **de-risk access in week 1** (this is one of the first items in my discovery-questions doc).

- **Why fourth:** it compounds everything after it, but it's a foundation, not a quick win — so it
  runs in parallel behind the faster wins rather than blocking them.
- **Estimate:** 2–4 weeks once API access is confirmed.

### 5. Sales Pipeline Automation — `2.2` *(Status: Partially started)*

Already in flight, so cheap to finish — and it closes the loop with `2.1`: automating the
**purchase-history request emails** is literally the "collect the purchase history" step that feeds
the savings analysis. Finishing the 2–3 pipeline stages + post-close doc creation compounds the #1 win.

- **Estimate:** 1–2 weeks to finish the partially-built pieces.

---

## 90-Day Sprint Plan

| Week | Work |
|------|------|
| 1–4  | `2.1` Savings Analysis → production (POC already exists) |
| 2–5  | `1.1` Stripe ↔ HubSpot name matching (overlap; foundational, contained) |
| 4–8  | `3.1` Customer Service → HubSpot ticketing |
| 5–10 | `1.2` ZenOne data integration (de-risk API access wk 1; backbone for the CS data cluster) |
| 8–12 | `2.2` finish sales-pipeline automation; begin `1.3`/`3.5` foundation now that billing + ZenOne data flow |

---

## What I'd deliberately defer (and why)

- **Dashboards & scoring — `1.3` unified dashboard, `3.4` CS KPI, `3.5` health score:** only as good as
  the data feeding them. They wait on `1.1` (billing join) and `1.2` (ZenOne). Building them sooner
  means reworking them.
- **Lifecycle, referral, drip — `3.6`, `3.7`, `3.8`:** high potential but depend on health-score data
  and onboarding maturity (`3.2` is Phase 1 complete). A referral ask lands far better once a member
  has *seen* their savings; sequence after the data backbone.
- **Tooling & process polish — `1.4` Notion PM, `2.3` comms tools, `2.4` PandaDoc, `2.5` decks,
  `3.9`–`3.13`:** all real, none are first-90-days leverage. `2.4` PandaDoc is the strongest of these
  and would be my early next-quarter pick (it automates post-conversion enrollment).
- **`4.1` Company AI Audit & Enablement:** I'd run a *lightweight, continuous* version from day one —
  I'm auditing for automation opportunities as I build — but formalize the company-wide program next
  quarter, once shipped wins have earned the credibility to ask everyone for their time.

---

## The meta point

The common thread across my top picks is **removing the human — especially the founder — from the
critical path on repeatable, revenue-bearing processes**: acquisition (`2.1` + `2.2`), billing truth
(`1.1`), and retention (`3.1`). Then I build the data backbone (`1.2`) that turns the next wave —
scoring, lifecycle, dashboards — from guesswork into leverage. A small team punches above its weight
by making sure no one person is the bottleneck on anything that repeats. Everything else sequences off
that.

*(Final rankings would be refined with a 30-minute conversation about current ARR, churn rate, and
where the founder actually spends their week — see `docs/questions-i-would-ask-first.md`.)*
