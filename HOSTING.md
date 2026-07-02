# Hosting the SeaBridge Dashboard (get a bookmarkable link)

Goal: a permanent web link — `https://something.onrender.com` — that shows the
dashboard **and** has the live **Refresh prices** button working, with no Python
or downloads on your machine. Works from any device, including a locked-down
work laptop.

We use **Render** (free tier) because it runs the project's already-tested
server directly. The one thing only *you* can do is the sign-in + click-deploy,
because it uses your GitHub account — I can't do that part from here. Everything
else is already set up in the repo (`render.yaml`).

---

## Deploy in ~5 clicks

1. Go to **https://render.com** and **Sign up with GitHub** (free, no credit card
   for the free tier).
2. Click **New +** (top right) → **Blueprint**.
3. **Connect your GitHub** if asked, then pick the repository **`plugins-quickstart`**.
4. When it asks which **branch**, choose **`claude/seabridge-portfolio-dashboard-gfs7lh`**
   (that's where this code lives right now).
   - *Or*, if you've merged PR #1 into `main`, just leave it on `main`.
5. Render reads `render.yaml` and shows a service named **seabridge-dashboard**.
   Click **Apply** / **Create**.
6. Wait ~2–3 minutes for the first build. When it's done, Render shows a URL like
   **`https://seabridge-dashboard-xxxx.onrender.com`** — **that's your link.**
   Open it, bookmark it, click **Refresh prices**.

That's it. Any time I push updates to the branch, Render redeploys automatically.

---

## Good to know

- **First load after idle is slow.** On the free tier the service "sleeps" after
  ~15 min of no traffic and takes ~30–60 sec to wake on the next visit. Normal;
  just wait for the first load. (A paid Render plan removes the sleep.)
- **Live prices** come from yfinance (Yahoo) by default — fine for a personal
  daily refresh, but it's an unofficial feed with no guarantees. To switch to
  offline sample data, in the Render dashboard set the env var
  `PRICE_PROVIDER=sample`. (The long-term "real" source is the FactSet MCP path —
  see `seabridge/README.md`.)
- **Ticker format:** the dashboard sends Yahoo-style symbols (e.g. `BRK-B`);
  most tickers work as-is. A few odd ones may show in the response's `errors`
  without breaking the rest.
- **Security:** the link is public but unguessable. It's sample/demo data by
  design. Don't put anything confidential in the sample data, and if you later
  wire in real holdings, add auth or keep the URL private.

---

## Alternatives (if you prefer)

- **Vercel** — the repo also includes a serverless setup under `seabridge/`
  (`vercel.json` + `api/prices.py`). Vercel doesn't "sleep," but the Python
  function setup is a bit more finicky than Render's run-the-server approach.
- **Run locally instead** — see `GETTING_STARTED.md` (needs Python on your
  machine).
- **Just view the design** — download `seabridge_dashboard_v2.html` and open it;
  works offline with sample data, no link needed (no live refresh).
