import os
from ultralytics import YOLO
from dotenv import load_dotenv

print("Setting up environment...")
load_dotenv()
input_folder = "input_images"
cropped_images = "cropped_images"

os.makedirs(cropped_images, exist_ok=True)

device = "cpu"

model = YOLO("best.pt")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set.")

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if not RAPIDAPI_KEY:
    print("Warning: RAPIDAPI_KEY environment variable not set.")

print("Environment setup complete.")
