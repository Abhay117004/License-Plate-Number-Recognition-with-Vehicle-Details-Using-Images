import os


def clear_images():
    folders = ["input_images", "cropped_images", "ocr_results", "api_results"]
    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    print("Cleared successfully")


if __name__ == "__main__":
    clear_images()
