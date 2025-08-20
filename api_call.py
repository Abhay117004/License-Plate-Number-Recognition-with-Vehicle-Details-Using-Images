import requests
import json
import os
from ocr import extract_plates


def get_vehicle_details(plate_number):
    url = "https://rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com/api/rc-vehicle/search-data"
    querystring = {"vehicle_no": plate_number}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers,
                                params=querystring, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid response", "raw": response.text}


if __name__ == "__main__":
    print("Fetching vehicle details from GET API...")
    plates = extract_plates()

    if not plates:
        print("No valid plates detected.")
    else:
        for plate in plates:
            print(f"\n[INFO] Checking plate: {plate}")
            result = get_vehicle_details(plate)
            print(json.dumps(result, indent=2))
