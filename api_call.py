import os
import glob
import json
import requests
from env_setup import RAPIDAPI_KEY

OCR_RESULTS_DIR = 'ocr_results'
API_RESULTS_DIR = 'api_results'


def get_vehicle_details(plate_number):
    """Fetches vehicle details for a given plate number using the new POST API."""
    if not RAPIDAPI_KEY:
        return {"error": "RAPIDAPI_KEY not configured."}

    url = "https://vehicle-rc-verification-advance.p.rapidapi.com/Getrcfulldetails"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "vehicle-rc-verification-advance.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    payload = {"rcnumber": plate_number}

    try:
        response = requests.post(url, headers=headers,
                                 json=payload, timeout=15)
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
