# Auto Demo & Recorder

A hands-free demo of the Savings Analyzer. It drives the app inside **its own
browser window** using Playwright — **your real mouse and keyboard are never
touched**, so you can keep working (or just watch it play). It can record the
whole run to a video file that the Assignment 4 page embeds automatically.

## What it shows
Opens the app → navigates to Savings Analysis → loads the sample prospect +
catalog → runs the 3-pass pipeline → walks the **$4,944 / 78.6%** result and the
review/unmatched tabs. On-screen captions narrate each step, so the recording
explains itself.

## Setup (one time)
```bash
pip install -r demo/requirements.txt
python -m playwright install chromium
```

## Self-narrating demo (no human voice needed)
`record_narrated.py` builds a finished video **with a built-in voiceover** — it synthesizes concise
narration with offline TTS (Windows SAPI), times each on-screen step to its line, and muxes the audio
into the video with the bundled ffmpeg:
```bash
python demo/record_narrated.py            # → demo/output/source-club-demo-narrated.webm
python demo/record_narrated.py --rate -2  # slower, clearer voice
```
The Video Walkthrough page plays this narrated version automatically when it exists (it falls back to
the silent captioned run below otherwise). To narrate in **your own** voice instead, use the
voiceover workflow below.

## Run it
```bash
# from the repo root
python demo/record_demo.py                # auto-starts the app, visible window, records video
python demo/record_demo.py --headless     # no visible window (faster, good for CI)
python demo/record_demo.py --no-record     # just watch it play, don't save a video
python demo/record_demo.py --no-start-server   # attach to an app you already have running
python demo/record_demo.py --use-ai        # also exercise the Claude pass (needs ANTHROPIC_API_KEY in .env)
python demo/record_demo.py --slow-mo 600   # slow the pacing down for a calmer recording
```

The video is written to `demo/output/source-club-demo.webm`. The **🎥 Video
Walkthrough** page plays it inline automatically whenever that file exists.

## Notes
- Default run is deterministic (fuzzy-only): same `$4,944 / 78.6%` every time.
- `--use-ai` turns on Pass 3; copy `assignment-1-savings-analysis/.env.example`
  to `.env` and set `ANTHROPIC_API_KEY` first.
- WebM plays in Chrome/Edge/Firefox and inside Streamlit. To hand someone an MP4,
  convert it: `ffmpeg -i demo/output/source-club-demo.webm demo/output/source-club-demo.mp4`.
