import os
import glob
import base64
from env_setup import cropped_images, client


def extract_plates():
    plates = []
    print("OCR Started")

    for cropped_path in glob.glob(os.path.join(cropped_images, "*")):
        with open(cropped_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        response = client.chat.completions.create(
            model="moondream-2B",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"}
                         },
                        {"type": "text",
                         "text": """You are an expert OCR system. Extract the vehicle license plate in the image.

                         Rules:
                         - Combine all characters into one string.
                         - Remove spaces and special characters.
                         - Output only the plate text.
                         - If unreadable, return: NOT_FOUND."""}
                    ]
                }
            ]
        )

        text = response.choices[0].message.content.strip()
        print(f"{os.path.basename(cropped_path)} : {text}")

        if text != "NOT_FOUND":
            plates.append(text)

    print("OCR Done")
    return plates
