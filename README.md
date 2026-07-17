# 🔋 PDI Keep-Alive

Never let your ServiceNow PDI hibernate again. Fork it, add 3 secrets, done. Fully automated, zero maintenance, zero cost.

## the problem

Free tier PDIs sleep after a few days of no activity, and waking one back up can take forever. This repo pings your PDI every day using GitHub Actions so it never dies on you. No server needed, no cost, and nobody touches your password except you.

## how it works

A GitHub Action runs once a day, spins up a headless browser (Playwright), logs into your PDI directly, and boom, your instance's activity timer resets. That's the whole trick.

This isn't guesswork either, the login flow is verified and tested against a real PDI login, not some random selectors pulled from thin air.

Everything runs inside your own fork using your own GitHub Secrets. Nobody, including me, ever sees your password. It never leaves your repo.

## setup, literally 5 min

1. **Fork this repo.** Top right, hit Fork.

2. Go to **Settings > Secrets and variables > Actions > New repository secret** in your fork and add these 3:

   | Secret | Value |
   |---|---|
   | `PDI_URL` | your instance url, like `https://dev12345.service-now.com` |
   | `PDI_USER` | your PDI username |
   | `PDI_PASS` | your PDI password |

3. Go to your fork's [**Actions** tab](../../actions), enable workflows if it asks.

4. Click **Run workflow** on "PDI Keep-Alive" to test it right now instead of waiting for the schedule.

That's literally it. It runs itself every day forever, for as long as your fork exists. Set it and forget it.

## how to check it actually worked

Every run saves 5 screenshots showing exactly what happened, step by step. Here's how to find them:

1. Go to your fork's [**Actions** tab](../../actions)
2. Click into the run you wanna check (top one is the latest)
3. Scroll down to the bottom of that page, past the job logs, to a section called **Artifacts**
4. Click **keepalive-proof-X** to download it, it's a zip
5. Unzip it, you'll get 5 png's:
   - `1_initial_page.png` - what it saw when it opened your PDI
   - `2_after_wake_attempt.png` - after trying to wake it up if it was hibernating
   - `3_form_filled.png` - login form right before hitting submit
   - `4_after_submit.png` - right after clicking login
   - `5_final_landed_page.png` - the actual logged in page, this is your proof it worked

if it failed instead, you'll see `5_login_failed.png` instead of the final one, open that one to see exactly what went wrong

heads up, these auto delete after 3 days to keep things clean, so download the zip if you wanna keep proof long term

also check the logs themselves while you're in there, expand "Run keep-alive script" step, look for `[SUCCESS] Logged in.` at the bottom, that's the real confirmation

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
