# START HERE — Earnings Revision Agent

A walkthrough for getting this project running in VS Code, written for someone who has never used Python. Budget about an hour. Do the parts in order; each one ends with a way to check it worked.

**What you'll have at the end:** an app in your browser where you pick a company, it pulls that company's latest earnings press release from the SEC, Claude reads it, and the agent recommends whether to revise your estimates, with the evidence for you to approve or reject. For how it all works, read `docs/PROJECT_GUIDE.md` afterwards.

---

## Three words you need first

| Word | What it means |
|---|---|
| **Python** | The language the project is written in. Files ending in `.py` are Python. |
| **VS Code** | The app you write and run code in. Think of it as Word, for code. |
| **Terminal** | A box at the bottom of VS Code where you type commands instead of clicking buttons. Type a command, press Enter, read what comes back. |

---

## Part 1 — Install the two programs (10 min)

1. **Python.** Go to [python.org/downloads](https://www.python.org/downloads/) and download the current version. Run the installer.
   - **Windows only:** on the first installer screen, tick **"Add python.exe to PATH"** before clicking Install. This is the #1 thing people miss.
2. **VS Code.** Go to [code.visualstudio.com](https://code.visualstudio.com/) and install it with the default options.

## Part 2 — Open the project in VS Code (5 min)

1. Unzip `earnings-agent.zip`. Move the `earnings-agent` folder somewhere you'll find it again, like Documents.
2. Open VS Code. Choose **File → Open Folder…** and pick the `earnings-agent` folder (the folder itself, not a file inside it). If asked "Do you trust the authors?", click **Yes**.
3. Install the Python add-on: click the **Extensions** icon in the left bar (four squares), search for **Python**, and install the one by Microsoft.

**Check:** the left panel lists files such as `app.py`, `START_HERE.md`, and a folder called `agent`.

## Part 3 — Create the project's private workspace (5 min)

Python projects each get their own "virtual environment": a private folder (named `.venv`) holding the add-on packages this project needs, kept separate from everything else on your computer.

1. Press **Ctrl+Shift+P** (Mac: **Cmd+Shift+P**). A search bar opens at the top.
2. Type `Python: Create Environment` and press Enter.
3. Choose **Venv**.
4. Choose the Python version you just installed.
5. When it asks about dependencies, **tick `requirements.txt`** and click OK.
6. Wait a minute or two while it downloads the packages (bottom-right shows progress).

**Check:** a `.venv` folder appears in the left panel.

<details>
<summary>If that menu didn't work, do it by hand</summary>

Open a terminal (**Terminal → New Terminal**) and type these one at a time, pressing Enter after each.

Mac:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Windows says "running scripts is disabled"? Click the small arrow next to the **+** at the top right of the terminal, choose **Command Prompt**, and run the last two lines again there.
</details>

## Part 4 — Tell the SEC who you are (3 min)

The SEC lets anyone download filings for free, but asks every program to send a name and email.

1. In the left panel, right-click `.env.example` → **Copy**, then right-click the empty space below the files → **Paste**.
2. Right-click the copy → **Rename** → name it exactly `.env`
3. Open `.env` and change the first line to your own name and email, for example:
   ```
   SEC_USER_AGENT=Jane Doe jane@andrew.cmu.edu
   ```
4. Save with **Ctrl+S** (Mac: **Cmd+S**).

`.env` is where private settings live. It is deliberately excluded from anything you share or upload.

## Part 5 — Run your first three commands (10 min)

Open a fresh terminal: **Terminal → New Terminal**. The line you type on should start with `(.venv)`. If it doesn't, close that terminal (trash-can icon) and open a new one.

**Command 1 — check your setup**
```
python step1_check_setup.py
```
You want every line to say `[OK]`. Any `[FIX]` line tells you what to do.

**Command 2 — download a real earnings release**
```
python step2_fetch_release.py AAPL
```
It looks up Apple at the SEC, lists its recent earnings announcements, downloads the newest press release, and prints the first 40 lines. A copy is saved in `data/releases/`. Try another ticker in place of `AAPL`.

**Command 3 — open the app**
```
streamlit run app.py
```
Your browser opens the app. (The first time, Streamlit may ask for an email in the terminal; just press Enter to skip.) To stop the app, click in the terminal and press **Ctrl+C**.

## Part 6 — Give the agent its AI (10 min)

The agent uses Claude to read each release. That needs an API key: a password that lets your code call Claude. It is separate from a Claude chat subscription and is paid by usage; one run of this agent costs a few cents.

1. Go to the Claude Console at [platform.claude.com](https://platform.claude.com) and sign in or create an account.
2. Add a small amount of credit under Billing (a few dollars covers the whole project).
3. Open **Settings → API keys**, create a key, and copy it. It starts with `sk-ant-`. You only see it once.
4. Open your `.env` file and paste it after `ANTHROPIC_API_KEY=` with no spaces or quotes. Save.

Treat the key like a password: never paste it into code, a chat, or a shared document. Each teammate should use their own.

**Command 4 — run the agent on the practice release**
```
python step3_run_agent.py --sample
```
It reads a made-up company's release and prints a full analyst note ending in a recommendation. You should see **REVISE UP**.

**Command 5 — run it on a real company**
```
python step3_run_agent.py AAPL
```
Until you add rows for that company and quarter to `estimates.csv`, the answer will be NEEDS REVIEW with the reason "no estimates on file". That is the agent working correctly.

**Command 6 — do the same thing in the app**
```
streamlit run app.py
```
Choose **Practice / red-team file** on the left, load the sample, click **Run the agent on this release**, and look through the evidence. At the bottom you'll see next quarter's estimates the agent proposes. Change one if you like, then approve.

**Command 7 — pull Wall Street consensus for a real company**
```
python step4_pull_consensus.py AAPL
```
It downloads analysts' consensus EPS and revenue from Yahoo Finance (free, no key needed) and copies it into `estimates.csv` wherever you don't already have a number. It never overwrites your estimates. Read section 6.1 of `docs/PROJECT_GUIDE.md` before relying on these numbers; it explains two traps.

---

## What each file is

| File or folder | What it's for | Will you edit it? |
|---|---|---|
| `START_HERE.md` | This guide | No |
| `docs/PROJECT_GUIDE.md` | The full explanation of the project and every part of it | Read it |
| `companies.csv` | The companies the agent covers | **Yes** — your team's final list |
| `estimates.csv` | Your team's own estimates ("the book") | **Yes** — seed from consensus, then it grows as you approve revisions |
| `data/consensus.csv` | Every consensus number pulled, and when | No — it's a record |
| `eval/labels.csv` | Your hand-made answer key | **Yes** |
| `.env` | Your private settings and keys | Twice |
| `app.py` | The visual app | Later |
| `step1_…`, `step2_…`, `step3_…` | The commands above | No |
| `agent/` | The agent itself, one file per job | Later, with Claude Code |
| `prompts/` | The instructions Claude is given | Yes, when tuning |
| `samples/`, `redteam/` | Practice and attack files (made-up company) | Add your own attacks |
| `tests/` | Automatic checks; run them by typing `pytest` | Later |
| `CLAUDE.md`, `.claude/skills/` | Ground rules and ready-made workflows for Claude Code | Rarely |
| `docs/` | Failure log, AI use log, finance background | **Yes** — keep the logs current |

Open any `.csv` file in VS Code and edit it like text: one row per line, commas between columns. Open any `.py` file to read it; the comments (lines starting with `#` or wrapped in `"""`) explain what the code does in plain English.

---

## When something goes wrong

| What you see | What to do |
|---|---|
| `python is not recognized` / `command not found: python` | The terminal isn't using `.venv`. Open a new terminal and look for `(.venv)`. On Windows, if it still fails, reinstall Python with "Add to PATH" ticked. |
| `ModuleNotFoundError: No module named …` | Packages aren't installed in this environment. Run `pip install -r requirements.txt`. |
| `No ANTHROPIC_API_KEY found` / `Claude rejected the API key` | Redo Part 6. The key goes in `.env`, right after the `=`, with no spaces. |
| `No SEC_USER_AGENT found` | Redo Part 4. The file must be named `.env` exactly, with nothing before the dot. |
| `The SEC refused the request (error 403)` | Your `.env` line needs a real name and email. |
| The release shown is the wrong document | Companies name their files differently, and the code makes a best guess. Write down the ticker and date: it's a real entry for your "where it breaks" log. |
| Anything else in red | Copy the whole red message and paste it to Claude. Error messages look scary and are usually one small fix. |

---

## Your to-do list

- [ ] Get all seven commands working (each teammate, on their own laptop)
- [ ] Agree on the final company list and update `companies.csv`
- [ ] Run `step2_fetch_release.py` for every company; note any that pull the wrong document
- [ ] Pull consensus for every company (`python step4_pull_consensus.py --all`), check it, and fill in the three metrics consensus doesn't cover
- [ ] Time yourself doing 2–3 earnings updates by hand (your "before" number)
- [ ] Build the answer key in `eval/labels.csv` **before** running the agent on those releases
- [ ] Run `python eval/run_backtest.py` and record the results
- [ ] Try to break it with the files in `redteam/`, then write your own
- [ ] Log every failure in `docs/failure_log.md` and every use of AI in `docs/ai_use_log.md`
