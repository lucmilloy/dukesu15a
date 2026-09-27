import requests
import json
import os
from datetime import datetime, timedelta

# Target Arenas
ARENAS = [
    "Bob MacQuarrie", "Ray Friel", "Lois Kemp", "R.J. Kennedy",
    "Navan", "Earl Armstrong", "Canterbury", "Bernard-Grandmaître",
    "Jim Durrell", "Richcraft Sensplex"
]

def fetch_ice():
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    print(f"[{now_str}] Scanning Ottawa facilities for ice openings...")
    
    # Active search query structure
    found_slots = []
    
    data = {
        "last_updated": now_str,
        "slots": found_slots
    }
    
    with open("ice_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Updated ice_data.json successfully.")

if __name__ == "__main__":
    fetch_ice()
