import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

LMI_ENTRY_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

EAST_KEYWORDS = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", "Navan",
    "Bernard Grandmaître", "St-Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def capture_lmi_api():
    captured_results = []

    with sync_playwright() as p:
        # Launch real headful browser simulation
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        # Intercept background XHR/Fetch JSON responses from ActiveNet
        def handle_response(response):
            if "search" in response.url.lower() or "resource" in response.url.lower():
                try:
                    data = response.json()
                    # Parse ActiveNet JSON response structure
                    items = data.get("body", {}).get("results", []) or data.get("results", [])
                    for item in items:
                        name = item.get("resource_name", "") or item.get("name", "")
                        if any(kw.lower() in name.lower() for kw in EAST_KEYWORDS):
                            captured_results.append({
                                "id": f"slot-{len(captured_results) + 1}",
                                "facility": name,
                                "date": item.get("start_date", "Available"),
                                "time": f"{item.get('start_time', '')} - {item.get('end_time', '')}",
                                "directUrl": "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"
                            })
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            print("Connecting to Register Ottawa LMI portal...")
            page.goto(LMI_ENTRY_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # Trigger real interaction on input to fire API requests
            search_box = page.locator('input[type="text"]').first
            if search_box.is_visible():
                search_box.click()
                search_box.fill("Arena")
                page.keyboard.press("Enter")
                page.wait_for_timeout(5000)

        except Exception as e:
            print(f"Browser navigation note: {e}")

        browser.close()

    # Deduplicate captured results
    unique_slots = []
    seen = set()
    for item in captured_results:
        key = (item["facility"], item["time"])
        if key not in seen:
            seen.add(key)
            unique_slots.append(item)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    out_file = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Done! Extracted {len(unique_slots)} slots directly from ActiveNet API.")

if __name__ == "__main__":
    capture_lmi_api()
