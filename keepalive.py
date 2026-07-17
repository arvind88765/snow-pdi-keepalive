import os
import sys
import shutil
from playwright.sync_api import sync_playwright

PDI_URL = os.environ.get("PDI_URL", "").rstrip("/")
PDI_USER = os.environ.get("PDI_USER", "")
PDI_PASS = os.environ.get("PDI_PASS", "")

PROOF_DIR = "proof"


def fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def shot(page, name: str):
    """Save a numbered screenshot into the proof folder."""
    path = os.path.join(PROOF_DIR, name)
    page.screenshot(path=path, full_page=True)
    print(f"[INFO] Screenshot saved: {path}")


def main():
    if not all([PDI_URL, PDI_USER, PDI_PASS]):
        fail("Missing PDI_URL, PDI_USER, or PDI_PASS env vars.")

    # Wipe old screenshots from any previous local run before starting fresh.
    if os.path.exists(PROOF_DIR):
        shutil.rmtree(PROOF_DIR)
    os.makedirs(PROOF_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"[INFO] Opening {PDI_URL} ...")
        page.goto(PDI_URL, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        shot(page, "1_initial_page.png")

        if "hibernat" in page.content().lower():
            print("[INFO] Instance appears to be hibernating, looking for wake button...")
            try:
                page.click("text=Wake", timeout=10000)
                page.wait_for_load_state("networkidle", timeout=60000)
            except Exception:
                print("[WARN] No wake button found, continuing anyway...")
            shot(page, "2_after_wake_attempt.png")
        else:
            shot(page, "2_after_wake_attempt.png")  # same page, kept for consistent numbering

        try:
            page.wait_for_selector("#user_name", timeout=15000)
        except Exception:
            shot(page, "3_login_form_not_found.png")
            fail("Login form (#user_name) not found. Page layout may have changed.")

        page.fill("#user_name", PDI_USER)
        page.fill("#user_password", PDI_PASS)
        shot(page, "3_form_filled.png")

        page.click("#sysverb_login")
        page.wait_for_load_state("networkidle", timeout=60000)
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
