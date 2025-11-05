import os
import sys


def run_program(base_filename):
    python_executable = sys.executable
    # Pass the base filename to each script
    os.system(f"{python_executable} preprocess_plate.py {base_filename}")
    os.system(f"{python_executable} ocr.py {base_filename}")
    os.system(f"{python_executable} api_call.py {base_filename}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_filename_arg = sys.argv[1]
        run_program(base_filename_arg)
    else:
        print("Error: No base filename provided to pipeline.py.")
        # Fallback for direct execution (optional)
        # run_program(None)
