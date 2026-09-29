import os
import json
import urllib.request
from datetime import datetime

# East Ottawa Arenas
EAST_OTTAWA_FACILITIES = [
    "Bob MacQuarrie",
    "Ray Friel",
    "Earl Armstrong",
    "Navan Arena",
    "Bernard-Grandmaître",
    "St-Laurent",
    "Canterbury",
    "Lois Kemp",
    "Cumberland Community"
]

API_URL = "https://ca.apm.activecommunities.com/ottawa/rest/reservation/search"

def fetch_live_east_ottawa_ice():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    
    payload = json.dumps({
        "facility_type_ids": [1],
        "page_number": 1,
        "page_size": 200
    }).encode('utf-8')

    req = urllib.request.Request(API_URL, data=payload, headers=headers, method='POST')
    
    east_ottawa_slots = []
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            all_slots = data.get('body', {}).get('reservations', [])
            
            for slot in all_slots:
                facility_name = slot.get('facility_name', '')
                if any(east_fac.lower() in facility_name.lower() for east_fac in EAST_OTTAWA_FACILITIES):
                    east_ottawa_slots.append({
                        "id": slot.get("reservation_id"),
                        "facility": facility_name,
                        "rink": slot.get("sub_facility_name", "Main Rink"),
                        "date": slot.get("start_date"),
                        "startTime": slot.get("start_time"),
                        "endTime": slot.get("end_time"),
                        "duration": slot.get("duration_minutes", 60),
                        "price": slot.get("rate", 156.00),
                        "directUrl": f"https://ca.apm.activecommunities.com/ottawa/Reserve_Options?facility_id={slot.get('facility_id')}"
                    })
            print(f"Retrieved {len(east_ottawa_slots)} East Ottawa ice slots.")

    except Exception as e:
        print(f"API Fetch Notice (writing current snapshot): {e}")

    # Build response payload
    output = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "count": len(east_ottawa_slots),
        "slots": east_ottawa_slots
    }
    
    # Determine safe output path regardless of execution context
    output_path = "ice/ice_data.json" if os.path.exists("ice") else "ice_data.json"
    
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully wrote output to {output_path}")

if __name__ == "__main__":
    fetch_live_east_ottawa_ice()
