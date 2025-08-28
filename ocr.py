import os
import glob
import json
from PIL import Image
import google.generativeai as genai
from env_setup import cropped_images, GEMINI_API_KEY

OCR_RESULTS_DIR = 'ocr_results'


def extract_plates():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured. OCR cannot proceed.")
        return
    genai.configure(api_key=GEMINI_API_KEY)

    os.makedirs(OCR_RESULTS_DIR, exist_ok=True)

    print("OCR Started: Creating individual JSON files for each plate.")
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = """
    You are a state-of-the-art AI Vehicle Recognition Specialist. Your very important task is to accurately detect, read, and normalize the alphanumeric text from a vehicle license plate in a given image. Follow the instructions carefully.

    **Primary Objective:**
    - Extract the license plate text with zero extra spaces or garbage characters.
    - Normalize the text to a standard, readable alphanumeric format (uppercase, no special symbols unless part of plate).
    - Verify the plate against the most likely country format.

    **Strict Output Instructions:**
    - Respond ONLY with a JSON object matching the schema below. No extra text or commentary.
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

    for cropped_path in glob.glob(os.path.join(cropped_images, "*")):
        base_name = os.path.splitext(os.path.basename(cropped_path))[0]
        try:
            img = Image.open(cropped_path)
            response = model.generate_content([prompt, img])
            cleaned = response.text.strip().replace(
                "```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            plate_text = result.get("plate_text_normalized", "NOT_FOUND")

            if plate_text != "NOT_FOUND" and result.get("is_readable", False):
                output_path = os.path.join(
                    OCR_RESULTS_DIR, f"{base_name}.json")
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Saved OCR result for {base_name} to {output_path}")
            else:
                print(
                    f"Plate in {base_name} was deemed unreadable by the model.")

        except Exception as e:
            print(f"Could not process {base_name}: {e}")

    print("OCR Done")


if __name__ == "__main__":
    extract_plates()
