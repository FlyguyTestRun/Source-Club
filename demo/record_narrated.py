"""
Source Club — Self-Narrating Demo Builder
==========================================

Produces a finished demo video with a built-in voiceover — no human recording needed:

  1. Synthesizes concise narration per step with Windows SAPI (offline TTS) -> WAV clips.
  2. Drives the app in a browser (Playwright), holding each on-screen step exactly as long
     as its narration clip, and records the screen to video.
  3. Assembles one narration track aligned to the *measured* step timings.
  4. Muxes the audio onto the video with ffmpeg (bundled via imageio-ffmpeg).

Output: demo/output/source-club-demo-narrated.webm  (plays with sound; embedded on the
Video Walkthrough page).

USAGE
  pip install -r demo/requirements.txt        # playwright + imageio-ffmpeg
  python -m playwright install chromium
  python demo/record_narrated.py              # builds the narrated video
  python demo/record_narrated.py --rate -2    # slower SAPI voice (-10..10)
"""

from __future__ import annotations
import argparse, os, subprocess, sys, time, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "output")
AUDIO = os.path.join(OUT, "audio")
FINAL = os.path.join(OUT, "source-club-demo-narrated.webm")
PORT = 8540
URL = f"http://localhost:{PORT}/"

# Each beat: (action_key, concise narration). Business-case-first.
BEATS = [
    ("landing",  "Source Club's biggest bottleneck is the savings analysis. Every prospect needs one before they sign, and today the founder does each one by hand."),
    ("page",     "It's about ten minutes each, twenty to forty times a month. And it's founder-only, so it caps how fast we can grow. This tool removes that cap."),
    ("samples",  "I upload the prospect's purchase history and our pricing catalog. No API key needed; it's fully deterministic."),
    ("run",      "Matching is the hard part, because suppliers name the same product differently. Three passes: exact SKU, fuzzy text, then optional A I."),
    ("results",  "In seconds: about forty-nine hundred dollars in savings, a seventy-eight percent match rate, nineteen high-confidence matches. Prices compare per unit, so pack sizes don't skew it."),
    ("review",   "Anything the software isn't sure about drops into a human review queue. It's never auto-trusted."),
    ("unmatched","Items we don't carry are surfaced separately, never force-matched."),
    ("close",    "One deliberate call: I left the A I vendor open, because it depends on the cloud platform. The goal is simple: take the founder out of this repeatable step entirely."),
]


def synth_clips(rate: int):
    os.makedirs(AUDIO, exist_ok=True)
    clips = []
    for i, (key, text) in enumerate(BEATS):
        txt = os.path.join(AUDIO, f"line{i}.txt")
        wav = os.path.join(AUDIO, f"clip{i}.wav")
        with open(txt, "w", encoding="utf-8") as f:
            f.write(text)
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Rate = {rate}; "
            f"$s.SetOutputToWaveFile('{wav}'); "
            f"$t = Get-Content -Raw -Encoding UTF8 '{txt}'; "
            "$s.Speak($t); $s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with wave.open(wav, "rb") as w:
            dur = w.getnframes() / w.getframerate()
            params = (w.getnchannels(), w.getsampwidth(), w.getframerate())
        clips.append({"key": key, "wav": wav, "dur": dur, "params": params})
        print(f"  TTS beat {i} ({key}): {dur:.1f}s")
    return clips


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
        beat(0)  # landing

        lp = page.locator(".st-key-lp button")
        page.goto(URL + "Savings_Analysis", wait_until="domcontentloaded")
        try:
            lp.wait_for(state="visible", timeout=12000)
        except Exception:
            page.click("a[href$='Savings_Analysis']"); lp.wait_for(state="visible", timeout=30000)
        beat(1)  # page / uploaders

        lp.click(); page.wait_for_timeout(1200)
        lc = page.locator(".st-key-lc button"); lc.wait_for(state="visible", timeout=20000); lc.click()
        page.wait_for_timeout(800)
        beat(2)  # samples loaded

        run = page.locator('button:has-text("Run Savings")'); run.wait_for(state="visible", timeout=20000)
        run.click()
        beat(3)  # running (narration plays over the spinner)

        page.wait_for_selector("text=$4,944", timeout=60000)
        page.get_by_text("📊 Results").scroll_into_view_if_needed()
        beat(4)  # results

        page.get_by_role("tab", name="Needs Review").click(); page.wait_for_timeout(500)
        beat(5)  # review

        page.get_by_role("tab", name="Unmatched").click(); page.wait_for_timeout(500)
        beat(6)  # unmatched

        page.get_by_role("tab", name="All Results").click(); page.wait_for_timeout(500)
        beat(7)  # close

        page.wait_for_timeout(800)
        video_path = page.video.path()
        ctx.close(); browser.close()
    return video_path, offsets


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


def mux(video, narr_wav, out):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-i", video, "-i", narr_wav,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "libopus", "-b:a", "96k", out],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=int, default=-1, help="SAPI voice rate (-10..10); slower = clearer")
    args = ap.parse_args()
    try:
        import playwright, imageio_ffmpeg  # noqa
    except ImportError:
        sys.exit("Run: pip install -r demo/requirements.txt && python -m playwright install chromium")

    print("Synthesizing narration (offline SAPI)…")
    clips = synth_clips(args.rate)
    print("Starting app + recording the narrated run…")
    srv = start_server()
    try:
        video, offsets = run_and_record(clips)
    finally:
        srv.terminate()
    print("Assembling aligned narration track…")
    narr = os.path.join(AUDIO, "narration.wav")
    assemble_audio(clips, offsets, narr)
    print("Muxing audio into video…")
    mux(video, narr, FINAL)
    try:
        os.remove(video)
    except OSError:
        pass
    print(f"\n🎬 Narrated demo saved: {FINAL}")


if __name__ == "__main__":
    main()
