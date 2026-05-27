"""
Source Club — Self-Narrating Demo Builder
==========================================

Produces a finished demo video with a built-in, natural-sounding voiceover — no human
recording needed:

  1. Synthesizes concise narration per step. Default engine is Microsoft Edge neural TTS
     (`edge-tts`, free, no API key, very natural) -> MP3, normalized to WAV via ffmpeg.
     Falls back to offline Windows SAPI if the network is unavailable.
  2. Drives the app in a browser (Playwright), holding each on-screen step exactly as long
     as its narration clip, and records the screen to video.
  3. Assembles one narration track aligned to the *measured* step timings.
  4. Muxes the audio onto the video with ffmpeg (bundled via imageio-ffmpeg).

Output: demo/output/source-club-demo-narrated.webm  (plays with sound; embedded on the
Video Walkthrough page).

USAGE
  pip install -r demo/requirements.txt        # playwright + imageio-ffmpeg + edge-tts
  python -m playwright install chromium
  python demo/record_narrated.py                       # natural neural voice (Andrew)
  python demo/record_narrated.py --voice en-US-AriaNeural   # different neural voice
  python demo/record_narrated.py --engine sapi              # offline robotic fallback
"""

from __future__ import annotations
import argparse, asyncio, os, subprocess, sys, time, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "output")
AUDIO = os.path.join(OUT, "audio")
FINAL = os.path.join(OUT, "source-club-demo-narrated.webm")
FINAL_MP4 = os.path.join(OUT, "source-club-demo-narrated.mp4")  # H.264/AAC — plays inline on GitHub
PORT = 8540
URL = f"http://localhost:{PORT}/"

# Each beat: (action_key, concise narration). Covers Assignments 1, 2 and 3.
BEATS = [
    # ── Assignment 1 — Savings Analysis ──────────────────────────────────────
    ("landing",  "Hi — this is my Source Club case study. I built a working tool for Assignment one and decision docs for two and three. Let me walk you through them."),
    ("page",     "Assignment one — the savings analysis. It's the biggest bottleneck: about ten minutes each, twenty to forty times a month, and it's founder-only, so it caps how fast we can grow. This tool removes that cap."),
    ("samples",  "I upload the prospect's purchase history and our pricing catalog. No API key needed; it's fully deterministic."),
    ("run",      "Matching is the hard part, because suppliers name the same product differently. Three passes: exact SKU, fuzzy text, then optional AI."),
    ("results",  "In seconds: about forty-nine hundred dollars in savings, a seventy-eight percent match rate, and nineteen high-confidence matches. Prices compare per unit, so pack sizes don't skew it."),
    ("review",   "Anything the software isn't sure about drops into a human review queue. It's never auto-trusted."),
    ("unmatched","Items we don't carry are surfaced separately, never force-matched. That's Assignment one."),
    # ── Assignment 2 — Stripe x HubSpot ──────────────────────────────────────
    ("a2_intro", "Assignment two: connecting Stripe and HubSpot. Stripe is billing truth, HubSpot is the CRM, and today they don't talk — so nobody can see billing health on a company without cross-referencing by hand."),
    ("a2_reco",  "I mapped three options — a native integration, a middleware tool, and a custom build — and I recommend n8n: free, self-hosted, and flexible enough to handle multi-location companies, where one company has several Stripe subscriptions."),
    # ── Assignment 3 — Prioritization ────────────────────────────────────────
    ("a3_intro", "Assignment three: prioritizing your real project queue. The question is what to tackle in the first ninety days."),
    ("a3_rank",  "First, automate the savings analysis — highest priority and the founder bottleneck. Then the Stripe-HubSpot name matching, which is foundational for every dashboard. Then customer service into HubSpot, the ZenOne data backbone, and finishing the sales-pipeline automation."),
    ("close",    "The thread across all three: take the founder out of the repeatable revenue paths, then build the data layer that turns everything after it into leverage. Thanks for watching."),
]


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _wav_params(path):
    with wave.open(path, "rb") as w:
        return (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes() / w.getframerate())


def synth_clips(engine: str, voice: str, rate: int):
    os.makedirs(AUDIO, exist_ok=True)
    ff = _ffmpeg()
    clips = []
    for i, (key, text) in enumerate(BEATS):
        wav = os.path.join(AUDIO, f"clip{i}.wav")
        if engine == "edge":
            mp3 = os.path.join(AUDIO, f"clip{i}.mp3")
            asyncio.run(_edge_save(text, voice, mp3))
            subprocess.run([ff, "-y", "-i", mp3, "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", wav],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # sapi
            txt = os.path.join(AUDIO, f"line{i}.txt")
            with open(txt, "w", encoding="utf-8") as f:
                f.write(text)
            ps = ("Add-Type -AssemblyName System.Speech; "
                  "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  f"$s.Rate = {rate}; $s.SetOutputToWaveFile('{wav}'); "
                  f"$t = Get-Content -Raw -Encoding UTF8 '{txt}'; $s.Speak($t); $s.Dispose()")
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        nch, sw, fr, dur = _wav_params(wav)
        clips.append({"key": key, "wav": wav, "dur": dur, "params": (nch, sw, fr)})
        print(f"  TTS beat {i} ({key}): {dur:.1f}s")
    return clips


async def _edge_save(text, voice, mp3):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(mp3)


def start_server():
    env = dict(os.environ); env.pop("ANTHROPIC_API_KEY", None)
    p = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py",
                          "--server.headless", "true", "--server.port", str(PORT)],
                         cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            if urllib.request.urlopen(URL, timeout=2).status == 200:
                return p
        except Exception:
            time.sleep(0.5)
    p.terminate(); raise RuntimeError("Streamlit did not start")


BANNER_JS = """
(text) => { let el=document.getElementById('demo-banner');
  if(!el){el=document.createElement('div');el.id='demo-banner';
    el.style.cssText='position:fixed;left:0;right:0;bottom:0;z-index:2147483647;padding:14px 22px;font:600 18px/1.4 system-ui,Segoe UI,Arial;color:#fff;background:linear-gradient(90deg,#0d3b66,#1d6fb8);box-shadow:0 -2px 12px rgba(0,0,0,.35)';
    document.body.appendChild(el);} el.textContent=text; }
"""


def run_and_record(clips):
    from playwright.sync_api import sync_playwright
    offsets = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, slow_mo=120)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  record_video_dir=OUT, record_video_size={"width": 1440, "height": 900})
        page = ctx.new_page()
        t0 = time.time()

        def beat(i):
            page.evaluate(BANNER_JS, BEATS[i][1])
            offsets.append(time.time() - t0)
            page.wait_for_timeout(int(clips[i]["dur"] * 1000) + 500)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_selector("a[href$='Savings_Analysis']", timeout=30000)
        beat(0)

        lp = page.locator(".st-key-lp button")
        page.goto(URL + "Savings_Analysis", wait_until="domcontentloaded")
        try:
            lp.wait_for(state="visible", timeout=12000)
        except Exception:
            page.click("a[href$='Savings_Analysis']"); lp.wait_for(state="visible", timeout=30000)
        beat(1)

        lp.click(); page.wait_for_timeout(1200)
        lc = page.locator(".st-key-lc button"); lc.wait_for(state="visible", timeout=20000); lc.click()
        page.wait_for_timeout(800)
        beat(2)

        run = page.locator('button:has-text("Run Savings")'); run.wait_for(state="visible", timeout=20000)
        run.click()
        beat(3)

        page.wait_for_selector("text=$4,944", timeout=60000)
        page.get_by_text("📊 Results").scroll_into_view_if_needed()
        beat(4)

        page.get_by_role("tab", name="Needs Review").click(); page.wait_for_timeout(500)
        beat(5)

        page.get_by_role("tab", name="Unmatched").click(); page.wait_for_timeout(500)
        beat(6)

        # ── Assignment 2 — Stripe x HubSpot ──────────────────────────────────
        page.goto(URL + "Stripe_HubSpot", wait_until="domcontentloaded")
        _wait_text(page, "Three Options", "Stripe")
        beat(7)
        page.mouse.wheel(0, 750); page.wait_for_timeout(500)
        beat(8)

        # ── Assignment 3 — Prioritization ────────────────────────────────────
        page.goto(URL + "Prioritization", wait_until="domcontentloaded")
        _wait_text(page, "First 90 days", "Framework")
        beat(9)
        page.mouse.wheel(0, 700); page.wait_for_timeout(500)
        beat(10)
        page.mouse.wheel(0, 700); page.wait_for_timeout(500)
        beat(11)

        page.wait_for_timeout(800)
        video_path = page.video.path()
        ctx.close(); browser.close()
    return video_path, offsets


def _wait_text(page, *phrases):
    """Wait until any of the phrases is visible (doc page rendered); fall back to a short wait."""
    for ph in phrases:
        try:
            page.get_by_text(ph, exact=False).first.wait_for(state="visible", timeout=8000)
            return
        except Exception:
            continue
    page.wait_for_timeout(2500)


def assemble_audio(clips, offsets, out_wav):
    nch, sw, fr = clips[0]["params"]
    end = max(offsets[i] + clips[i]["dur"] for i in range(len(clips))) + 1.0
    total = bytearray(int(end * fr) * sw * nch)
    for i, c in enumerate(clips):
        with wave.open(c["wav"], "rb") as w:
            data = w.readframes(w.getnframes())
        start = int(offsets[i] * fr) * sw * nch
        if start + len(data) > len(total):
            total.extend(b"\x00" * (start + len(data) - len(total)))
        total[start:start + len(data)] = data
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(nch); w.setsampwidth(sw); w.setframerate(fr)
        w.writeframes(bytes(total))
    return end


def mux(video, narr_wav, out, duration):
    ff = _ffmpeg()
    subprocess.run([ff, "-y", "-i", video, "-i", narr_wav,
                    "-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.2f}",
                    "-c:v", "copy", "-c:a", "libopus", "-b:a", "96k", out],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def to_mp4(webm, mp4):
    """H.264/AAC copy for universal playback (GitHub inline, email, any device)."""
    ff = _ffmpeg()
    subprocess.run([ff, "-y", "-i", webm,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", mp4],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["edge", "sapi"], default="edge",
                    help="edge = natural neural TTS (needs network); sapi = offline robotic fallback")
    ap.add_argument("--voice", default="en-US-AndrewNeural", help="edge-tts neural voice name")
    ap.add_argument("--rate", type=int, default=-1, help="SAPI voice rate (-10..10) when --engine sapi")
    args = ap.parse_args()
    try:
        import playwright, imageio_ffmpeg  # noqa
    except ImportError:
        sys.exit("Run: pip install -r demo/requirements.txt && python -m playwright install chromium")

    engine = args.engine
    print(f"Synthesizing narration ({engine}, voice={args.voice if engine=='edge' else 'SAPI'})…")
    try:
        clips = synth_clips(engine, args.voice, args.rate)
    except Exception as e:
        if engine == "edge":
            print(f"  ⚠️  Neural TTS failed ({repr(e)[:120]}); falling back to offline SAPI.")
            engine = "sapi"; clips = synth_clips("sapi", args.voice, args.rate)
        else:
            raise

    print("Starting app + recording the narrated run…")
    srv = start_server()
    try:
        video, offsets = run_and_record(clips)
    finally:
        srv.terminate()

    print("Assembling aligned narration track…")
    narr = os.path.join(AUDIO, "narration.wav")
    dur = assemble_audio(clips, offsets, narr)
    print("Muxing audio into video…")
    mux(video, narr, FINAL, dur)
    print("Encoding MP4 (H.264/AAC) for universal playback…")
    to_mp4(FINAL, FINAL_MP4)
    try:
        os.remove(video)
    except OSError:
        pass
    # tidy temp clips
    for f in os.listdir(AUDIO):
        try: os.remove(os.path.join(AUDIO, f))
        except OSError: pass
    try: os.rmdir(AUDIO)
    except OSError: pass
    print(f"\n🎬 Narrated demo saved:\n  {FINAL}\n  {FINAL_MP4}  (voice: {args.voice if engine=='edge' else 'SAPI'})")


if __name__ == "__main__":
    main()
