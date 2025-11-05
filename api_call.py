import os
import glob
import json
import requests
from env_setup import RAPIDAPI_KEY

OCR_RESULTS_DIR = 'ocr_results'
API_RESULTS_DIR = 'api_results'


def get_vehicle_details(plate_number):
    """Fetches vehicle details for a given plate number using the new POST API."""
    # Prefer configured key from env_setup, fallback to the key provided in the
    # example snippet if not present.
    api_key = RAPIDAPI_KEY or "935854549emsh35ddace65ebc8b7p13d261jsn96a7f03f9794"

    if not api_key:
        return {"error": "RAPIDAPI_KEY not configured."}

    # New GET-based RapidAPI endpoint (uses query param vehicle_no)
    url = "https://rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com/api/rc-vehicle/search-data"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com"
    }
    params = {"vehicle_no": plate_number}

    try:
        response = requests.get(url, headers=headers,
                                params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid API response", "raw": response.text}


if __name__ == "__main__":
    print("Fetching vehicle details from new POST API...")
    os.makedirs(API_RESULTS_DIR, exist_ok=True)

    ocr_files = glob.glob(os.path.join(OCR_RESULTS_DIR, "*.json"))

    if not ocr_files:
        print("No OCR result files found to process.")
    else:
        for ocr_file_path in ocr_files:
            base_name = os.path.splitext(os.path.basename(ocr_file_path))[0]
            try:
                with open(ocr_file_path, 'r') as f:
                    ocr_data = json.load(f)

                plate_number = ocr_data.get("plate_text_normalized")
                if not plate_number:
                    continue

                print(
                    f"\n[API_CALL] Checking plate: {plate_number} from {base_name}.json")
                details = get_vehicle_details(plate_number)
                details['plate_number_queried'] = plate_number

                output_path = os.path.join(
                    API_RESULTS_DIR, f"{base_name}.json")
                with open(output_path, 'w') as f:
                    json.dump(details, f, indent=2)
                print(f"Saved API result for {plate_number} to {output_path}")

            except Exception as e:
                print(f"Failed to process {base_name}.json: {e}")

    print("\nAPI calls finished.")
