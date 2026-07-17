"""
HAR Recorder for ServiceNow PDI login flow.
--------------------------------------------
Launches a real (non-headless) browser so you can manually log in.
Records EVERYTHING - full request/response bodies, headers, timing -
and auto-saves the HAR file when you close the browser.

Usage:
    python har_recorder.py https://dev374528.service-now.com/

Output:
    ./har_recordings/session_<timestamp>.har
"""

import sys
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "har_recordings"


def main():
    if len(sys.argv) < 2:
        print("Usage: python har_recorder.py <url>")
        sys.exit(1)

    target_url = sys.argv[1]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    har_path = os.path.join(OUTPUT_DIR, f"session_{timestamp}.har")

    print(f"[INFO] Recording HAR to: {har_path}")
    print("[INFO] A browser window will open. Log in manually.")
    print("[INFO] Close the browser window when done — HAR auto-saves on close.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)

        # record_har_content="embed" captures full response bodies too,
        # not just headers/metadata — gives you the complete picture.
        context = browser.new_context(
            record_har_path=har_path,
            record_har_content="embed",
            record_har_mode="full",
            viewport={"width": 1366, "height": 800},
        )

        page = context.new_page()

        # Log every request/response live to console too, so you see
        # exactly what's firing in real time without needing to open the HAR.
        page.on("request", lambda req: print(f"[REQ]  {req.method:6s} {req.url}"))
        page.on("response", lambda res: print(f"[RES]  {res.status:3d}    {res.url}"))

        page.goto(target_url, timeout=60000)

        print("\n[INFO] Waiting for you to finish logging in and close the browser...")
        print("[INFO] (Or press Enter here once done, to close it automatically.)\n")

        try:
            input()
        except KeyboardInterrupt:
            pass

        # Closing the context is what flushes/writes the HAR file to disk.
        context.close()
        browser.close()

    print(f"\n[SUCCESS] HAR saved: {har_path}")
    print("[INFO] Send me this file (or grep the login POST request from it) "
          "and I'll pull the real selectors/endpoints out of it.")


if __name__ == "__main__":
    main()
