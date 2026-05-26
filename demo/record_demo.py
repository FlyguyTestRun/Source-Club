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
  python demo/record_demo.py                 # auto-starts app, headed, records
  python demo/record_demo.py --headless      # no visible window (CI / fast)
  python demo/record_demo.py --no-record      # just watch, don't save a video
  python demo/record_demo.py --no-start-server  # attach to an app you already run
  python demo/record_demo.py --use-ai         # turn on the Claude pass (needs .env key)

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


def make_narrator(page):
    def narrate(text: str, hold: float = 2.4):
        page.evaluate(_BANNER_JS, text)
        print(f"  • {text}")
        page.wait_for_timeout(int(hold * 1000))
    return narrate


def run_demo(page, base_url: str, use_ai: bool):
    narrate = make_narrator(page)

    page.goto(base_url, wait_until="domcontentloaded")
    page.wait_for_selector("a[href$='Savings_Analysis']", timeout=30000)
    narrate("Source Club case study — one app, four deliverables. Opening the live tool…")

    page.click("a[href$='Savings_Analysis']")
    page.wait_for_selector("text=Assignment 1", timeout=30000)
    narrate("Assignment 1: upload a prospect's purchase history + the Source Club catalog.")

    # Load both sample files. A short settle between clicks lets the first
    # Streamlit rerun finish before the second click, avoiding a click/rerun race.
    page.locator(".st-key-lp button").click()
    page.wait_for_timeout(1200)
    page.locator(".st-key-lc button").click()
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
    args = ap.parse_args()

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
            run_demo(page, base_url, args.use_ai)
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
