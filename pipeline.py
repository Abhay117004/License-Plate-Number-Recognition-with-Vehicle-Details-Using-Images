import os
import sys


def run_program():
    python_executable = sys.executable
    os.system(f"{python_executable} preprocess_plate.py")
    os.system(f"{python_executable} ocr.py")
    os.system(f"{python_executable} api_call.py")


if __name__ == "__main__":
    run_program()
