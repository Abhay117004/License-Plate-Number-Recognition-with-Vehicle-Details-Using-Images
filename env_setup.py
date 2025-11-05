import os
from ultralytics import YOLO
from dotenv import load_dotenv

print("Setting up environment...")
# load_dotenv() is still good for local testing
load_dotenv()

# --- PATHS ---
# Vercel/Render are read-only, except for /tmp
# We will use /tmp for all file operations.
BASE_DIR = '/tmp'
input_folder = os.path.join(BASE_DIR, 'input_images')
cropped_images = os.path.join(BASE_DIR, 'cropped_images')
ocr_results_folder = os.path.join(BASE_DIR, 'ocr_results')
api_results_folder = os.path.join(BASE_DIR, 'api_results')

# Create all directories on startup
for folder in [input_folder, cropped_images, ocr_results_folder, api_results_folder]:
    os.makedirs(folder, exist_ok=True)

print(f"Using input folder: {input_folder}")
print(f"Using cropped folder: {cropped_images}")
print(f"Using OCR results folder: {ocr_results_folder}")
print(f"Using API results folder: {api_results_folder}")


device = "cpu"
model_path = "best.pt"

if not os.path.exists(model_path):
    app_model_path = os.path.join("/app", model_path)
    if os.path.exists(app_model_path):
        model_path = app_model_path
    else:
        print(
            f"CRITICAL WARNING: YOLO model 'best.pt' not found at {model_path} or {app_model_path}")

print(f"Loading YOLO model from: {model_path}")
try:
    model = YOLO(model_path)
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load YOLO model. {e}")
    model = None


# --- API KEYS ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set.")

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if not RAPIDAPI_KEY:
    print("Warning: RAPIDAPI_KEY environment variable not set.")

print("Environment setup complete.")
