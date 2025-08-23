import os
import cv2
import glob
from env_setup import model, input_folder, cropped_images


def preprocess_plate(image):
    enhanced = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    return enhanced


for image_path in glob.glob(os.path.join(input_folder, "*")):
    image = cv2.imread(image_path)
    results = model(image, verbose=False)
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    for idx, box in enumerate(results[0].boxes):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = image[y1:y2, x1:x2]
        cropped = preprocess_plate(cropped)
        cropped_path = os.path.join(
            cropped_images, f"{base_name}_plate_{idx}.jpg")
        cv2.imwrite(cropped_path, cropped)
        print(f"Saved cropped plate in --> {cropped_path}")

print("Preprocess Done")
