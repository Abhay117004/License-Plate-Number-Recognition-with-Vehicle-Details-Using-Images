import os
import sys


def run_program():
    """Executes the entire image processing pipeline in sequence."""
    print("--- Starting Pipeline ---")

    python_executable = sys.executable

    print("\n--- Running Preprocessing (Plate Detection) ---")
    os.system(f"{python_executable} preprocess_plate.py")

    print("\n--- Running OCR (Text Extraction) ---")
    os.system(f"{python_executable} ocr.py")

    print("\n--- Running API Call (Vehicle Details) ---")
    os.system(f"{python_executable} api_call.py")

    print("\n--- Pipeline Finished ---")


if __name__ == "__main__":
    run_program()
