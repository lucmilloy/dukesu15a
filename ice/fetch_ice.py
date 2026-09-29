import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

LMI_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

EAST_ARENAS = [
    "Bob MacQuarrie", "Ray Friel", "Earl Armstrong", "Navan",
    "Bernard-Grandmaître", "Bernard Grandmaître", "St-Laurent", 
    "Canterbury", "Lois Kemp", "Cumberland"
]

def scrape_ottawa_ice():
    captured_slots = []

    with sync_playwright() as p:
        # Launch browser with human viewport and stealth flags
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        print("Navigating to ActiveNet LMI portal...")
        try:
            page.goto(LMI_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            # Wait for search box to be visible
            search_box = page.locator('input[type="text"]').first
            page.wait_for_selector('input[type="text"]', timeout=15000)

            # Perform search for "Arena" or "Ice" to expand all arena rows
            print("Executing broader resource search...")
            search_box.click()
            search_box.fill("Arena")
            page.keyboard.press("Enter")
            
            # Allow ASP.NET postback to complete
            page.wait_for_timeout(6000)

            # Extract table rows and result items
            rows = page.locator("tr, .resource-result-item, .calendar-event-container").all()
            print(f"Scanned {len(rows)} DOM elements.")

            for row in rows:
                try:
                    text = row.inner_text().strip()
                    if not text:
                        continue

                    # Filter for East Ottawa facility matches
                    if any(arena.lower() in text.lower() for arena in EAST_ARENAS):
                        # Extract booking href if present
                        link_el = row.locator("a[href*='Reserve'], a[href*='resource']").first
                        href = LMI_URL
                        if link_el.count() > 0:
                            val = link_el.get_attribute("href") or ""
                            if val:
                                href = val if val.startswith("http") else f"https://ca.apm.activecommunities.com/ottawa/{val}"

                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        
                        captured_slots.append({
                            "id": f"slot-{len(captured_slots) + 1}",
                            "facility": lines[0] if lines else "East Ottawa Arena",
                            "details": " | ".join(lines[1:]) if len(lines) > 1 else text,
                            "directUrl": href
                        })
                except Exception:
                    continue

        except Exception as e:
            print(f"Execution notice: {e}")

        browser.close()

    # Deduplicate results
    unique_slots = []
    seen = set()
    for s in captured_slots:
        key = (s["facility"], s["details"])
        if key not in seen:
            seen.add(key)
            unique_slots.append(s)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    out_file = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Done. Written {len(unique_slots)} slots to {out_file}.")

if __name__ == "__main__":
    scrape_ottawa_ice()
