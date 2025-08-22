from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import subprocess
import sys
import webbrowser

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'input_images')
CROPPED_FOLDER = os.path.join(BASE_DIR, 'cropped_images')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


# Add static file serving for CSS and JS files
@app.route('/styles.css')
def serve_css():
    return send_from_directory('templates', 'styles.css')


@app.route('/script.js')
def serve_js():
    return send_from_directory('templates', 'script.js')


@app.route('/<path:filename>')
def serve_uploaded_file(filename):
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    if filename.lower().endswith(allowed_extensions):
        return send_from_directory('uploads', filename)
    return "File not found", 404


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'message': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    from werkzeug.utils import secure_filename
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(file_path)

    return jsonify({'message': f'Image saved to {file_path}'}), 200


@app.route('/run-ocr', methods=['POST'])
def run_ocr():
    try:
        result = subprocess.run(
            [sys.executable, 'pipeline.py'], capture_output=True, text=True)
        folders = [UPLOAD_FOLDER, CROPPED_FOLDER]
        for folder in folders:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    file_path = os.path.join(folder, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

        return jsonify({'message': result.stdout if result.stdout else 'OCR completed successfully'})
    except Exception as e:
        return jsonify({'message': f'OCR execution failed: {str(e)}'}), 500


@app.route('/clear-images', methods=['POST'])
def clear_images():
    try:
        folders = [UPLOAD_FOLDER, CROPPED_FOLDER]
        for folder in folders:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    file_path = os.path.join(folder, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        return jsonify({'message': 'Cleared successfully'})
    except Exception as e:
        return jsonify({'message': f'Failed to clear images: {str(e)}'}), 500


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=True, use_reloader=False)
