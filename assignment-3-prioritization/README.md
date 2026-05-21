# Assignment 3 — Project Prioritization

## Framework

Every project gets scored on three axes:

- **Revenue Impact** — Does this directly add revenue or prevent churn in the next 90 days?
- **Operational Leverage** — Does this free up founder/team time that gets reinvested in growth?
- **Sequencing Dependency** — Is something else blocked until this is done?

Projects that score high on all three get done first. Projects that score high on Revenue Impact but require other things to exist first get sequenced accordingly.

---

## Project Rankings

### 🥇 1. Savings Analysis Automation

**Revenue Impact: Critical**
This is the primary conversion tool. Every new member goes through a savings analysis first. At 5–7 hours per analysis, the founder can only run so many per month — that's a hard ceiling on acquisition velocity. Automating this doesn't just save time, it removes a growth bottleneck entirely.

**Operational Leverage: Highest**
5–7 hours of skilled founder time → ~15 minutes of review on uncertain matches. That reclaimed time goes directly back into sales conversations and member success.

**An important nuance on the tech:** Source Club already partners with **Base86** (AI product matching) and **ZenOne** (procurement platform with 200K+ normalized SKUs). These are the right production-scale tools for matching. The automation work here is not rebuilding what Base86 does — it's building the **workflow wrapper** around it: the intake form, the pipeline that feeds prospect data into Base86/ZenOne, and the formatted savings report that comes out the other end. That's a much faster build than it looks on paper.

**Sequencing: None blocked by this; everything accelerates after**
Nothing needs to exist before this gets built. And once it's built, the team can run 2–3× as many analyses without adding headcount.

**Estimate:** 1–2 weeks to production-ready automation using existing ZenOne/Base86 integrations; faster than building matching from scratch

---

### 🥈 2. Stripe + HubSpot Integration

**Revenue Impact: High**
Without billing visibility in HubSpot, churn is invisible until it happens. With this integration, a `billing_health = at_risk` flag surfaces before a member cancels — creating a window for a proactive call. One retained member at $500–800/month pays for this project in the first month.

**Operational Leverage: High**
Every team member spends time manually cross-referencing Stripe and HubSpot today. This eliminates that entirely.

**Sequencing: Foundational for the reporting dashboard**
The dashboard (project 4) is only as good as the data feeding it. Do the integration first.

**Estimate:** 1 week with n8n (recommended approach)

---

### 🥉 3. Reporting Dashboard

**Revenue Impact: Medium**
Better internal visibility enables better decisions — catching churn trends, understanding which member segments save the most, identifying referral opportunities. Doesn't directly generate revenue but prevents bad decisions from losing it.

**Operational Leverage: Medium**
Eliminates ad-hoc reporting requests. Team spends less time building one-off exports.

**Sequencing: Requires integration (project 2) to be meaningful**
Build 2–3 weeks after the Stripe + HubSpot integration is stable. Use Metabase or Looker Studio — both free tiers are more than enough for this data volume.

**Estimate:** 2–3 weeks after integration is live

---

### 4. Member Portal

**Revenue Impact: High (medium-term)**
The portal is where members see their savings history, manage their account, and feel the value of their subscription. It's the most direct lever for reducing churn and driving referrals — but it's also the biggest project here.

**Operational Leverage: Moderate**
Reduces inbound support ("how much have I saved this year?"), automates reporting delivery.

**Sequencing: Depends on clean integration data**
The portal's value comes from surfacing real billing and savings data. Start this after the Stripe + HubSpot integration is stable. Also: the referral program (project 5) is dramatically more effective when it lives inside the portal.

**Estimate:** 6–10 weeks (largest project in the queue)

---

### 5. Referral Program Automation

**Revenue Impact: High potential, speculative**
Referrals from happy members are the highest-quality leads Source Club can get. But the word "happy" is doing a lot of work there. A member who can't easily see their savings won't refer anyone. A member who just saw "$18,400 saved this year" in their portal absolutely will.

**Operational Leverage: Low until scale, high after**
Automating the referral flow saves time at volume, but it needs volume to matter.

**Sequencing: Build on top of the member portal**
The portal is the right vehicle for referral prompts (post-savings-report display, renewal anniversary triggers). Sequence after project 4.

**Estimate:** 2–4 weeks after portal is live

---

## 90-Day Sprint Plan

| Week | Work |
|------|------|
| 1–3 | Savings Analysis Automation → production |
| 2–4 | Stripe + HubSpot Integration (slight overlap, independent workstreams) |
| 4–6 | Reporting Dashboard (data is now flowing) |
| 5–12 | Member Portal (longest project, starts after integration is stable) |
| 10–14 | Referral Program (built on top of portal) |

---

## What's Intentionally De-prioritized

**Member Portal is not first, even though it's impactful.** Starting the portal first means 6–10 weeks pass before any meaningful velocity improvement is visible. The sequencing argument is simple: integrations and automation first, because they make every subsequent project faster, cheaper, and more data-rich. A portal built before the Stripe sync is stable will need to be reworked anyway.

**Referral program is last, not because it's unimportant** — it's because referrals from members who haven't experienced the value yet don't convert. Get the experience right first.

---

## The Meta Point

The common thread across the top two priorities is **removing the human from the critical path**. Source Club is a small team that punches above its weight — the way you maintain that as you grow is by making sure the founder isn't the bottleneck on any repeatable process. Savings analysis automation and billing sync both directly address that. Everything else follows.
