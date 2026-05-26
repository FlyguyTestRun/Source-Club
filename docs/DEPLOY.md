# Deploying the Savings Analyzer (free, no Streamlit Cloud)

Both options host the **same app** — no rebuild. The repo
(`https://github.com/FlyguyTestRun/Source-Club`) is already public.

---

## Option A — Render (recommended; uses your existing GitHub repo)

Render's GitHub connection is separate from Streamlit's, so it sidesteps the
Streamlit↔GitHub trouble. The repo already includes `render.yaml`, so it's basically one click.

1. Go to **https://render.com** → sign up (free, no card) → authorize GitHub when asked.
2. Click **New +** → **Blueprint**.
3. Select the **`Source-Club`** repo → Render reads `render.yaml` → **Apply**.
4. Wait ~3–5 min for the first build. You'll get a public URL like
   **`https://source-club-savings.onrender.com`** — that's your Assignment 1 link.

> Free instances sleep after ~15 min idle, so the first hit after a nap takes ~30–50s to wake.
> Fine for a reviewer; just open it once before you send the email so it's warm.

**Optional AI pass:** in the Render dashboard → your service → **Environment** → add
`ANTHROPIC_API_KEY`. Skip it and the app runs the deterministic fuzzy demo ($4,944).

---

## Option B — Hugging Face Spaces (no GitHub needed at all)

Best if the GitHub connection keeps failing. HF hosts Streamlit natively and you push to
*their* git (a Hugging Face token, not GitHub).

1. Go to **https://huggingface.co** → create a free account.
2. **New → Space** → name it (e.g. `source-club`) → **SDK: Streamlit** → **Free CPU** → Create.
3. At the top of this repo's `README.md`, add this front matter (HF reads it):
   ```
   ---
   title: Source Club Savings Analyzer
   emoji: 🦷
   colorFrom: blue
   colorTo: indigo
   sdk: streamlit
   app_file: app.py
   pinned: false
   ---
   ```
4. Push this repo to the Space's git remote (replace `<user>`/`<space>`):
   ```bash
   git remote add hf https://huggingface.co/spaces/<user>/<space>
   git push hf main
   ```
   When prompted, username = your HF username, password = an HF **access token**
   (huggingface.co → Settings → Access Tokens → New token, "write").
5. The Space builds automatically and serves at
   **`https://huggingface.co/spaces/<user>/<space>`** — your Assignment 1 link.

> No `git` at all? On the Space's **Files** tab you can upload files in the browser instead —
> just preserve the folder layout (`app.py`, `requirements.txt`, `pages/`, `assignment-1-savings-analysis/`).

---

## Sanity check (either option)
Open the URL → sidebar **💰 Savings Analysis** → **Load sample** ×2 → **Run** →
confirm **$4,944 / 78.6%**. Done.
