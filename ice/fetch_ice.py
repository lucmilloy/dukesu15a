import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

EAST_OTTAWA_FACILITIES = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", "Navan",
    "Bernard-Grandmaître", "St-Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def fetch_ottawa_ice():
    captured_slots = []

    with sync_playwright() as p:
        # Launch browser with real-user emulation
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Intercept background XHR/Fetch API responses
        def intercept_response(response):
            if "Reserve_Options" in response.url or "resource" in response.url or "search" in response.url:
                try:
                    data = response.json()
                    # Parse potential slot structures returned by ActiveNet
                    items = data.get('body', {}).get('results', []) or data.get('results', []) or []
                    for item in items:
                        fac_name = item.get('facility_name', '') or item.get('resource_name', '')
                        if any(fac.lower() in fac_name.lower() for fac in EAST_OTTAWA_FACILITIES):
                            captured_slots.append({
                                "id": str(item.get('id') or len(captured_slots) + 1),
                                "facility": fac_name,
                                "rink": item.get('sub_facility_name', 'Main Rink'),
                                "date": item.get('start_date'),
                                "startTime": item.get('start_time'),
                                "endTime": item.get('end_time'),
                                "price": item.get('rate', 156.00),
                                "directUrl": "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"
                            })
                except Exception:
                    pass

        page.on("response", intercept_response)

        try:
            # Load the public Last-Minute Ice page directly
            page.goto("https://ca.apm.activecommunities.com/ottawa/Reserve_Options", wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Navigation note: {e}")

        browser.close()

    # Fallback/Safety Check: Ensure JSON remains structured
    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(captured_slots),
        "slots": captured_slots
    }

    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Scrape completed: {len(captured_slots)} slots recorded.")

if __name__ == "__main__":
    fetch_ottawa_ice()
