# Source Club — 90-Day AI & Systems Architecture Scope

**Document type:** Strategic architecture proposal for the Head of AI Powered Operations role  
**Scope:** Weeks 1–12 post-hire  
**Prepared:** May 2026

---

## Platform Decision: Google Cloud (Vertex AI)

### TL;DR

Source Club runs on Google Workspace (confirmed). The right AI platform is **Google Vertex AI / Gemini Enterprise Agent Platform** — not AWS Bedrock, not Azure AI Foundry.

---

### What Each Platform Actually Is

| Platform | What It Is | Best For |
|----------|-----------|---------|
| **AWS Bedrock** | Amazon's managed AI API service — access Claude, Llama, Mistral, and 40+ other models through a single AWS endpoint. No infrastructure to manage; pay per token. | Teams already deep in AWS infrastructure; companies that need to compare many different models side-by-side |
| **Azure AI Foundry** | Microsoft's unified AI platform — model access + MLOps + deployment, tightly integrated with Microsoft 365, Teams, GitHub, and Copilot. | Companies already on Microsoft 365/Azure with existing Windows/Office workflows |
| **Google Vertex AI** | Google Cloud's AI platform — model access + agent orchestration + data pipelines, natively connected to Google Workspace (Docs, Sheets, Drive, Gmail, Calendar). | Companies on Google Workspace, data-heavy workflows, teams that need AI agents to work directly with their existing documents and spreadsheets |

---

### Why Vertex AI for Source Club

**Signal 1 — Google Workspace is already in use (confirmed)**
Source Club uses Google Docs for SOPs. Vertex AI agents connect directly to Google Docs, Sheets, Drive, and Gmail — no custom connectors needed. Choosing AWS or Azure means building bridges back to Google that don't need to exist.

**Signal 2 — Small team, lean infrastructure**
At 7 people, no one has time to manage complex AWS IAM policies or Azure subscription hierarchies. GCP is the most approachable cloud for a small technical team. Vertex AI's UI and docs are cleaner; onboarding is faster.

**Signal 3 — Startup credits ($350K advantage)**
Google's AI Track startup program offers up to **$350,000 in credits** (Year 1: $250K covering 100% of usage; Year 2: 20% match up to $100K). This means Source Club could run full production AI infrastructure at **zero cost for 12–18 months** while they scale.

For comparison:
- AWS Activate: up to $100K
- Microsoft for Startups: up to $150K
- **GCP AI Track: up to $350K** ✅

**Signal 4 — Cost-effective AI for dental supply matching**
Dental product matching is not a reasoning-heavy task. It needs fast, accurate categorization and semantic equivalency — a job for **Gemini 2.5 Flash** at $0.075 input / $0.30 output per 1M tokens (roughly 80% cheaper than Claude Sonnet for the same task). For ambiguous matches requiring deeper reasoning, Claude 3.5 Sonnet via Vertex Model Garden is available at standard pricing — no separate API contract needed.

**Signal 5 — Context caching for static catalog data**
ZenOne's 200K+ SKU catalog is largely static. Vertex AI's context caching feature discounts cached input tokens by **90%**. Load the catalog once, cache it, and every subsequent matching API call costs a fraction of standard pricing.

---

## Current System Map

Before proposing changes, here's the honest picture of what exists today:

```
PROSPECT ACQUISITION
  ┌─────────────────────────────────────────────────────────┐
  │  Dental Practice                                        │
  │  └── Exports purchase history from supplier            │
  │       (Benco, Patterson, Henry Schein — CSV/Excel)      │
  └──────────────────────┬──────────────────────────────────┘
                         │ Manual email/upload
                         ▼
MANUAL PROCESS (TODAY — ~10 min each, 20-40/mo = 5-7+ hrs/mo)
  ┌─────────────────────────────────────────────────────────┐
  │  Founder                                                │
  │  └── Opens prospect CSV                                 │
  │  └── Opens Source Club catalog (ZenOne)                 │
  │  └── Manually matches products line by line             │
  │  └── Calculates savings                                 │
  │  └── Builds savings report in Google Docs               │
  └──────────────────────┬──────────────────────────────────┘
                         │ Report sent to prospect
                         ▼
MEMBER ONBOARDING (EXISTING)
  ┌─────────────────────────────────────────────────────────┐
  │  HubSpot (CRM)  ←——X——→  Stripe (Billing)              │
  │       ↑                        ↑                        │
  │  No real-time sync         No CRM visibility            │
  │                                                         │
  │  ZenOne (Procurement)      Base86 (AI Matching)         │
  │  ↑ Used post-conversion    ↑ Used for matching          │
  │    (member operations)       but not in pipeline        │
  └─────────────────────────────────────────────────────────┘
```

**Core gaps:**
1. Savings analysis is a manual, founder-bottlenecked process
2. Stripe and HubSpot don't talk — billing health is invisible in CRM
3. ZenOne and Base86 exist but aren't wired into an automated workflow
4. No intake-to-report pipeline; no trigger, no automation, no email delivery

---

## Target Architecture — End of 90 Days

```
AUTOMATED INTAKE
  ┌──────────────────────────────────────────────────────────────┐
  │  Prospect fills out Google Form (or Typeform)                │
  │  └── Uploads CSV/Excel purchase history                      │
  │  └── Provides practice name, email, location count           │
  └────────────────────────────┬─────────────────────────────────┘
                               │ Trigger: new form submission
                               ▼
VERTEX AI AGENT PIPELINE (Google Cloud)
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  Agent 1: Intake & Parse                                     │
  │  └── Reads uploaded file from Google Drive                   │
  │  └── Auto-detects columns (Benco/Patterson/Schein headers)   │
  │  └── Normalizes SKUs, descriptions, pack sizes               │
  │                                                              │
  │  Agent 2: Product Matching                                   │
  │  └── Pass 1: Exact SKU → ZenOne catalog API                  │
  │  └── Pass 2: Fuzzy match → Base86 normalized product names   │
  │  └── Pass 3: Gemini 2.5 Flash semantic match (ambiguous)     │
  │  └── Confidence scoring: HIGH / MEDIUM / LOW                 │
  │  └── LOW items → human review queue (Google Sheet)           │
  │                                                              │
  │  Agent 3: Savings Calculation                                │
  │  └── Compares matched items: prospect price vs SC price      │
  │  └── Annualizes by quantity                                  │
  │  └── Generates summary: total savings, top opportunities     │
  │                                                              │
  │  Agent 4: Report Generation                                  │
  │  └── Populates Google Doc template with savings data         │
  │  └── Exports branded PDF                                     │
  │  └── Uploads to Google Drive (archived by practice name)     │
  │                                                              │
  │  Agent 5: Delivery & CRM Sync                                │
  │  └── Sends savings report PDF via Gmail to prospect          │
  │  └── Creates/updates HubSpot Contact + Company               │
  │  └── Logs analysis run to BigQuery                           │
  │                                                              │
  └────────────────────────────┬─────────────────────────────────┘
                               │ seconds of compute + brief review (vs ~10 min hands-on each today)
                               ▼
MEMBER ONBOARDING (AUTOMATED)
  ┌──────────────────────────────────────────────────────────────┐
  │  HubSpot (CRM)  ←──── n8n ────→  Stripe (Billing)           │
  │       ↑                               ↑                      │
  │  stripe_customer_id (indexed)    Webhooks on events:         │
  │  stripe_subscription_status      subscription.updated        │
  │  stripe_billing_health           invoice.payment_failed      │
  │  stripe_mrr                      subscription.deleted        │
  │                                                              │
  │  ZenOne (Procurement)         Base86 (AI Matching)           │
  │  ↑ Members order via ZenOne   ↑ Matching knowledge base      │
  │  ↑ Pricing data → pipeline    ↑ Normalized SKU graph         │
  │                                                              │
  │  BigQuery (Data Warehouse)    Looker Studio (Dashboard)      │
  │  ↑ Match logs, savings data   ↑ Member health, MRR,          │
  │  ↑ Member analytics           ↑ savings trends, referrals    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 90-Day Sprint Plan

### Phase 1 — Weeks 1–3: Remove the Bottleneck

**Goal:** Take the founder out of the per-analysis loop — from ~10 min of hands-on work each (5–7+ hrs/month) to near-zero, with only edge cases reviewed.

**What gets built:**
- Google Form intake (prospect uploads CSV/Excel + fills basic info)
- Vertex AI matching pipeline (exact SKU → Base86 fuzzy → Gemini Flash semantic)
- Google Sheets review queue for LOW confidence items
- Savings report generated from Google Doc template → PDF → emailed automatically
- Human reviews only the uncertain matches before send — a few minutes, and not necessarily the founder

**Tech used:**
- Vertex AI (Gemini 2.5 Flash + context caching on ZenOne catalog)
- Google Forms + Drive + Docs + Gmail (Google Workspace, already in use)
- Base86 API (existing partner — normalize their SKU data as input to matching)
- ZenOne API (existing partner — live catalog pricing, not a static CSV)

**Success metric:** Founder spends < 15 min per savings analysis. Match rate ≥ 85%.

---

### Phase 2 — Weeks 2–4: Connect Billing to CRM

**Goal:** Every HubSpot Company record shows real-time billing health from Stripe.

**What gets built:**
- n8n workflow (self-hosted, Docker): Stripe webhooks → HubSpot property updates
- One-time reconciliation script: fuzzy-match Stripe customer names → HubSpot Company records, write `stripe_customer_id` to each
- 5 custom HubSpot Company properties: `stripe_customer_id`, `stripe_subscription_status`, `stripe_mrr`, `stripe_billing_health`, `stripe_last_payment_date`
- Multi-location data model: Company → multiple Deals (one per location)

**Tech used:**
- n8n (self-hosted, free)
- Stripe webhooks
- HubSpot API

**Success metric:** Any team member can open a HubSpot Company record and see billing status, MRR, and health score in real time.

---

### Phase 3 — Weeks 4–7: Reporting + Data Foundation

**Goal:** Leadership sees a live dashboard of member health, savings delivered, and revenue.

**What gets built:**
- BigQuery data warehouse (GCP):
  - Members table (from HubSpot)
  - Billing table (from Stripe via n8n)
  - Savings analyses table (from Agent pipeline logs)
  - Match quality table (confidence scores, review queue outcomes)
- Looker Studio dashboard connected to BigQuery:
  - ARR and MRR trends
  - Member billing health (at-risk / delinquent count)
  - Savings delivered (total across all members YTD)
  - Match rate and AI accuracy metrics
  - Top members by savings (referral candidates)

**Tech used:**
- Google BigQuery (GCP — free tier covers this data volume easily)
- Looker Studio (free, Google's BI tool)
- n8n (data sync jobs)

**Success metric:** Weekly leadership review happens from the dashboard, not from ad-hoc Stripe/HubSpot exports.

---

### Phase 4 — Weeks 6–12: Member Portal (Foundation)

**Goal:** Members can log in, see their savings history, and manage their account — without calling the team.

**What gets built:**
- Member-facing web app (lightweight — React or Next.js)
- Authentication via Stripe Customer Portal (billing self-service) or custom
- Savings history page: pulls from BigQuery savings analyses log
- Account/billing page: shows subscription status, next payment date
- Foundation for referral program (Week 10+)

**Tech used:**
- Next.js (or Streamlit for speed, depending on design requirements)
- Supabase (auth + database for member portal) OR Google Firebase (if staying in GCP)
- BigQuery (data source for savings history)
- Stripe Customer Portal (billing management, no custom code needed)

**Success metric:** Inbound "how much have I saved?" support requests drop by 50%.

---

## Full Tech Stack — End of 90 Days

| Layer | Tool | Cost | Why |
|-------|------|------|-----|
| **AI Platform** | Google Vertex AI | Free (GCP AI Track credits) | Native Google Workspace integration, Gemini Flash cheapest model for matching |
| **AI Model (matching)** | Gemini 2.5 Flash | ~$0.075/$0.30 per 1M tokens | Fast, cheap, accurate for product categorization |
| **AI Model (complex)** | Claude 3.5 Sonnet via Vertex | ~$3/$15 per 1M tokens | Via Vertex Model Garden — no separate Anthropic contract needed |
| **Catalog source** | ZenOne API | Existing contract | 200K+ normalized SKUs, live pricing |
| **Matching knowledge** | Base86 | Existing contract | Normalized product graph, AI equivalency data |
| **Workflow automation** | Google Vertex AI Agents | Free (credits) | Multi-step pipeline: intake → match → report → CRM sync |
| **Billing/CRM sync** | n8n (self-hosted) | Free | Stripe ↔ HubSpot; extensible to ZenOne + Base86 |
| **CRM** | HubSpot | Existing subscription | Member relationships, pipeline tracking |
| **Billing** | Stripe | Existing subscription | Subscriptions, payment health |
| **Intake** | Google Forms | Free (Workspace) | Zero-friction prospect upload |
| **Document storage** | Google Drive | Free (Workspace) | Reports archive, catalog snapshots |
| **Report templates** | Google Docs | Free (Workspace) | Savings report template (autofilled by Agent 4) |
| **Data warehouse** | Google BigQuery | Free tier / ~$5/mo | Savings analytics, member health, referral tracking |
| **BI dashboard** | Looker Studio | Free | Member health, MRR, savings delivered |
| **Member portal DB** | Supabase (free tier) | Free | Auth + member data for portal |
| **Contracts/proposals** | PandaDoc | Existing subscription | Member enrollment after savings analysis |

---

## What AWS Bedrock and Azure AI Foundry Would Look Like Instead

### If they were on AWS Bedrock:
- Same Claude API, but calls routed through AWS instead of Anthropic direct
- Would need custom connectors to Google Workspace (no native integration)
- Slightly more model flexibility (Llama, Mistral easier to access)
- **$100K credits vs $350K** — significant gap at early stage
- Recommend only if they already have AWS infrastructure for other reasons

### If they were on Azure AI Foundry:
- Best if they migrated to Microsoft 365 (SharePoint, Teams, Outlook instead of Google Docs/Gmail)
- Deep GitHub integration (relevant for this case study codebase)
- GPT-4o natively available (strongest reasoning model for complex matching tasks)
- **$150K credits vs $350K** — still a gap
- Recommend only if they decide to exit Google Workspace

---

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| ZenOne/Base86 APIs have no public docs or access restrictions | Medium | Start with static catalog CSV (as POC does today); negotiate API access in Week 1 |
| Vertex AI Agent pipeline latency too slow for real-time UX | Low | Use async batch mode — form submitted → email sent in 5–10 min, not instant |
| Gemini Flash accuracy insufficient for ambiguous dental product names | Low | Fallback path to Claude 3.5 Sonnet (via Vertex Model Garden) for LOW confidence items |
| GCP AI Track credits require application/approval | Low | Apply on Day 1; approval typically takes 1–2 weeks; use Anthropic direct API in the interim |
| n8n self-hosted requires a server to run on | Low | Deploy on Railway or Render free tier; or GCP Cloud Run (free tier) |
| Prospect portal scope creep delays delivery | Medium | Build the minimum: savings history + billing status. No custom design in Phase 4. |

---

## Day 1 Checklist

On the first day in the role, before writing a single line of code:

- [ ] Get access to ZenOne — understand catalog format and API availability
- [ ] Get access to Base86 — understand matching API, data export format
- [ ] Confirm Google Workspace plan tier (needed for certain Drive/Docs API quotas)
- [ ] Apply for GCP AI Track startup credits ($250K Year 1)
- [ ] Review current HubSpot Company structure — confirm there's a custom property field for `stripe_customer_id`
- [ ] Pull one real prospect purchase history file to see actual column names/format
- [ ] Watch all remaining Source Club SOPs to understand the full current manual workflow
- [ ] Have 30-min conversation with founder: current ARR, target ARR, churn rate, biggest bottleneck beyond savings analysis

---

## Out of Scope for 90 Days

The following are real projects but don't fit in the 90-day window without sacrificing execution quality on the above:

- **Referral program automation** — depends on Member Portal (Phase 4) being stable
- **Fine-tuning a custom model** on Source Club's historical match data — requires 6+ months of match logs first
- **Full-featured member portal** (multi-page, custom design system) — Phase 4 builds the foundation only
- **EDI integration with dental suppliers** — enterprise-level; not needed for current scale
- **Predictive churn model** — needs 12+ months of BigQuery billing data first
