import requests
import json
from datetime import datetime, timedelta

def scrape_ottawa_ice():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %I:%M %p")
    print(f"[{now_str}] Querying Ottawa ActiveNet facility schedules...")

    url = "https://register.ottawa.ca/api/m/facility/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }

    # Target East/Central Arenas
    target_arenas = [
        "Bob MacQuarrie", "Ray Friel", "Lois Kemp", "R.J. Kennedy",
        "Navan", "Earl Armstrong", "Canterbury", "Bernard-Grandmaître",
        "Jim Durrell", "Richcraft Sensplex"
    ]

    found_slots = []

    # Calculate 20-day horizon window
    start_date = now.strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=20)).strftime("%Y-%m-%d")

    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "activity_type_ids": [1], # Ice Rinks
        "category": "Facility"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            results = response.json().get("body", {}).get("facilities", [])
            
            for item in results:
                facility_name = item.get("name", "")
                
                # Check for target East/Central arenas
                if any(arena.lower() in facility_name.lower() for arena in target_arenas):
                    for availability in item.get("availabilities", []):
                        slot_time_str = availability.get("start_time", "")
                        slot_date_str = availability.get("date", "")
                        
                        try:
                            slot_dt = datetime.strptime(slot_date_str, "%Y-%m-%d")
                            day_of_week = slot_dt.weekday() # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
                            hour = int(slot_time_str.split(":")[0]) if ":" in slot_time_str else 0
                            
                            # Filters: Weekdays (Tue/Wed/Fri 4 PM - 8 PM) | Weekends (Sat/Sun 8 AM - 8 PM)
                            is_target_weekday = (day_of_week in [1, 2, 4]) and (16 <= hour <= 20)
                            is_target_weekend = (day_of_week in [5, 6]) and (8 <= hour <= 20)

                            if is_target_weekday or is_target_weekend:
                                found_slots.append({
                                    "arena": facility_name,
                                    "date": slot_date_str,
                                    "time": slot_time_str,
                                    "link": f"https://register.ottawa.ca/facility/details/{item.get('id', '')}"
                                })
                        except Exception:
                            continue
        else:
            print(f"ActiveNet status code: {response.status_code}")

    except Exception as e:
        print(f"Scraper error: {e}")

    output_data = {
        "last_updated": now_str,
        "slots": found_slots
    }

    with open("ice_data.json", "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Complete. Target slots found: {len(found_slots)}")

if __name__ == "__main__":
    scrape_ottawa_ice()
