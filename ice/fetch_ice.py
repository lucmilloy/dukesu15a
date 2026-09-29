import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

LMI_URL = "https://ca.apm.activecommunities.com/ottawa/Reserve_Options"

# Official ActiveNet facility identifiers for East Ottawa LMI arenas
EAST_ARENAS = [
    "BobMacQuarrie", "Earl Armstrong", "Ray Friel", "Navan",
    "Bernard Grandmaître", "St-Laurent", "Canterbury", "Lois Kemp", "Cumberland"
]

def scrape_lmi():
    captured_slots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900}
        )
        page = context.new_page()

        print("Opening Register Ottawa LMI portal...")
        try:
            page.goto(LMI_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Navigation warning: {e}")

        # Extract initial facility cards
        cards = page.locator('.resource-result-item, tr.resource-row, div[class*="resource-item"]').all()
        print(f"Found {len(cards)} facility entries on portal.")

        for card in cards:
            try:
                text = card.inner_text().strip()
                if not text:
                    continue

                # Filter for East Ottawa arenas
                if any(arena.lower() in text.lower() for arena in EAST_ARENAS):
                    # Check if there are direct reserve links inside the row/card
                    links = card.locator('a').all()
                    for link in links:
                        link_text = link.inner_text().strip()
                        href = link.get_attribute("href") or ""

                        # Capture hyperlinked available time slots or reservation targets
                        if href and ("Reserve" in href or "resource" in href or "Calendar" in href):
                            full_url = href if href.startswith("http") else f"https://ca.apm.activecommunities.com/ottawa/{href}"
                            
                            captured_slots.append({
                                "id": f"slot-{len(captured_slots) + 1}",
                                "facility": text.split("\n")[0] if text else "East Ottawa Arena",
                                "details": text.replace("\n", " | "),
                                "directUrl": full_url
                            })
            except Exception as err:
                continue

        browser.close()

    # Deduplicate results
    unique_slots = []
    seen = set()
    for slot in captured_slots:
        key = (slot["facility"], slot["details"])
        if key not in seen:
            seen.add(key)
            unique_slots.append(slot)

    output_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(unique_slots),
        "slots": unique_slots
    }

    # Save to file
    out_dir = "ice" if os.path.exists("ice") else "."
    out_file = os.path.join(out_dir, "ice_data.json")
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Scrape complete. Output written to {out_file} ({len(unique_slots)} slots recorded).")

if __name__ == "__main__":
    scrape_lmi()
