import os
import sys
from playwright.sync_api import sync_playwright

PDI_URL = os.environ.get("PDI_URL", "").rstrip("/")
PDI_USER = os.environ.get("PDI_USER", "")
PDI_PASS = os.environ.get("PDI_PASS", "")

def fail(msg: str):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main():
    if not all([PDI_URL, PDI_USER, PDI_PASS]):
        fail("Missing PDI_URL, PDI_USER, or PDI_PASS env vars.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"[INFO] Opening {PDI_URL} ...")
        page.goto(PDI_URL, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)

        if "hibernat" in page.content().lower():
            print("[INFO] Instance appears to be hibernating, looking for wake button...")
            try:
                page.click("text=Wake", timeout=10000)
                page.wait_for_load_state("networkidle", timeout=60000)
            except Exception:
                print("[WARN] No wake button found, continuing anyway...")

        try:
            page.wait_for_selector("#user_name", timeout=15000)
        except Exception:
            fail("Login form (#user_name) not found. Page layout may have "
                 "changed -- re-run har_recorder.py to re-verify selectors.")

        page.fill("#user_name", PDI_USER)
        page.fill("#user_password", PDI_PASS)
        page.click("#sysverb_login")
        page.wait_for_load_state("networkidle", timeout=60000)

        content = page.content().lower()
        current_url = page.url.lower()

        if "user_password" in content and "invalid" in content:
            browser.close()
            fail("Login failed -- invalid username or password.")

        if "login.do" in current_url:
            browser.close()
            fail("Still on login page after submit -- login likely failed.")

        print(f"[SUCCESS] Logged in. Landed on: {page.url}")
        browser.close()


if __name__ == "__main__":
    main()
