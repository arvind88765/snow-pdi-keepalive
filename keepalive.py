

import os
import sys
import shutil
from playwright.sync_api import sync_playwright

PDI_URL = os.environ.get("PDI_URL", "").rstrip("/")
PDI_USER = os.environ.get("PDI_USER", "")
PDI_PASS = os.environ.get("PDI_PASS", "")

PROOF_DIR = "proof"

# How long to give a possibly-hibernating instance to finish waking up
# after navigation/login, in milliseconds.
WAKE_GRACE_MS = 15000


def fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def shot(page, name: str):
    """Save a numbered screenshot into the proof folder."""
    path = os.path.join(PROOF_DIR, name)
    page.screenshot(path=path, full_page=True)
    print(f"[INFO] Screenshot saved: {path}")


def safe_wait(page):
    """
    Wait for the page to finish its initial load, then give it a short
    grace period. Does NOT use networkidle -- ServiceNow's UI polls
    constantly in the background and networkidle can hang forever.
    """
    try:
        page.wait_for_load_state("load", timeout=60000)
    except Exception:
        print("[WARN] load event timed out, continuing anyway...")
    page.wait_for_timeout(WAKE_GRACE_MS)


def main():
    if not all([PDI_URL, PDI_USER, PDI_PASS]):
        fail("Missing PDI_URL, PDI_USER, or PDI_PASS env vars.")

    if os.path.exists(PROOF_DIR):
        shutil.rmtree(PROOF_DIR)
    os.makedirs(PROOF_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"[INFO] Opening {PDI_URL} ...")
        page.goto(PDI_URL, timeout=60000)
        safe_wait(page)
        shot(page, "1_initial_page.png")

        if "hibernat" in page.content().lower():
            print("[INFO] Instance appears to be hibernating, looking for wake button...")
            try:
                page.click("text=Wake", timeout=10000)
                safe_wait(page)
            except Exception:
                print("[WARN] No wake button found, continuing anyway...")
            shot(page, "2_after_wake_attempt.png")
        else:
            shot(page, "2_after_wake_attempt.png")  # same page, kept for consistent numbering

        try:
            page.wait_for_selector("#user_name", timeout=30000)
        except Exception:
            shot(page, "3_login_form_not_found.png")
            fail("Login form (#user_name) not found. Page layout may have changed, "
                 "or the instance is still waking up and needs more time.")

        page.fill("#user_name", PDI_USER)
        page.fill("#user_password", PDI_PASS)
        shot(page, "3_form_filled.png")

        page.click("#sysverb_login")
        safe_wait(page)
        shot(page, "4_after_submit.png")

        content = page.content().lower()
        current_url = page.url.lower()

        if "user_password" in content and "invalid" in content:
            shot(page, "5_login_failed.png")
            browser.close()
            fail("Login failed -- invalid username or password.")

        if "login.do" in current_url:
            shot(page, "5_login_failed.png")
            browser.close()
            fail("Still on login page after submit -- login likely failed.")

        shot(page, "5_final_landed_page.png")
        print(f"[SUCCESS] Logged in. Landed on: {page.url}")
        browser.close()


if __name__ == "__main__":
    main()
