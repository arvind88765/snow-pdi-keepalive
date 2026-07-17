# 🔋 PDI Keep-Alive

Never let your ServiceNow PDI hibernate again. Fork it, add 3 secrets, done. Fully automated, zero maintenance, zero cost.

## the problem

Free tier PDIs sleep after a few days of no activity, and waking one back up can take forever. This repo pings your PDI every day using GitHub Actions so it never dies on you. No server needed, no cost, and nobody touches your password except you.

## how it works

A GitHub Action runs once a day, spins up a headless browser (Playwright), logs into your PDI directly, and boom, your instance's activity timer resets. That's the whole trick.

This isn't guesswork either, the login flow was verified against a real captured login session (HAR) from an actual PDI, so it's not some random selectors pulled from thin air. Check `har_recorder.py` if you ever wanna re-verify it yourself, useful if ServiceNow ever changes their login page.

Everything runs inside your own fork using your own GitHub Secrets. Nobody, including me, ever sees your password. It never leaves your repo.

## setup, literally 5 min

1. **Fork this repo.** Top right, hit Fork.

2. Go to **Settings > Secrets and variables > Actions > New repository secret** in your fork and add these 3:

   | Secret | Value |
   |---|---|
   | `PDI_URL` | your instance url, like `https://dev12345.service-now.com` |
   | `PDI_USER` | your PDI username |
   | `PDI_PASS` | your PDI password |

3. Go to the **Actions** tab, enable workflows if it asks.

4. Click **Run workflow** on "PDI Keep-Alive" to test it right now instead of waiting for the schedule.

That's literally it. It runs itself every day forever, for as long as your fork exists. Set it and forget it.

## heads up

- MFA enabled on your PDI? this won't work, gotta disable MFA on the dev instance for this to log in
- want it to run more/less often? edit the `cron` line in `.github/workflows/keepalive.yml`
- this is just automating a normal login, nothing sketchy, no bypassing anything
- pro tip, don't use your main admin creds if you can avoid it, spin up a low priv login just for this

## wanna run it locally first

```bash
cp .env.example .env   # drop your real values in here
pip install -r requirements.txt
playwright install chromium
export $(cat .env | xargs) && python keepalive.py
```

## why fork + Actions instead of some hosted bot

Because nobody has to trust a stranger with their password. Your creds live in your own repo's encrypted secrets, period. This repo is just the automation logic, everyone runs their own copy independently.
