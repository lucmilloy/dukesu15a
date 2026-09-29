import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Direct URL to Ottawa's Last Minute Ice Resource Search
LMI_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

# East Ottawa Facility Keywords to filter
EAST_KEYWORDS = [
    "BobMacQuarrie", "Bob MacQuarrie", "Ray Friel", "Earl Armstrong",
    "Navan", "Bernard-Grandmaître", "Bernard Grandmaître", 
    "St-Laurent", "St. Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def scrape_ottawa_lmi():
    found_slots = []

    with sync_playwright() as p:
        # Launch browser in headful mode emulation
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        print("Navigating to Register Ottawa LMI Portal...")
        page.goto(LMI_URL, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for the main search input to be interactable
        page.wait_for_selector('input[type="text"]', timeout=15000)

        # Search each East facility keyword explicitly
        for kw in EAST_KEYWORDS:
            try:
                print(f"Querying portal for: {kw}...")
                
                # Clear and fill keyword search
                search_box = page.locator('input[type="text"]').first
                search_box.fill("")
                search_box.fill(kw)
                
                # Press Enter or click Search button
                page.keyboard.press("Enter")
                
                # Allow ActiveNet dynamic AJAX response to complete
                page.wait_for_timeout(3000)

                # Extract all clickable resource cards / blue hyperlinked results
                # ActiveNet LMI items always contain blue reservation links or resource row elements
                items = page.locator('.resource-result-item, tr.resource-row, div[class*="resource"]').all()

                for item in items:
                    text = item.inner_text().strip()
                    if not text:
                        continue

                    # Look for date/time patterns (e.g. Oct 2, 8:00 PM - 9:00 PM)
                    if any(term.lower() in text.lower() for term in EAST_KEYWORDS):
                        # Extract href if a direct booking link exists
                        links = item.locator('a').all()
                        booking_url = LMI_URL
                        for l in links:
                            href = l.get_attribute("href") or ""
                            if "Reserve" in href or "resource" in href:
                                booking_url = href if href.startswith("http") else f"https://ca.apm.activecommunities.com/ottawa/{href}"
                                break

                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        found_slots.append({
                            "id": f"slot-{len(found_slots) + 1}",
                            "facility": kw,
                            "title": lines[0] if lines else kw,
                            "details": " | ".join(lines[1:]) if len(lines) > 1 else text,
                            "directUrl": booking_url
                        })

            except Exception as e:
                print(f"Notice while searching {kw}: {e}")

        browser.close()

    # Deduplicate slots by title and details
    unique_slots = []
    seen = set()
    for slot in found_slots:
        identifier = f"{slot['facility']}-{slot['details']}"
        if identifier not in seen:
            seen.add(identifier)
            unique_slots.append(slot)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSuccess! Total unique slots captured: {len(unique_slots)}")

if __name__ == "__main__":
    scrape_ottawa_lmi()
