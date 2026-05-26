# Assignment 2 — Stripe & HubSpot Integration Architecture

## The Problem

Stripe is the billing source of truth. HubSpot is the relationship source of truth. Right now they don't talk — which means:

- You can't see billing health from inside HubSpot when talking to a member
- You can't act on payment failures before a member churns
- Multi-location practices (one HubSpot Company, potentially multiple Stripe subscriptions) have no unified view
- The name your member gave Stripe and the name in HubSpot may not match — so even manual cross-referencing is error-prone

> **Note on the full systems picture:** *if* Source Club also uses **ZenOne** (procurement) and **Base86** (AI product matching) — my assumption, not stated in the brief — the same n8n workflow can be extended to sync their member status / usage data into HubSpot Company records, giving the team a single source of truth for each member's full lifecycle (billing health + procurement activity + savings tracked). The billing/CRM gap (Stripe → HubSpot) below stands on its own regardless.

---

## Three Options

### Option A — Native HubSpot × Stripe App (Marketplace)

HubSpot's App Marketplace has an official Stripe integration that syncs payment objects (invoices, quotes, subscriptions) as HubSpot *Payment* records.

| | |
|---|---|
| **Setup time** | ~30 minutes |
| **Cost** | Included with HubSpot Sales/Service Hub |
| **Pros** | Zero code, maintained by HubSpot, fast to deploy |
| **Cons** | Limited to HubSpot's defined field mapping — can't push custom fields like `stripe_billing_health` to Company records, doesn't handle multi-location rollup logic, won't reconcile naming mismatches |
| **Verdict** | Solves ~60% of the immediate need. Good "stop the bleeding" option for this week, but leaves the custom business logic gaps open. |

---

### Option B — n8n (Self-Hosted, Open Source) ✅ Recommended

[n8n](https://n8n.io) is a free, open-source workflow automation tool (think Zapier but self-hosted, no per-operation fees). Run it in a Docker container on any server.

**How it works:**
1. Stripe sends a webhook to your n8n instance on subscription events
2. n8n workflow: receives event → parses payload → looks up HubSpot Company by `stripe_customer_id` (custom property) → updates Company and Deal records

**Stripe events to handle:**
- `customer.subscription.updated` — sync new status + MRR
- `customer.subscription.deleted` — mark canceled
- `invoice.payment_failed` — set `stripe_billing_health = at_risk`
- `invoice.payment_succeeded` — reset health to healthy

**n8n workflow sketch:**
```
[Stripe Webhook Trigger]
        │
        ▼
[Parse Event Type]
        │
   ┌────┴─────────────────────────────┐
   ▼ payment_failed                   ▼ subscription.updated
[Set billing_health = at_risk]   [Update MRR + status]
        │                             │
        └──────────┬──────────────────┘
                   ▼
     [HubSpot: Find Company by stripe_customer_id]
                   │
                   ▼
     [HubSpot: Update Company Properties]
                   │
                   ▼
        [Log result / notify on error]
```

| | |
|---|---|
| **Setup time** | 2–3 hours (Docker deploy + workflow build) |
| **Cost** | Free (self-hosted) |
| **Pros** | Full control over field mapping and conditional logic, visual workflow builder, built-in retry and error logging, no SaaS cost, handles multi-location rollup |
| **Cons** | You host and maintain it, need a server (Railway/Render free tier works), another thing to monitor |
| **Verdict** | Best balance of power, flexibility, and zero ongoing cost for a small team. **This is the recommendation.** |

---

### Option C — Custom Webhook Handler (Python/FastAPI)

A lightweight Python service deployed on Railway or Render's free tier. ~50–80 lines of code.

```python
# Minimal sketch
@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)

    if event["type"] == "invoice.payment_failed":
        customer_id = event["data"]["object"]["customer"]
        hubspot_company = find_company_by_stripe_id(customer_id)
        update_hubspot_property(hubspot_company, "stripe_billing_health", "at_risk")
```

| | |
|---|---|
| **Setup time** | 4–6 hours |
| **Cost** | Free (Railway/Render free tier) |
| **Pros** | Maximum flexibility, version-controlled, no visual tool dependency, easiest to test |
| **Cons** | More upfront work, no visual builder for non-technical team members to modify |
| **Verdict** | Best long-term option, but n8n is faster to stand up and achieves the same result for this team size. Migrate here if n8n logic gets complex. |

---

## Recommendation: Start with n8n, migrate to custom if needed

**Why n8n first:**
Source Club runs lean. n8n gives the full flexibility of custom logic without requiring a deployment pipeline, tests, or CI — the visual workflow is the documentation. A non-engineer can follow the flow and understand what's happening.

**Migration path is low-risk:** Both n8n and the custom handler consume the same Stripe webhooks. Run them in parallel for a week, validate outputs match, then cut over. Zero downtime.

---

## HubSpot Properties to Create

Add these as custom Company properties before wiring either integration:

| Property | Type | Purpose |
|---|---|---|
| `stripe_customer_id` | Text (indexed) | Lookup key — the join between Stripe and HubSpot |
| `stripe_subscription_status` | Dropdown | `active`, `past_due`, `canceled`, `trialing` |
| `stripe_mrr` | Number (currency) | Monthly recurring revenue for this company |
| `stripe_billing_health` | Dropdown | `healthy`, `at_risk`, `delinquent` |
| `stripe_last_payment_date` | Date | Last successful payment |
| `stripe_location_count` | Number | For multi-location practices |

**One-time setup:** Run a script that fuzzy-matches Stripe customer names to HubSpot Company names and writes `stripe_customer_id` to each record. After that, all future syncing is event-driven.

---

## Multi-Location Data Model

```
HubSpot Company (e.g. "Smith Dental Group")
  ├── stripe_mrr = $895  (sum of all locations)
  ├── stripe_billing_health = at_risk  (worst across locations)
  │
  ├── Deal: "Location 1 – Downtown" → stripe_subscription_id = sub_xxx
  └── Deal: "Location 2 – Suburbs"  → stripe_subscription_id = sub_yyy
```

The Company record gets rollup fields (total MRR, worst health). Each Deal gets location-specific billing data. This way a sales rep sees the whole picture on the Company page, and a billing alert surfaces the specific location with the issue.
