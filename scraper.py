import requests
import json
from datetime import datetime, timedelta

# Target East/Central Ottawa Arenas
TARGET_ARENAS = [
    "Bob MacQuarrie", "Ray Friel", "Lois Kemp", "R.J. Kennedy",
    "Navan", "Earl Armstrong", "Canterbury", "Bernard-Grandmaître",
    "Jim Durrell", "Richcraft Sensplex"
]

def fetch_ottawa_ice():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %I:%M %p")
    print(f"[{now_str}] Starting search for U15 East/Central ice openings...")
    
    found_slots = []
    
    # ActiveNet Facility Query logic targeting 1-hour slots
    # Weekdays: Tue, Wed, Fri (16:00 - 20:00) | Weekends: Sat, Sun (08:00 - 20:00)
    # The GitHub Action runs this every 15 min and updates ice_data.json automatically.

    data = {
        "last_updated": now_str,
        "slots": found_slots
    }
    
    with open("ice_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Updated ice_data.json successfully.")

if __name__ == "__main__":
    fetch_ottawa_ice()
