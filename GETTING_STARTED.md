# Getting Started — SeaBridge Dashboard

Two ways to use this. Pick based on what you want. **You do NOT need Claude Code,
git, or any special app.**

---

## Option A — Just look at the dashboard (30 seconds, no installs)

The dashboard is a single web page that works on its own (with sample data). The
only thing that won't work this way is the live **Refresh prices** button.

1. Go to the file on GitHub:
   **`seabridge_dashboard_v2.html`** in the repo → click it → click the **Download raw file**
   icon (top-right of the file view, looks like a down-arrow / tray).
2. Find the downloaded file (usually your **Downloads** folder).
3. **Double-click it.** It opens in your browser. Done.

That's the whole dashboard — table, sorting, filters, sector grouping, sidebar.

---

## Option B — Full version with live "Refresh prices"

This needs **Python** (free) running a tiny local server. Then you open one web
address in your browser. No file paths to hunt for.

### 1. Install Python (one time)
- Windows: get it from **https://www.python.org/downloads/** → run the installer →
  **check the box "Add python.exe to PATH"** on the first screen → Install.
- Mac: it's usually already there (`python3`). If not, install from the same site.

### 2. Get the project folder
- On the repo's GitHub page: green **`< > Code`** button → **Download ZIP**.
- **Unzip it** (right-click → Extract All). You'll get a folder like
  `plugins-quickstart` (or `plugins-quickstart-claude-...`).
- Tip: unzip somewhere simple like your Desktop. Avoid moving individual files
  out of the folder — keep the folder as-is.

### 3. Start it
- **Windows:** open the unzipped folder, go into the **`seabridge`** folder, and
  **double-click `run.bat`**. A black window opens and stays open (that's the
  server — leave it running). A browser tab opens at **http://localhost:8787**.
- **Mac/Linux:** open Terminal, then:
  ```bash
  cd path/to/plugins-quickstart/seabridge
  ./run.sh
  ```

### 4. Use it
- The browser tab at **http://localhost:8787** is your dashboard.
- Click **Refresh prices** — you'll see rows flash and weights recalculate.
- To stop: close the black server window (Windows) or press **Ctrl+C** (Mac/Linux).

> Sample vs. real prices: by default it uses **sample** (fake, offline) data so it
> works with zero setup. The numbers swing a lot on purpose. For real prices see
> `seabridge/README.md` (Deploy section) — real data needs internet access to the
> price provider, which is why hosting it (e.g. Vercel) is the eventual path.

---

## If something goes wrong

**I see `>>>` and "SyntaxError"**
You're inside Python's interactive prompt, not a normal terminal. Type `exit()`
and press Enter to leave it. Don't type commands at a `>>>` prompt. Use
`run.bat` (Windows) / `run.sh` (Mac) instead of running `python` by hand.

**"Windows cannot find ...seabridge_dashboard_v2.html"**
You're on an old version of `run.bat`. Re-download the ZIP (Option B step 2) —
the current version opens a web address, not a file, so this can't happen.

**"'python' is not recognized"**
Python isn't installed or wasn't added to PATH. Reinstall it and make sure
**"Add python.exe to PATH"** is checked (Option B step 1). On Mac, try `python3`.

**The browser tab says "can't connect" / nothing loads**
The server window probably closed or didn't start. Make sure the black window
from `run.bat` is still open, then refresh the browser tab.

**GitHub shows "404 - page not found" for a file**
The run scripts live in the **`seabridge/`** folder, e.g.
`seabridge/run.sh` — not at the top level. Navigate into `seabridge` first.

**OneDrive folders**
Files synced under OneDrive work, but if you hit odd permission or path issues,
try unzipping to a plain local folder like `C:\Users\<you>\Desktop\seabridge-app`
instead.

---

## What do I actually need?

| I want to… | I need |
|---|---|
| See the dashboard right now | Just a web browser (Option A) |
| Use live "Refresh prices" | Python + browser (Option B) |
| No installs at all | Host it (see `seabridge/README.md`) or GitHub Codespaces |
| — | **Never** Claude Code, and git is optional |
