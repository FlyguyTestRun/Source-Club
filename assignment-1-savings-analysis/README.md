# Assignment 1 — Savings Analysis Automation

## The Problem

Generating a savings analysis for a prospect currently takes **5–7 hours of founder time** per analysis. At 20–40 analyses per month, that's a hard cap on how fast Source Club can grow — you can only acquire as many members as there are hours to manually match their purchase history against the catalog.

The core challenge: dental suppliers use completely inconsistent product naming, SKUs, pack sizes, and units. A product that one supplier calls *"Nitrile Exam Gloves Medium 100/bx"* shows up in another's invoice as *"EXAM GLOVES NITRILE MED 100CT"* — same product, zero overlap in text.

---

## Architecture

A three-pass matching pipeline that starts cheap and fast, escalates only when needed:

```
[Prospect CSV Upload]
        │
        ▼
[Ingestion + Normalization]
  - Lowercase, expand abbreviations (bx→box, pk→pack, ea→each…)
  - Strip punctuation, normalize whitespace
  - SKU: strip non-alphanumeric, uppercase
        │
        ▼
[Pass 1: Exact SKU Match]  ──────────────────── Match? → HIGH confidence
  Dict lookup on normalized supplier/manufacturer SKU
        │ No match
        ▼
[Pass 2: Fuzzy Description Match]  ─────────── Score ≥ 85? → MEDIUM/HIGH
  RapidFuzz token_sort_ratio against catalog descriptions
        │ Score < threshold
        ▼
[Pass 3: Claude AI Semantic Match]  ─────────── Batch of up to 20 items
  Sends ambiguous items + top fuzzy candidates to Claude
  Structured JSON response: {catalog_id, confidence, reasoning}
  Falls back to best fuzzy result if API unavailable
        │
        ▼
[Confidence Scoring]
  🟢 HIGH ≥ 90   → Auto-accepted
  🟡 MEDIUM ≥ 70 → Flagged for quick review
  🔴 LOW < 70    → Review queue (human decision)
        │
        ▼
[Output: Results Table + CSV Download + Review Queue]
```

**Why three passes?** Exact SKU is free and instant. Fuzzy catches ~70% of remaining items at negligible cost. Claude handles the genuinely ambiguous cases — brand aliases, pack size conversions, generic vs. branded equivalents. Batching keeps API cost to cents per analysis.

---

## Stack

| Tool | Purpose | Cost |
|------|---------|------|
| `pandas` | CSV ingestion, data wrangling | Free / OSS |
| `rapidfuzz` | Fuzzy string matching | Free / OSS (MIT) |
| `streamlit` | Web UI (no frontend code needed) | Free / OSS |
| `anthropic` SDK | Claude API for ambiguous matches | Pay-per-use (~<$0.10/analysis) |
| `python-dotenv` | API key loading | Free / OSS |

---

## How to Run

```bash
cd assignment-1-savings-analysis

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key (optional — app works without it in fuzzy-only mode)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Launch the app
streamlit run app.py
```

Then open `http://localhost:8501`.

Click **Load sample data** on both uploaders for an instant demo — no files needed.

### CLI / No API Key

The app runs in **fuzzy-only mode** if no API key is set. Pass 3 is skipped; unresolved items go directly to the review queue. Match rate drops slightly on ambiguous items, but the core functionality works.

---

## Sample Data

`sample_data/prospect_purchase_history.csv` — 28 rows exercising all match paths:
- 8 rows with clean SKU matches (easy wins → HIGH confidence)
- 10 rows with description variations (fuzzy match → MEDIUM/HIGH)
- 5 rows with pack-size or unit differences (normalization handles these)
- 5 genuinely ambiguous rows (Claude resolves with reasoning)
- 2 intentionally unmatched items (Source Club doesn't carry them)

Pricing is based on realistic dental supply market rates; the resulting savings totals align with Source Club's stated $10K–$30K/year member savings range.

---

## What This POC Doesn't Cover (Yet)

This is a working proof-of-concept, not a production system. The right direction is clear; it just needs more time to build:

**Immediate next steps:**
- Connect to the live Source Club catalog (Google Sheets API or direct DB query) instead of a static CSV
- Handle `.xlsx` uploads and multi-sheet workbooks (how most suppliers export)
- Add a simple one-click "approve match" / "correct match" flow for the review queue

**Short-term (Month 1):**
- **Streamlit Cloud or self-hosted deploy** so the founder doesn't need to run it locally
- **SQLite match cache** — previously confirmed matches are reused instantly, reducing Claude API calls to near zero over time
- **Pack size normalization** — handle "100/box @ $18" vs. "50/box @ $10" unit-price equivalence automatically

**The real production architecture (Graph RAG):**
> At scale, the right solution is a **product knowledge graph** — dental supply items as nodes, with edges representing "same product, different supplier branding." A Graph RAG system would embed all catalog items, build semantic relationships across supplier naming conventions, and match new items against the graph rather than a flat list. Accuracy improves continuously as more data flows through it. For a small team doing 20–40 analyses/month, the 3-pass pipeline above is the pragmatic POC that gets the job done today.

**Longer-term:**
- Trigger automatically when a prospect submits their purchase history via a web form
- Email the completed savings analysis back within minutes, no founder involvement required
- Track match-rate metrics over time to measure improvement
