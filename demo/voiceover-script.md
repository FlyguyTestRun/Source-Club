# Demo Voiceover Script (Assignment 1) — business-case-first

A simple, timed narration to read aloud while the auto-demo drives the app. It **opens on the
business case** (the bottleneck and the ROI) and *then* shows the tool. Each block matches one
on-screen step. Run with captions hidden and a relaxed ~2.2× pace:

```bash
python demo/record_demo.py --voiceover
```

Start your screen recorder (Loom, etc.), launch the command, and read each line as the matching
action happens. Total ≈ 90 seconds. Speak naturally — pause whenever; the demo waits for the timer.

> This is the **Assignment 1** segment. For the full 3–5 min video (A1 + A2 + A3 + close), it slots
> into the complete script in `assignment-4-video/README.md`.

---

### 1 · App opens — *lead with the problem* *(landing page)*
> "Before I show you anything — Source Club's single biggest bottleneck is the savings analysis.
> Every prospect needs one before they'll sign, and right now the founder does each one by hand."

### 2 · Savings Analysis page *(the two uploaders appear)*
> "It's about ten minutes each, twenty to forty times a month — call it five to seven hours a month.
> But the real cost is that it's *founder-only*: it caps how fast we can sign new members, and it
> ties up the one person who can least afford the interruption. This tool removes that cap."

### 3 · Samples load *(Prospect: 28 rows | Catalog: 28 items)*
> "The process has two parts — collecting and cleaning the purchase history, then running the
> analysis. Here I upload the prospect's file and our pricing catalog. No API key — it's all
> deterministic."

### 4 · Click Run *(spinner)*
> "Matching is the hard part, because suppliers describe the same product totally differently. So it
> runs three passes — exact SKU, then fuzzy text matching, then an optional AI pass for the
> genuinely ambiguous ones."

### 5 · Results — $4,944 *(metrics + table)*
> "A couple of seconds later: about forty-nine hundred dollars in savings on this sample slice, a
> seventy-eight percent match rate, nineteen high-confidence matches. And it compares prices
> per-unit — so a hundred-count box versus a fifty doesn't throw the numbers off."

### 6 · Needs Review tab *(MEDIUM matches)*
> "Anything the software isn't fully sure about doesn't get trusted — it drops into this review queue
> for a human to confirm. That's how I keep a person in the loop exactly where judgment matters."

### 7 · Unmatched tab
> "Items we don't carry are surfaced separately — never force-matched into a fake savings number."

### 8 · Close
> "One deliberate call: I left the AI vendor open — Gemini or Claude depends on which cloud you're
> on — so I shipped a reliable floor and would decide that with the facts in hand. The whole point is
> the business case I opened with: get the founder out of this repeatable step entirely, so growth
> isn't capped by one person's calendar."

---

**Tips**
- Lines run long? Just keep talking — the next action waits for the pacing timer.
- More breathing room: `python demo/record_demo.py --voiceover --hold-scale 3`.
- Tighter: `--hold-scale 1.6`. Want captions back *and* your voice? Drop `--voiceover`.
