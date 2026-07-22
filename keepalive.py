
import os
import sys
import shutil
import time
from playwright.sync_api import sync_playwright

PDI_URL = os.environ.get("PDI_URL", "").rstrip("/")
PDI_USER = os.environ.get("PDI_USER", "")
PDI_PASS = os.environ.get("PDI_PASS", "")

PROOF_DIR = "proof"

# Total time to keep polling for the login form to appear, in seconds.
# A hibernating PDI can take well over a minute to wake up, so this is
# generous on purpose.
WAKE_TIMEOUT_S = 120
POLL_INTERVAL_S = 5


def fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def shot(page, name: str):
    """Save a numbered screenshot into the proof folder."""
    path = os.path.join(PROOF_DIR, name)
    page.screenshot(path=path, full_page=True)
    print(f"[INFO] Screenshot saved: {path}")


def wait_for_login_form(page, timeout_s=WAKE_TIMEOUT_S):
    """
    Poll for the login form to appear, reloading periodically. Handles a
    hibernating/waking instance whose interstitial page doesn't contain any
    predictable text, by just retrying until the real form shows up or we
    give up after timeout_s seconds.
    """
    deadline = time.time() + timeout_s
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            page.wait_for_selector("#user_name", timeout=5000)
            return True
        except Exception:
            pass

        print(f"[INFO] Login form not up yet (attempt {attempt}), "
              f"reloading and retrying...")
        try:
            page.reload(timeout=30000)
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL_S)

    return False


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
        try:
            page.wait_for_load_state("load", timeout=60000)
        except Exception:
            print("[WARN] load event timed out, continuing anyway...")
        shot(page, "1_initial_page.png")

        print("[INFO] Waiting for login form (polling in case instance is waking up)...")
        found = wait_for_login_form(page)
        shot(page, "2_after_wake_attempt.png")

        if not found:
            shot(page, "3_login_form_not_found.png")
            fail(f"Login form (#user_name) still not found after "
                 f"{WAKE_TIMEOUT_S}s of polling. Instance may be taking "
                 f"unusually long to wake up, or the page layout changed.")

        page.fill("#user_name", PDI_USER)
        page.fill("#user_password", PDI_PASS)
        shot(page, "3_form_filled.png")

        page.click("#sysverb_login")
        try:
            page.wait_for_load_state("load", timeout=60000)
        except Exception:
            print("[WARN] load event timed out after submit, continuing anyway...")
        page.wait_for_timeout(5000)
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
