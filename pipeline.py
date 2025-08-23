import os


def run_program():
    os.system("python env_setup.py")
    os.system("python preprocess_plate.py")
    os.system("python ocr.py")
    os.system("python api_call.py")


if __name__ == "__main__":
    run_program()
