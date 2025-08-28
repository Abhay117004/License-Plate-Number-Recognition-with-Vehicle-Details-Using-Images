import os
import glob
import json
from PIL import Image
import google.generativeai as genai
from env_setup import cropped_images


def extract_plates():
    google_api_key = os.environ.get("GEMINI_API_KEY")
    if not google_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=google_api_key)

    plates = []
    print("OCR Started with Detailed Prompt")

    model = genai.GenerativeModel('gemini-2.5-pro')

    prompt = """
    You are a state-of-the-art AI Vehicle Recognition Specialist. Your primary objective is to accurately extract, normalize, and verify the alphanumeric text from the vehicle license plate in the provided image. You must be meticulous and provide your output in a structured JSON format.

    **Primary Objective:**
    Analyze the image to find the vehicle license plate, extract its text, and provide detailed, structured information about it.

    **Output Format (Strict JSON):**
    Return a single JSON object with the following schema. Do not output any text outside of this JSON object.
    ```json
    {
      "plate_text_normalized": "string",
      "confidence_score": "float (0.0 to 1.0)",
      "is_readable": "boolean",
      "country_detected": "string (or null)",
      "format_applied": "boolean",
      "notes": "string (for ambiguities or issues)"
    }
    ```

    **Step-by-Step Instructions:**
    1. Identify & Extract
    2. Translate & Normalize
    3. Verify with Country Context
    4. Final Formatting
    5. Handle Edge Cases: unreadable, partial, ambiguous, no plate found.

    Process the image provided and return only the JSON object.
    """

    for cropped_path in glob.glob(os.path.join(cropped_images, "*")):
        try:

            img = Image.open(cropped_path)

            response = model.generate_content([prompt, img])

            cleaned = response.text.strip().replace(
                "```json", "").replace("```", "").strip()

            result = json.loads(cleaned)
            plate_text = result.get("plate_text_normalized", "NOT_FOUND")

            print(
                f"{os.path.basename(cropped_path)} : {plate_text} "
                f"(Confidence: {result.get('confidence_score', 'N/A')})"
            )

            if plate_text != "NOT_FOUND" and result.get("is_readable", False):
                plates.append(plate_text)

        except json.JSONDecodeError:
            print(
                f"Invalid JSON from Gemini for {os.path.basename(cropped_path)}. Raw output:\n{response.text}")
        except Exception as e:
            print(f"Error processing {os.path.basename(cropped_path)}: {e}")

    print("OCR Done")
    return plates
