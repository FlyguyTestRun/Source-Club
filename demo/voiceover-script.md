# Demo Voiceover Script (Assignment 1)

A simple, timed narration to read aloud while the auto-demo drives the app. Each block matches one
on-screen step. Run it with captions hidden and slower pacing:

```bash
python demo/record_demo.py --voiceover
```

Start your screen recorder (Loom, etc.), launch the command, and read each line as the matching
action happens. Total ≈ 70–80 seconds. Speak naturally — it's fine to pause; the demo waits.

> This covers **Assignment 1**. For the full 3–5 min submission video (A1 + A2 + A3 + close), use
> the complete script in `assignment-4-video/README.md` — this A1 portion slots into it.

---

### 1 · App opens *(the landing page appears)*
> "This is the savings-analysis tool I built. The brief said the founder runs these by hand — about
> ten minutes each, twenty to forty times a month — and it's the biggest bottleneck. Here's how I'd
> automate it."

### 2 · Savings Analysis page loads *(two uploaders show)*
> "The real process has two parts: collecting and cleaning a prospect's purchase history, then
> running the analysis. This focuses on the analysis engine — you upload the prospect's file and our
> pricing catalog."

### 3 · Samples load *(both files load)*
> "I'll use the sample prospect file and catalog. It runs with no API key — everything you're seeing
> is deterministic."

### 4 · Click Run *(spinner)*
> "The hard part is matching: suppliers describe the same product completely differently. So it runs
> three passes — exact SKU, then fuzzy text matching, then an optional AI pass for the ambiguous
> ones."

### 5 · Results appear — $4,944 *(metrics row)*
> "In a couple of seconds: about forty-nine hundred dollars in savings on this sample slice, at a
> seventy-eight percent match rate, with nineteen high-confidence matches."

### 6 · Needs Review tab
> "Anything the software isn't sure about doesn't get trusted — it drops into this review queue for a
> human to confirm. That's how I keep a person in the loop exactly where it matters."

### 7 · Unmatched tab
> "Items we don't carry are surfaced separately, never force-matched."

### 8 · All Results tab
> "And prices are compared per unit, so different pack sizes — a hundred-count box versus a fifty —
> don't throw the numbers off."

### 9 · Close
> "One deliberate call: I left the AI vendor choice open, because whether that's Gemini or Claude
> depends on which cloud Source Club is on — so I shipped a reliable floor and would decide that with
> the facts in hand. The whole point: take the founder out of this repeatable step entirely."

---

**Tips**
- If a line runs long, just keep talking — the next action waits for the pacing timer.
- Want more breathing room? Add `--hold-scale 2.2`. Faster? `--hold-scale 1.3`.
- Prefer captions *and* your voice? Drop `--voiceover` and the on-screen captions come back.
