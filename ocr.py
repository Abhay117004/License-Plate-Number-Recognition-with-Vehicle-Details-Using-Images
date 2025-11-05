import os
import glob
import json
from PIL import Image
import google.generativeai as genai
import sys

from env_setup import cropped_images, GEMINI_API_KEY, ocr_results_folder


def extract_plates(base_filename=None):
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured. OCR cannot proceed.")
        return
    genai.configure(api_key=GEMINI_API_KEY)
    print("OCR Started: Creating individual JSON files for each plate.")

    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    prompt = """
    You are a state-of-the-art AI Vehicle Recognition Specialist. Your task is to accurately detect, read, and normalize the alphanumeric text from a vehicle license plate image.

    **Primary Objective:**
    - Extract the license plate text with zero extra spaces or garbage characters.
    - Always normalize Indian plates:
    - Convert any regional language text (e.g., Devanagari, Hindi, Marathi, etc.) into the standard Latin format.
    - Replace the full state name (like "MAHARASHTRA") with its two-letter state code (e.g., "MH" for Maharashtra).
    - Remove all spaces and non-alphanumeric symbols.
    - Final format should look like `MH12GC2868`.

    **Examples:**
    - "महाराष्ट्र 12 जी सी 2868" → "MH12GC2868"
    - "Delhi 5 AB 1234" → "DL5AB1234"
    - "गुजरात 07 एचके 9087" → "GJ07HK9087"

    **Strict Output Instructions:**
    Respond ONLY with a JSON object:
    ```json
    {
    "plate_text_normalized": "string",
    "confidence_score": "float (0.0 to 1.0)",
    "is_readable": "boolean",
    "country_detected": "string (or null)",
    "format_applied": "boolean",
    "notes": "string (for ambiguities or issues)"
    }
    """

    if base_filename:
        search_pattern = os.path.join(cropped_images, f"{base_filename}*")
    else:
        print("Error: No base filename provided to ocr.py")
        return

    print(f"OCR searching for cropped plates at: {search_pattern}")
    cropped_files = glob.glob(search_pattern)

    if not cropped_files:
        print("No cropped plates found to process.")
        return

    for cropped_path in cropped_files:
        base_name = os.path.splitext(os.path.basename(cropped_path))[0]
        print(f"Processing OCR for: {base_name}")
        try:
            img = Image.open(cropped_path)
            response = model.generate_content([prompt, img])
            cleaned = response.text.strip().replace(
                "```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            plate_text = result.get("plate_text_normalized", "NOT_FOUND")

            if plate_text != "NOT_FOUND" and result.get("is_readable", False):
                output_path = os.path.join(
                    ocr_results_folder, f"{base_name}.json")
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Saved OCR result for {base_name} to {output_path}")
            else:
                print(
                    f"Plate in {base_name} was deemed unreadable by the model.")

        except Exception as e:
            print(f"Could not process {base_name}: {e}")
            print(
                f"Response text that caused error: {response.text if 'response' in locals() else 'N/A'}")

    print("OCR Done")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_filename_arg = sys.argv[1]
        extract_plates(base_filename_arg)
    else:
        extract_plates()
