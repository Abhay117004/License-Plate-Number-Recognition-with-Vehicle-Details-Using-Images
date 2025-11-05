import os
import glob
import json
import requests
import sys

from env_setup import RAPIDAPI_KEY, ocr_results_folder, api_results_folder


def get_vehicle_details(plate_number):
    """Fetches vehicle details for a given plate number using the new POST API."""
    api_key = RAPIDAPI_KEY
    if not api_key:
        print("Error: RAPIDAPI_KEY not configured.")
        return {"error": "RAPIDAPI_KEY not configured."}

    url = "[https://rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com/api/rc-vehicle/search-data](https://rto-vehicle-details-rc-puc-insurance-mparivahan.p.rapidapi.com/api/rc-vehicle/search-data)"
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
        print(f"API Request failed: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        print(f"API response was not valid JSON: {response.text}")
        return {"error": "Invalid API response", "raw": response.text}


if __name__ == "__main__":
    print("Fetching vehicle details from API...")

    base_filename = None
    if len(sys.argv) > 1:
        base_filename = sys.argv[1]
    else:
        print("Error: No base filename provided to api_call.py")
        sys.exit(1)

    search_pattern = os.path.join(ocr_results_folder, f"{base_filename}*.json")
    print(f"API_CALL searching for OCR results at: {search_pattern}")

    ocr_files = glob.glob(search_pattern)

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
                    api_results_folder, f"{base_name}.json")
                with open(output_path, 'w') as f:
                    json.dump(details, f, indent=2)
                print(f"Saved API result for {plate_number} to {output_path}")

            except Exception as e:
                print(f"Failed to process {base_name}.json: {e}")

    print("\nAPI calls finished.")
