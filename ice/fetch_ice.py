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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "facility_type_ids": [1],
        "page_number": 1,
        "page_size": 200
    }).encode('utf-8')

    req = urllib.request.Request(API_URL, data=payload, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            all_slots = data.get('body', {}).get('reservations', [])
            
            east_ottawa_slots = []
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
            
            output = {
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "count": len(east_ottawa_slots),
                "slots": east_ottawa_slots
            }
            
            with open("ice_data.json", "w") as f:
                json.dump(output, f, indent=2)
                
            print(f"Successfully updated ice_data.json with {len(east_ottawa_slots)} slots.")

    except Exception as e:
        print(f"Error fetching ice data: {e}")

if __name__ == "__main__":
    fetch_live_east_ottawa_ice()
