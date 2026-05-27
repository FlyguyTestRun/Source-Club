"""
Source Club — Auto Demo & Recorder
===================================

Drives the running Streamlit app inside its OWN browser window and (optionally)
records the whole thing to a video file. It uses Playwright, which controls a
separate browser instance — your real mouse and keyboard are never touched, so
you can keep working (or just watch it play) while it runs.

What it does, hands-free:
  1. (optionally) starts the Streamlit app
  2. opens the landing page, then the Savings Analysis page
  3. loads the sample prospect + catalog files
  4. runs the 3-pass matching pipeline
  5. walks the results (savings figure, confidence tiers, review/unmatched tabs)
  6. saves a video to demo/output/source-club-demo.webm

On-screen captions narrate each step, so the recording explains itself — good
for dropping straight into the Assignment 4 video page.

USAGE
  pip install -r demo/requirements.txt
  python -m playwright install chromium
  python demo/record_demo.py                 # auto-starts app, headed, records (with captions)
  python demo/record_demo.py --voiceover     # clean run to narrate over (captions off, slow pace)
  python demo/record_demo.py --headless      # no visible window (CI / fast)
  python demo/record_demo.py --no-record      # just watch, don't save a video
  python demo/record_demo.py --no-start-server  # attach to an app you already run
  python demo/record_demo.py --use-ai         # turn on the Claude pass (needs .env key)
  python demo/record_demo.py --hold-scale 2   # slow every pause down 2x

VOICEOVER WORKFLOW
  Run `python demo/record_demo.py --voiceover` and read demo/voiceover-script.md aloud as the
  browser drives itself. The captions are hidden so your narration carries the story. The pacing is
  tuned (~2.2x holds) to give you time to speak each line; use --hold-scale to go slower/faster.

The deterministic demo runs in fuzzy-only mode (no API key needed) and always
produces the same $4,944 / 78.6% result. --use-ai additionally exercises Pass 3.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
OUTPUT_DIR = os.path.join(HERE, "output")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "source-club-demo.webm")


# ── helpers ───────────────────────────────────────────────────────────────────
def _server_up(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def start_server(port: int, use_ai: bool) -> subprocess.Popen:
    env = dict(os.environ)
    if not use_ai:
        # Force fuzzy-only so the demo is deterministic even if a key is present.
        env.pop("ANTHROPIC_API_KEY", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.headless", "true", "--server.port", str(port)],
        cwd=REPO_ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://localhost:{port}/"
    for _ in range(60):
        if _server_up(url):
            return proc
        time.sleep(0.5)
    proc.terminate()
    raise RuntimeError(f"Streamlit did not come up on {url} within 30s")


# A body-level caption banner, injected so it survives Streamlit's reruns.
_BANNER_JS = """
(text) => {
  let el = document.getElementById('demo-banner');
  if (!el) {
    el = document.createElement('div');
    el.id = 'demo-banner';
    el.style.cssText = [
      'position:fixed','left:0','right:0','bottom:0','z-index:2147483647',
      'padding:14px 22px','font:600 18px/1.4 system-ui,Segoe UI,Arial',
      'color:#fff','background:linear-gradient(90deg,#0d3b66,#1d6fb8)',
      'box-shadow:0 -2px 12px rgba(0,0,0,.35)','letter-spacing:.2px',
    ].join(';');
    document.body.appendChild(el);
  }
  el.textContent = text;
}
"""


def make_narrator(page, captions: bool = True, hold_scale: float = 1.0):
    def narrate(text: str, hold: float = 2.4):
        if captions:
            page.evaluate(_BANNER_JS, text)
        print(f"  • {text}")
        page.wait_for_timeout(int(hold * hold_scale * 1000))
    return narrate


def run_demo(page, base_url: str, use_ai: bool, *, captions: bool = True, hold_scale: float = 1.0):
    narrate = make_narrator(page, captions=captions, hold_scale=hold_scale)

    page.goto(base_url, wait_until="domcontentloaded")
    page.wait_for_selector("a[href$='Savings_Analysis']", timeout=30000)
    narrate("Source Club case study — one app, four deliverables. Opening the live tool…")

    # Navigate straight to the Savings Analysis page by URL. This is deterministic
    # (no dependence on a sidebar click landing mid-rerun). Fall back to the nav
    # link if the URL slug doesn't resolve, then wait for the page to actually render.
    lp = page.locator(".st-key-lp button")
    page.goto(base_url.rstrip("/") + "/Savings_Analysis", wait_until="domcontentloaded")
    try:
        lp.wait_for(state="visible", timeout=12000)
    except Exception:
        page.click("a[href$='Savings_Analysis']")
        lp.wait_for(state="visible", timeout=30000)
    narrate("Assignment 1: upload a prospect's purchase history + the Source Club catalog.")

    # Load both sample files. A short settle between clicks lets the first
    # Streamlit rerun finish before the second click, avoiding a click/rerun race.
    lp.click()
    page.wait_for_timeout(1200)
    lc = page.locator(".st-key-lc button")
    lc.wait_for(state="visible", timeout=20000)
    lc.click()
    narrate("Sample prospect file + catalog loaded — no API key required for this demo.")

    # The Run button only appears once both files are present; wait for it.
    run_btn = page.locator('button:has-text("Run Savings")')
    run_btn.wait_for(state="visible", timeout=20000)
    run_btn.click()
    narrate("Running the 3-pass pipeline: exact SKU → fuzzy description → (optional) Claude AI…", hold=1.5)

    page.wait_for_selector("text=$4,944", timeout=60000)
    narrate("Result: ~$4,944/yr in savings at a 78.6% match rate — 19 HIGH-confidence matches.", hold=3.0)

    # Walk the result tabs.
    for tab, caption in [
        ("Needs Review", "MEDIUM/LOW matches drop into a human review queue — not auto-trusted."),
        ("Unmatched", "Items Source Club doesn't carry are surfaced separately, never force-matched."),
        ("All Results", "Per-unit pricing ('Their $/unit' vs 'SC $/unit') handles different pack sizes correctly."),
    ]:
        try:
            page.get_by_role("tab", name=tab).click()
            narrate(caption, hold=2.8)
        except Exception:
            pass

    page.mouse.wheel(0, 600)
    narrate("Full report downloads as CSV. The founder-only bottleneck (5–7+ hrs/month) is removed.", hold=3.0)
    if use_ai:
        narrate("AI pass was ON — Pass 3 resolves ambiguous rows fuzzy matching can't.", hold=2.5)


def main():
    ap = argparse.ArgumentParser(description="Auto-run + record the Source Club savings demo.")
    ap.add_argument("--port", type=int, default=8501)
    ap.add_argument("--headless", action="store_true", help="run without a visible browser window")
    ap.add_argument("--no-record", dest="record", action="store_false", help="don't save a video")
    ap.add_argument("--no-start-server", dest="start_server", action="store_false",
                    help="attach to an already-running app instead of launching one")
    ap.add_argument("--use-ai", action="store_true", help="enable the Claude AI pass (needs ANTHROPIC_API_KEY)")
    ap.add_argument("--slow-mo", type=int, default=350, help="ms delay between actions (watchable pacing)")
    ap.add_argument("--voiceover", action="store_true",
                    help="record a clean run for narrating over: hides the on-screen captions and "
                         "slows pacing so you can read demo/voiceover-script.md aloud")
    ap.add_argument("--hold-scale", type=float, default=None,
                    help="multiply every step's pause (e.g. 1.6 = slower). Defaults to 1.0, or 1.7 with --voiceover")
    args = ap.parse_args()

    captions = not args.voiceover
    hold_scale = args.hold_scale if args.hold_scale is not None else (2.2 if args.voiceover else 1.0)
    if args.voiceover and args.slow_mo == 350:
        args.slow_mo = 550  # smoother visuals for narration unless overridden

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright not installed. Run:\n"
                 "  pip install -r demo/requirements.txt\n"
                 "  python -m playwright install chromium")

    base_url = f"http://localhost:{args.port}/"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    server = None
    if args.start_server and not _server_up(base_url):
        print(f"Starting Streamlit on {base_url} …")
        server = start_server(args.port, args.use_ai)
    elif not _server_up(base_url):
        sys.exit(f"No app running at {base_url} and --no-start-server was set.")

    print("Launching demo browser (your real mouse is NOT used)…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless, slow_mo=args.slow_mo)
        ctx_kwargs = {"viewport": {"width": 1440, "height": 900}}
        if args.record:
            ctx_kwargs["record_video_dir"] = OUTPUT_DIR
            ctx_kwargs["record_video_size"] = {"width": 1440, "height": 900}
        context = browser.new_context(**ctx_kwargs)
        page = context.new_page()

        ok = True
        try:
            run_demo(page, base_url, args.use_ai, captions=captions, hold_scale=hold_scale)
        except Exception as e:
            ok = False
            print(f"\n⚠️  Demo step failed: {e}")
        finally:
            video = page.video.path() if (args.record and page.video) else None
            context.close()   # flushes the video file
            browser.close()

        if args.record and video and os.path.exists(video):
            shutil.move(video, FINAL_VIDEO)
            print(f"\n🎥 Recording saved: {FINAL_VIDEO}")
        elif args.record:
            print("\n⚠️  No video file was produced.")

    if server:
        server.terminate()
        try:
            server.wait(timeout=10)
        except Exception:
            server.kill()

    print("Done." if ok else "Finished with errors (see above).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
