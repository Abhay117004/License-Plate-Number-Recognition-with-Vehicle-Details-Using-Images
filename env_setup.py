import os
from ultralytics import YOLO
from openai import OpenAI

input_folder = "input_images"
cropped_images = "cropped_images"
os.makedirs(cropped_images, exist_ok=True)

device = "cpu"

model = YOLO("best.pt")

MOONDREAM_API_KEY = os.getenv("MOONDREAM_API_KEY")
client = OpenAI(api_key=MOONDREAM_API_KEY,
                base_url="https://api.moondream.ai/v1")

print("Setup Done")
