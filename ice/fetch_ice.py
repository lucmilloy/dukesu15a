import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# East Ottawa facilities & keyword matching rules
TARGET_FACILITIES = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", 
    "Navan", "Bernard-Grandmaître", "St-Laurent", 
    "Canterbury", "Lois Kemp", "Cumberland"
]

LMI_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

def scrape_ice_slots():
    slots = []

    with sync_playwright() as p:
        # Launch Chromium with full browser context
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to Register Ottawa Last-Minute Ice Portal...")
        page.goto(LMI_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Iterate through target facilities to pull available blue slots
        for target in TARGET_FACILITIES:
            try:
                print(f"Checking availability for: {target}...")
                
                # Search input field on ActiveNet Reserve_Options page
                search_input = page.locator('input[type="text"]').first
                if search_input.is_visible():
                    search_input.fill(target)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(2500)

                # ActiveNet blue links indicate available last-minute ice
                links = page.query_selector_all('a[href*="Reserve_Options"], a[href*="resource"], .resource-result-item')
                
                for link in links:
                    text = link.inner_text().strip()
                    href = link.get_attribute("href") or ""
                    
                    # Validate time pattern (e.g., 7:00 PM - 8:00 PM)
                    if re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM)', text, re.IGNORECASE):
                        slots.append({
                            "id": f"slot-{len(slots) + 1}",
                            "facility": target,
                            "details": text.replace("\n", " "),
                            "directUrl": href if href.startswith("http") else f"https://ca.apm.activecommunities.com/ottawa/{href}"
                        })

            except Exception as e:
                print(f"Error checking {target}: {e}")

        browser.close()

    # Deduplicate slots by details/facility
    unique_slots = []
    seen = set()
    for s in slots:
        key = (s["facility"], s["details"])
        if key not in seen:
            seen.add(key)
            unique_slots.append(s)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    # Save to JSON
    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nScrape complete! Found {len(unique_slots)} available slots.")

if __name__ == "__main__":
    scrape_ice_slots()
