# Source Club — Case Study Submission

My response to the Source Club case study for the **Head of AI Powered Operations, Systems & RevOps**
role. One working app (Assignment 1) plus concise decision docs (2 & 3), a self-narrating video
walkthrough (4), and a bonus 90-day architecture scope.

> **Reviewers — start here:** [`INTERVIEWER_GUIDE.md`](./INTERVIEWER_GUIDE.md) is the 2-minute
> "how to run it and what to look at" guide. Everything below links straight to each deliverable.

---

## Deliverables — at a glance

| # | Assignment | What it is | Open it |
|---|-----------|-----------|---------|
| 1 | **Savings Analysis Automation** | **Working app** + 3-pass matching pipeline + sample data | [code & architecture](./assignment-1-savings-analysis/README.md) · run it ↓ |
| 2 | Stripe × HubSpot Integration | Decision doc: 3 options → recommendation (n8n), schema, multi-location model | [read](./assignment-2-stripe-hubspot/README.md) |
| 3 | Project Prioritization | The **real project queue**, ranked: top 5 for the first 90 days + what I'd defer | [read](./assignment-3-prioritization/README.md) |
| 4 | Video Walkthrough | **Self-narrating demo video** (built-in voiceover) + recording script | [folder](./assignment-4-video/README.md) · video ↓ |
| ⭐ | 90-Day Architecture Scope (bonus) | Platform decision + end-state system design + cost model | [read](./docs/90-day-architecture-scope.md) |

**Supporting docs:**
[`docs/CASE-STUDY-BRIEF.md`](./docs/CASE-STUDY-BRIEF.md) (the brief, verbatim — source of truth) ·
[`docs/questions-i-would-ask-first.md`](./docs/questions-i-would-ask-first.md) (what I'd confirm before building) ·
[`docs/DEPLOY.md`](./docs/DEPLOY.md) (free hosting options).

---

## Run the app (Assignment 1)

```bash
pip install -r requirements.txt
streamlit run app.py            # opens http://localhost:8501 — all pages in the sidebar
```
On the **💰 Savings Analysis** page: click **Load sample** on both uploaders → **Run** →
**~$4,944 in savings at a 78.6% match rate** (19 high-confidence). Works with no API key
(fuzzy-only); add `ANTHROPIC_API_KEY` to a `.env` to enable the optional Claude pass.

No live URL needed to evaluate — the brief asks for "links or files," and this repo + the video
are the working thing. Optional one-click hosting (Render / Hugging Face) is in
[`docs/DEPLOY.md`](./docs/DEPLOY.md).

## Watch the demo (Assignment 4) — with audio

A finished, **self-narrating** walkthrough of the live tool (natural neural voiceover, no recording
required). Three ways to play it, all with sound:

- **On GitHub (no install):** open
  [`demo/output/source-club-demo-narrated.mp4`](./demo/output/source-club-demo-narrated.mp4) →
  GitHub plays the MP4 inline in the file view. Press play, sound on.
- **Locally (file):** open `demo/output/source-club-demo-narrated.mp4` in any browser/player, or the
  `.webm` version.
- **Locally (in the app):** `streamlit run app.py` → **🎥 Video Walkthrough** page → press play.

Rebuild or re-voice it with [`demo/record_narrated.py`](./demo/record_narrated.py) (outputs both
`.mp4` and `.webm`); narrate it in your own voice with
[`demo/voiceover-script.md`](./demo/voiceover-script.md).

---

## How I approached it

The brief says *"a rough working thing beats a beautiful description"* — so:
- **Assignment 1** is running code you can try right now, structured as the team's own **two-part
  process** (collect & clean the purchase history → run the analysis). It's honest about which part
  is fully built (the analysis engine) vs. lighter (the cleanup), per the Benco training video.
- **Assignments 2 & 3** are concise, act-on-able decision docs — Assignment 3 prioritizes the
  **actual project queue**, not invented projects.
- The architecture reflects what I'd actually build, with explicit notes on what the POC skips.

**Confirmed vs. assumed:** the brief confirms only **Stripe** and **HubSpot**. Google Workspace,
GCP, **ZenOne**, **Base86**, and PandaDoc are my working assumptions — flagged as such throughout,
with verification near the top of [`docs/questions-i-would-ask-first.md`](./docs/questions-i-would-ask-first.md).
A strong operator asks those questions before committing a platform; I built a reliable floor and
deferred the bets that depend on answers I don't have yet (e.g., the AI vendor).

## Repository layout

```
app.py                         Landing page — run this (multipage Streamlit)
INTERVIEWER_GUIDE.md           Reviewer quick-start
pages/                         1 live tool + 4 doc pages (savings, stripe/hubspot, prioritization, video, architecture)
assignment-1-savings-analysis/ savings_ui.py · matcher.py · report_generator.py · sample_data/
assignment-2-stripe-hubspot/   README.md (decision doc)
assignment-3-prioritization/   README.md (real-queue prioritization)
assignment-4-video/            README.md (script) — demo video lives in demo/output/
demo/                          record_narrated.py (self-narrating) · record_demo.py · voiceover-script.md
docs/                          CASE-STUDY-BRIEF.md · questions-i-would-ask-first.md · 90-day-architecture-scope.md · DEPLOY.md
```
