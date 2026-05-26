# Assignment 1 — Savings Analysis Automation

## The Problem

Generating a savings analysis for a prospect currently takes **5–7 hours of founder time** per analysis. At 20–40 analyses per month, that's a hard cap on how fast Source Club can grow — you can only acquire as many members as there are hours to manually match their purchase history against the catalog.

The core challenge: dental suppliers use completely inconsistent product naming, SKUs, pack sizes, and units. A product that one supplier calls *"Nitrile Exam Gloves Medium 100/bx"* shows up in another's invoice as *"EXAM GLOVES NITRILE MED 100CT"* — same product, zero overlap in text.

---

## Existing Tech Stack Context

Source Club already partners with two platforms that are directly relevant here:

| Platform | Role | How It Fits |
|----------|------|-------------|
| **ZenOne** | Procurement platform — 200K+ normalized SKUs, multi-supplier price comparison, CSV export | The **catalog source of truth**. Production version of this tool pulls pricing directly from ZenOne rather than a static CSV |
| **Base86** | AI-driven product matching — semantic equivalency across supplier catalogs | The **matching engine** at production scale. This POC replicates Base86's core capability using open-source tools (Claude + RapidFuzz) so it can be evaluated and iterated on independently |

**Why build a POC when Base86 exists?**
Base86 is an enterprise platform designed for broad procurement use cases. What Source Club needs is a **purpose-built savings analysis workflow** — prospect uploads a file, gets a formatted savings report in minutes, with a human review queue for uncertain matches. That last mile of workflow automation is what this POC demonstrates. The production version would integrate Base86's matching data as an input rather than replacing it.

---

## Architecture

A three-pass matching pipeline that starts cheap and fast, escalates only when needed:

```
[Prospect CSV / Excel Upload]
  (Benco, Patterson, Henry Schein, any supplier export format)
        │
        ▼
[Ingestion + Normalization]
  - Auto-detect column names (Item Number → description, Your Price → unit_price, etc.)
  - Lowercase, expand abbreviations (bx→box, pk→pack, ea→each, cs→case)
  - Strip punctuation, normalize whitespace
  - SKU: strip non-alphanumeric, uppercase
  - Drop empty rows from Excel exports
        │
        ▼
[Pass 1: Exact SKU Match]  ──────────────────── Match? → HIGH confidence
  Dict lookup on normalized supplier/manufacturer SKU
  (In production: lookup against ZenOne SKU index)
        │ No match
        ▼
[Pass 2: Fuzzy Description Match]  ─────────── Score ≥ 72? → MEDIUM/HIGH
  RapidFuzz token_sort_ratio against catalog descriptions
  (In production: against Base86 normalized product names)
        │ Score < threshold
        ▼
[Pass 3: Claude AI Semantic Match]  ─────────── Batch of up to 20 items
  Sends ambiguous items + top fuzzy candidates to Claude
  System prompt: dental supply domain expert
  Structured JSON response: {catalog_id, confidence, reasoning}
  Falls back to best fuzzy score if API unavailable
        │
        ▼
[Confidence Scoring]
  🟢 HIGH ≥ 90   → Auto-accepted
  🟡 MEDIUM ≥ 70 → Flagged for quick human review
  🔴 LOW < 70    → Review queue (human makes the call)
        │
        ▼
[Output Tabs]
  All Results | Needs Review | Unmatched
  + Download full CSV report
```

**Why three passes?** Exact SKU is free and instant. Fuzzy catches ~70% of remaining items at negligible cost. Claude handles genuinely ambiguous cases — brand aliases, pack-size conversions, generic vs. branded equivalents. Batching keeps API cost to pennies per analysis.

---

## Stack

| Tool | Purpose | Cost |
|------|---------|------|
| `pandas` | CSV/Excel ingestion, data wrangling | Free / OSS |
| `openpyxl` | Excel `.xlsx` support, multi-sheet handling | Free / OSS |
| `rapidfuzz` | Fuzzy string matching | Free / OSS (MIT) |
| `streamlit` | Web UI — no frontend code needed | Free / OSS |
| `anthropic` SDK | Claude API for ambiguous matches | ~<$0.10/analysis |
| `python-dotenv` | API key loading | Free / OSS |
| **ZenOne** *(production)* | Live catalog pricing via API | Existing contract |
| **Base86** *(production)* | Normalized product knowledge base | Existing contract |

---

## How to Run

```bash
cd assignment-1-savings-analysis

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key (optional — app works without it)
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY=your_key_here

# Launch
streamlit run app.py
```

Open `http://localhost:8501` → click **Load sample** on both uploaders → instant demo, no API key needed.

**No API key?** App runs in fuzzy-only mode (Pass 3 skipped). Match rate is ~78% on sample data; AI mode pushes it higher on ambiguous items.

---

## Supported Input Formats

The app auto-detects column names from any supplier export:

| Supplier | Column Names Auto-Detected |
|---------|---------------------------|
| **Benco Dental** | `Item Number`, `Your Price`, `Qty Ordered`, `Mfr#`, `Extended Price` |
| **Patterson Dental** | `Catalog#`, `Item Name`, `Net Price`, `Quantity`, `Unit of Measure` |
| **Henry Schein** | `Product Number`, `Product Description`, `Price Each`, `Units Ordered` |
| **Generic CSV/Excel** | Any common variant — falls back to manual mapping UI if not detected |

If a column isn't auto-detected, the app shows a dropdown for manual mapping before running.

---

## Sample Data

`sample_data/prospect_purchase_history.csv` — 28 rows exercising all match paths:
- 8 rows: clean SKU matches → HIGH confidence
- 10 rows: description variations (e.g. "Nitrile Exam Gloves Medium 100/bx" vs. "EXAM GLOVES NITRILE MED 100CT")
- 5 rows: pack-size normalization required
- 5 rows: genuinely ambiguous → Claude resolves with reasoning
- 2 rows: intentionally unmatched (items Source Club doesn't carry)

Pricing uses realistic dental supply market rates. Savings totals align with Source Club's stated $10K–$30K/year member savings range.

---

## What This POC Doesn't Cover (Yet)

This is a working proof-of-concept. The right direction is clear; it just needs time:

**Immediate (Week 1–2):**
- Connect to live ZenOne catalog via API instead of static CSV
- Pull Base86's normalized product data as the matching knowledge base
- One-click "approve / correct" flow in the review queue tab

**Short-term (Month 1):**
- **Hosted deploy** (Streamlit Cloud or Azure Container Apps) — no local install needed
- **Match cache** — confirmed matches stored locally; Claude API calls drop to near zero over time
- **Pack size unit normalization** — "100/box @ $18" vs. "50/box @ $10" auto-converted to per-unit price before comparing

**Production architecture:**
> The right long-term system is a **product knowledge graph** backed by Base86's catalog data — dental supply items as nodes, edges representing "same product, different supplier branding." A Graph RAG layer over this graph would match new items semantically, with accuracy improving continuously as more analyses run through it. The three-pass pipeline above is the pragmatic POC that gets the job done today and demonstrates the approach.

**Full workflow automation (Long-term):**
- Prospect submits purchase history via web form
- Automated pipeline runs matching, calculates savings
- Formatted savings report emailed back in minutes — zero founder involvement
- Ties into PandaDoc/Stripe pipeline for seamless member enrollment after conversion
