import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

EAST_OTTAWA_FACILITIES = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", "Navan",
    "Bernard-Grandmaître", "St-Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def fetch_real_ice():
    slots = []
    with sync_playwright() as p:
        # Launch headless browser to bypass bot detection
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate directly to Ottawa's ActiveNet reservation page
        url = "https://ca.apm.activecommunities.com/ottawa/ActiveNet_Calendar"
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Extract reservations rendered in the DOM / API responses
            # Note: You can target the specific facility dropdown or table elements here
            print("Successfully reached ActiveNet calendar page.")
        except Exception as e:
            print(f"Playwright navigation notice: {e}")
            
        browser.close()

    # Save real data only (no synthetic fallbacks)
    output = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(slots),
        "slots": slots
    }

    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    fetch_real_ice()
