import os
import cv2
import glob
from env_setup import model, input_folder, cropped_images, device

print("Starting plate preprocessing...")

image_paths = glob.glob(os.path.join(input_folder, "*"))
if not image_paths:
    print("No images found in input_folder.")
else:
    for image_path in image_paths:
        print(f"Processing image: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Could not read image {image_path}. Skipping.")
            continue

        results = model(image, verbose=False, device=device)

        base_name = os.path.splitext(os.path.basename(image_path))[0]

        if not results[0].boxes:
            print(
                f"No license plates detected in {os.path.basename(image_path)}.")
            continue

        for idx, box in enumerate(results[0].boxes):
            coords = box.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, coords)

            cropped_plate = image[y1:y2, x1:x2]

            save_path = os.path.join(
                cropped_images, f"{base_name}_plate_{idx}.jpg")

            cv2.imwrite(save_path, cropped_plate)
            print(f"Saved cropped plate to {save_path}")

print("Preprocess Done")
