import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

EAST_OTTAWA_FACILITIES = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", "Navan",
    "Bernard-Grandmaître", "St-Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def fetch_real_ice():
    captured_slots = []

    with sync_playwright() as p:
        # Launch headless browser with full user-agent spoofing
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Listen for internal API responses while the page loads
        def handle_response(response):
            if "reservation/search" in response.url or "reservation/quicksearch" in response.url:
                try:
                    data = response.json()
                    reservations = data.get('body', {}).get('reservations', []) or data.get('reservations', []) or []
                    
                    for slot in reservations:
                        fac_name = slot.get('facility_name', '') or slot.get('center_name', '')
                        if any(east_fac.lower() in fac_name.lower() for east_fac in EAST_OTTAWA_FACILITIES):
                            captured_slots.append({
                                "id": str(slot.get("reservation_id") or slot.get("id")),
                                "facility": fac_name,
                                "rink": slot.get("sub_facility_name") or slot.get("room_name") or "Main Rink",
                                "date": slot.get("start_date") or slot.get("date"),
                                "startTime": slot.get("start_time"),
                                "endTime": slot.get("end_time"),
                                "duration": slot.get("duration_minutes", 60),
                                "price": float(slot.get("rate") or slot.get("price") or 156.00),
                                "directUrl": f"https://ca.apm.activecommunities.com/ottawa/Reserve_Options?facility_id={slot.get('facility_id', '')}"
                            })
                except Exception:
                    pass

        page.on("response", handle_response)

        # Navigate to ActiveNet calendar
        try:
            print("Opening ActiveNet Portal via Playwright...")
            page.goto("https://ca.apm.activecommunities.com/ottawa/ActiveNet_Calendar", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(5000)  # Allow background XHR requests to complete
        except Exception as e:
            print(f"Browser navigation notice: {e}")

        browser.close()

    # Deduplicate slots by ID
    unique_slots = {s['id']: s for s in captured_slots}.values()
    final_slots = list(unique_slots)

    output = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(final_slots),
        "slots": final_slots
    }

    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Successfully captured and saved {len(final_slots)} live ice slots.")

if __name__ == "__main__":
    fetch_real_ice()
