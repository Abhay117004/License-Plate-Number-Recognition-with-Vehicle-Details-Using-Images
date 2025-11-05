import os
import sys
import json
import glob
import shutil
import subprocess
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

try:
    from env_setup import (
        input_folder,
        cropped_images,
        ocr_results_folder,
        api_results_folder
    )
except ImportError as e:
    print(f"CRITICAL: Failed to import env_setup. {e}")
    sys.exit(1)


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/styles.css')
def serve_css():
    return send_from_directory('templates', 'styles.css')


@app.route('/script.js')
def serve_js():
    return send_from_directory('templates', 'script.js')


last_uploaded_filename = None


@app.route('/upload', methods=['POST'])
def upload_image():
    global last_uploaded_filename
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'}), 400
    if file:
        filename = secure_filename(file.filename)
        # Use the imported path
        file_path = os.path.join(input_folder, filename)
        file.save(file_path)
        print(f"Image saved to: {file_path}")

        last_uploaded_filename = os.path.splitext(filename)[0]
        return jsonify({'message': f'Image {filename} uploaded successfully.'}), 200
    return jsonify({'error': 'Unknown error during upload'}), 500


@app.route('/run-ocr', methods=['POST'])
def run_ocr():
    if not last_uploaded_filename:
        print("Error: /run-ocr called but last_uploaded_filename is not set.")
        return jsonify({"error": "No image has been uploaded yet."}), 400

    print(f"Running pipeline for: {last_uploaded_filename}")
    try:
        # Pass the base filename to the pipeline
        result = subprocess.run(
            [sys.executable, 'pipeline.py', last_uploaded_filename],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        print("Pipeline STDOUT:", result.stdout)
        if result.stderr:
            print("Pipeline STDERR:", result.stderr)

        all_details = []
        # Look for results in the correct directory
        search_path = os.path.join(
            api_results_folder, f"{last_uploaded_filename}*.json")
        print(f"Searching for results in: {search_path}")

        result_files = glob.glob(search_path)
        if not result_files:
            print("No API result JSON files found.")
            return jsonify({"error": "No vehicle details found."}), 200

        for filename in result_files:
            with open(filename, 'r') as f:
                all_details.append(json.load(f))

        print(f"Found {len(all_details)} result(s).")
        return jsonify(all_details)

    except subprocess.CalledProcessError as e:
        log_output = e.stdout + "\n" + e.stderr
        print(f"Error during pipeline execution: {log_output}")
        return jsonify({"error": "Failed to process image.", "log": log_output}), 500
    except Exception as e:
        print(f"An error occurred in /run-ocr: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clear-images', methods=['POST'])
def clear_images_route():
    print("Clear route triggered.")
    try:
        # Use the imported path variables
        folders_to_clear = [input_folder, cropped_images,
                            ocr_results_folder, api_results_folder]

        for folder in folders_to_clear:
            if os.path.exists(folder):
                print(f"Clearing folder: {folder}")
                shutil.rmtree(folder)
                os.makedirs(folder)

        global last_uploaded_filename
        last_uploaded_filename = None

        return jsonify({'message': 'Cleared all temporary images and results successfully'}), 200
    except Exception as e:
        print(f"Error clearing images: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
