import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

LMI_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

# East Ottawa Facility Identifiers
EAST_FACILITIES = [
    "Bob MacQuarrie", "BobMacQuarrie", "Ray Friel", "Earl Armstrong",
    "Navan", "Bernard Grandmaître", "Bernard-Grandmaître", 
    "St-Laurent", "St. Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def scrape_ottawa_ice():
    found_slots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        print(f"Connecting to ActiveNet LMI portal: {LMI_URL}")
        try:
            page.goto(LMI_URL, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
        except Exception as e:
            print(f"Initial page load warning: {e}")

        # Search facility keywords safely
        for facility in EAST_FACILITIES:
            try:
                # Find keyword input
                search_input = page.locator('input[type="text"]').first
                if not search_input.is_visible():
                    continue

                print(f"Searching: {facility}")
                search_input.click()
                search_input.fill("")
                search_input.type(facility, delay=50)
                
                # Submit search
                search_button = page.locator('button:has-text("Search"), input[type="submit"]').first
                if search_button.is_visible():
                    search_button.click()
                else:
                    search_input.press("Enter")

                page.wait_for_timeout(3000)

                # Query page content without throwing selector errors
                rows = page.locator("tr, div.resource-result-item, div.calendar-event").all()
                
                for row in rows:
                    try:
                        text = row.inner_text().strip()
                        if not text:
                            continue

                        # Match time format (e.g. 7:00 AM, 08:30 PM)
                        if re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)', text):
                            # Extract direct link if present
                            link_el = row.locator("a").first
                            href = LMI_URL
                            if link_el.count() > 0:
                                val = link_el.get_attribute("href") or ""
                                if val:
                                    href = val if val.startswith("http") else f"https://ca.apm.activecommunities.com/ottawa/{val}"

                            found_slots.append({
                                "id": f"slot-{len(found_slots) + 1}",
                                "facility": facility,
                                "details": text.replace("\n", " | "),
                                "directUrl": href
                            })
                    except Exception:
                        continue

            except Exception as err:
                print(f"Skip {facility} due to error: {err}")

        browser.close()

    # Deduplicate results
    unique_slots = []
    seen = set()
    for s in found_slots:
        key = (s["facility"], s["details"])
        if key not in seen:
            seen.add(key)
            unique_slots.append(s)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    # Ensure output directory exists and write JSON
    out_dir = "ice" if os.path.exists("ice") else "."
    out_file = os.path.join(out_dir, "ice_data.json")
    
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Scrape completed cleanly. Recorded {len(unique_slots)} slots to {out_file}.")

if __name__ == "__main__":
    scrape_ottawa_ice()
