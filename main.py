import os
import sys
import json
import glob
import shutil
import webbrowser
import subprocess
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Vercel has a read-only filesystem, except for the /tmp directory.
# We will use the /tmp directory for all file operations.
BASE_DIR = '/tmp'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'input_images')
CROPPED_FOLDER = os.path.join(BASE_DIR, 'cropped_images')
OCR_RESULTS_DIR = os.path.join(BASE_DIR, 'ocr_results')
API_RESULTS_DIR = os.path.join(BASE_DIR, 'api_results')

# Ensure the app object is discoverable by Vercel's WSGI server
app = Flask(__name__)

for folder in [UPLOAD_FOLDER, CROPPED_FOLDER, OCR_RESULTS_DIR, API_RESULTS_DIR]:
    os.makedirs(folder, exist_ok=True)


@app.route('/')
def home():
    # Adjust template path for Vercel environment
    template_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'templates', 'index.html')
    return render_template(template_path)


@app.route('/styles.css')
def serve_css():
    # Adjust static file path for Vercel environment
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), 'styles.css')


@app.route('/script.js')
def serve_js():
    # Adjust static file path for Vercel environment
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), 'script.js')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({'message': f'Image {filename} uploaded successfully.'}), 200
    return jsonify({'error': 'Unknown error during upload'}), 500


@app.route('/run-ocr', methods=['POST'])
def run_ocr():
    try:
        result = subprocess.run(
            [sys.executable, 'pipeline.py'],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        print("Pipeline STDOUT:", result.stdout)
        if result.stderr:
            print("Pipeline STDERR:", result.stderr)

        all_details = []
        if os.path.exists(API_RESULTS_DIR):
            for filename in glob.glob(os.path.join(API_RESULTS_DIR, "*.json")):
                with open(filename, 'r') as f:
                    all_details.append(json.load(f))

        return jsonify(all_details)

    except subprocess.CalledProcessError as e:
        log_output = e.stdout + "\n" + e.stderr
        print(f"Error during pipeline execution: {log_output}")
        return jsonify({"error": "Failed to process image."}), 500
    except Exception as e:
        print(f"An error occurred in /run-ocr: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clear-images', methods=['POST'])
def clear_images_route():
    try:
        folders_to_clear = [UPLOAD_FOLDER, CROPPED_FOLDER,
                            OCR_RESULTS_DIR, API_RESULTS_DIR]
        for folder in folders_to_clear:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                os.makedirs(folder)
        return jsonify({'message': 'Cleared all temporary images and results successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # The host must be set to '0.0.0.0' to be accessible from outside the container
    app.run(host='0.0.0.0', port=5000, debug=False)
