# PDI Keep-Alive

Stop your ServiceNow **PDI (Personal Developer Instance)** from hibernating.

Free-tier PDIs auto-sleep after a few days of inactivity, and waking one back up
can take a long time. This repo pings your PDI on a schedule using GitHub
Actions so you never lose it — **no server, no cost, no shared credentials.**

## How it works

A GitHub Actions workflow runs **once a day**, launches a headless browser
(Playwright), and logs into your PDI directly (not via the developer portal —
straight to `https://devXXXXX.service-now.com/`, which uses a simple login
form, not Okta/SSO). That's it — your instance's activity timer resets and
it stays awake.

This login flow was verified against a real captured HAR of an actual PDI
login, not guessed — see `har_recorder.py` if you ever need to re-verify it
against your own instance (e.g. if ServiceNow changes their login page).

Everything runs **inside your own fork**, using **your own GitHub Secrets**.
Nobody (including the repo author) ever sees your PDI credentials.

## Setup (5 minutes, one-time)

1. **Fork this repo** (top right → Fork).

2. In your fork, go to **Settings → Secrets and variables → Actions → New repository secret**
   and add these three secrets:

   | Secret name | Value |
   |---|---|
   | `PDI_URL`  | Your instance URL, e.g. `https://dev12345.service-now.com` |
   | `PDI_USER` | Your PDI login username |
   | `PDI_PASS` | Your PDI login password |

3. Go to the **Actions** tab of your fork and enable workflows if prompted.

4. (Optional) Click **Run workflow** on the `PDI Keep-Alive` workflow to test it immediately.

That's it. It'll now run automatically every 2 days for as long as your fork exists.

## Notes / limitations

- If your PDI has MFA enabled, this script won't be able to log in — disable MFA on the dev instance, or adjust the script.
- Adjust the schedule in `.github/workflows/keepalive.yml` (the `cron` line) if you want it to run more/less often.
- This automates a normal login — nothing exploits or bypasses ServiceNow security.
- Consider using a low-privilege PDI login rather than your main admin account, just as good practice.

## Run it locally (optional)

```bash
cp .env.example .env   # fill in your values
pip install -r requirements.txt
playwright install chromium
export $(cat .env | xargs) && python keepalive.py
```

## Why GitHub Actions instead of a hosted service?

Because nobody has to trust anyone else with their password. Every user's
credentials live only in their own repo's encrypted Secrets store — this repo
is just the automation logic, forked and run independently by each person.
