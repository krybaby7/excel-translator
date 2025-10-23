"""
Flask API for Excel Translator
"""
from flask import Flask, request, send_file, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
from excel_translator import convert_xls_to_xlsx, translate_excel_with_format
import os
import tempfile
import shutil
import json
import uuid
from threading import Thread
from queue import Queue

app = Flask(__name__)

# Configure CORS for development
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store progress for active translations
translation_progress = {}  # {task_id: {"current": 0, "total": 0, "message": "", "status": "processing"}}
translation_results = {}  # {task_id: output_path}


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Excel Translator"}), 200


@app.route('/translate', methods=['POST'])
def translate():
    """
    Start translation and return a task ID for progress tracking
    Expected parameters:
    - file: Excel file (.xls or .xlsx)
    - source_lang: source language code (default: 'fr')
    - target_lang: target language code (default: 'en')
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Get language parameters
        source_lang = request.form.get('source_lang', 'fr')
        target_lang = request.form.get('target_lang', 'en')

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Initialize progress tracking
        translation_progress[task_id] = {
            "current": 0,
            "total": 0,
            "message": "Starting translation...",
            "status": "processing"
        }

        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)

        # Start translation in background thread
        def translate_task():
            try:
                # Convert .xls to .xlsx if needed
                converted_path = input_path
                if input_path.endswith('.xls'):
                    converted_path = convert_xls_to_xlsx(input_path)

                if not converted_path.endswith('.xlsx'):
                    translation_progress[task_id] = {
                        "current": 0,
                        "total": 0,
                        "message": "Unsupported file format",
                        "status": "error"
                    }
                    return

                # Translate the file with progress callback
                output_path = os.path.join(temp_dir, f"translated_{os.path.basename(converted_path)}")

                def progress_callback(current, total, message):
                    translation_progress[task_id] = {
                        "current": current,
                        "total": total,
                        "message": message,
                        "status": "processing"
                    }

                translate_excel_with_format(converted_path, output_path, source_lang, target_lang, progress_callback)

                # Store result
                translation_results[task_id] = {
                    "output_path": output_path,
                    "temp_dir": temp_dir,
                    "filename": file.filename
                }

                translation_progress[task_id] = {
                    "current": 100,
                    "total": 100,
                    "message": "Translation complete!",
                    "status": "complete"
                }

            except Exception as e:
                translation_progress[task_id] = {
                    "current": 0,
                    "total": 0,
                    "message": f"Error: {str(e)}",
                    "status": "error"
                }
                # Clean up on error
                shutil.rmtree(temp_dir, ignore_errors=True)

        thread = Thread(target=translate_task)
        thread.daemon = True
        thread.start()

        return jsonify({"task_id": task_id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/progress/<task_id>', methods=['GET'])
def get_progress_stream(task_id):
    """Stream progress updates using Server-Sent Events"""
    def generate():
        try:
            while True:
                if task_id not in translation_progress:
                    yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                    break

                progress_data = translation_progress[task_id]
                yield f"data: {json.dumps(progress_data)}\n\n"

                # Stop streaming if complete or error
                if progress_data["status"] in ["complete", "error"]:
                    break

                # Small delay to avoid overwhelming the client
                import time
                time.sleep(0.5)

        except GeneratorExit:
            pass

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/download/<task_id>', methods=['GET'])
def download_result(task_id):
    """Download the translated file"""
    try:
        if task_id not in translation_results:
            return jsonify({"error": "Translation not found or not complete"}), 404

        result = translation_results[task_id]
        output_path = result["output_path"]
        temp_dir = result["temp_dir"]
        filename = result["filename"]

        # Remove any existing extension and ensure .xlsx
        base_name = os.path.splitext(filename)[0]

        response = send_file(
            output_path,
            as_attachment=True,
            download_name=f"translated_{base_name}.xlsx"
        )

        # Clean up after sending
        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                # Clean up tracking data
                if task_id in translation_progress:
                    del translation_progress[task_id]
                if task_id in translation_results:
                    del translation_results[task_id]
            except:
                pass

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """Return list of commonly supported languages"""
    languages = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh-CN": "Chinese (Simplified)",
        "ar": "Arabic",
        "hi": "Hindi"
    }
    return jsonify(languages), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
