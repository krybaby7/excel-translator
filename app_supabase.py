"""
Flask API for Excel Translator with Supabase Backend
This version uses Supabase for storage and database while keeping Flask for the API
Perfect for local testing before deploying to Vercel
"""
from flask import Flask, request, send_file, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
from excel_translator_optimized import convert_xls_to_xlsx, translate_excel_with_format
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import tempfile
import json
import uuid
from threading import Thread
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for development
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials in .env file!")
    print("Please ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"Connected to Supabase: {SUPABASE_URL}")


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index_local.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Supabase connection
        result = supabase.table("translation_jobs").select("count").limit(1).execute()
        return jsonify({
            "status": "healthy",
            "service": "Excel Translator (Supabase Backend)",
            "supabase": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "Excel Translator (Supabase Backend)",
            "error": str(e)
        }), 500


@app.route('/translate', methods=['POST'])
def translate():
    """
    Start translation using Supabase backend
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

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Read file content
        file_content = file.read()
        file_size = len(file_content)

        # Upload file to Supabase Storage
        input_path = f"input/{job_id}/{file.filename}"
        try:
            supabase.storage.from_("excel-files").upload(
                input_path,
                file_content,
                file_options={
                    "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
            )
        except Exception as e:
            return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500

        # Create job record in Supabase database
        job_data = {
            "id": job_id,
            "original_filename": file.filename,
            "input_file_path": input_path,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "status": "pending",
            "file_size": file_size,
            "progress_message": "Starting translation..."
        }

        try:
            supabase.table("translation_jobs").insert(job_data).execute()
        except Exception as e:
            # Clean up uploaded file if DB insert fails
            supabase.storage.from_("excel-files").remove([input_path])
            return jsonify({"error": f"Failed to create job: {str(e)}"}), 500

        # Start translation in background thread
        def translate_task():
            try:
                # Update status to processing
                supabase.table("translation_jobs").update({
                    "status": "processing",
                    "progress_message": "Downloading file..."
                }).eq("id", job_id).execute()

                # Download file from Supabase Storage
                file_data = supabase.storage.from_("excel-files").download(input_path)

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_input:
                    temp_input.write(file_data)
                    temp_input_path = temp_input.name

                # Convert .xls to .xlsx if needed
                converted_path = temp_input_path
                if temp_input_path.endswith('.xls'):
                    supabase.table("translation_jobs").update({
                        "progress_message": "Converting .xls to .xlsx..."
                    }).eq("id", job_id).execute()
                    converted_path = convert_xls_to_xlsx(temp_input_path)

                if not converted_path.endswith('.xlsx'):
                    supabase.table("translation_jobs").update({
                        "status": "error",
                        "error_message": "Unsupported file format"
                    }).eq("id", job_id).execute()
                    os.unlink(temp_input_path)
                    return

                # Prepare output file path
                output_filename = f"translated_{os.path.splitext(file.filename)[0]}.xlsx"
                temp_output_path = tempfile.mktemp(suffix='.xlsx')

                # Define progress callback
                def progress_callback(current, total, message):
                    supabase.table("translation_jobs").update({
                        "current_cell": current,
                        "total_cells": total,
                        "progress_message": message,
                        "status": "processing"
                    }).eq("id", job_id).execute()

                # Perform translation WITH OPTIMIZATIONS
                # batch_size=10 means update database every 10 cells (not every cell!)
                # parallel=True enables parallel translation (not yet implemented fully)
                translate_excel_with_format(
                    converted_path,
                    temp_output_path,
                    source_lang,
                    target_lang,
                    progress_callback,
                    batch_size=10,
                    parallel=False  # Keep False for now (single-threaded is safer)
                )

                # Upload translated file to Supabase Storage
                output_path = f"output/{job_id}/{output_filename}"
                with open(temp_output_path, 'rb') as f:
                    supabase.storage.from_("excel-files").upload(
                        output_path,
                        f.read(),
                        file_options={
                            "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        }
                    )

                # Update job as complete
                supabase.table("translation_jobs").update({
                    "status": "complete",
                    "output_file_path": output_path,
                    "progress_message": "Translation complete!",
                    "current_cell": 100,
                    "total_cells": 100
                }).eq("id", job_id).execute()

                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    if converted_path != temp_input_path:
                        os.unlink(converted_path)
                    os.unlink(temp_output_path)
                except:
                    pass

            except Exception as e:
                # Update job as error
                try:
                    supabase.table("translation_jobs").update({
                        "status": "error",
                        "error_message": str(e),
                        "progress_message": f"Error: {str(e)}"
                    }).eq("id", job_id).execute()
                except:
                    pass
                print(f"Translation error: {e}")

        thread = Thread(target=translate_task)
        thread.daemon = True
        thread.start()

        return jsonify({"task_id": job_id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/progress/<task_id>', methods=['GET'])
def get_progress_stream(task_id):
    """Stream progress updates using Server-Sent Events from Supabase"""
    def generate():
        try:
            max_iterations = 240  # 2 minutes max (240 * 0.5s)
            iterations = 0

            while iterations < max_iterations:
                try:
                    # Fetch job status from Supabase
                    result = supabase.table("translation_jobs").select(
                        "status, current_cell, total_cells, progress_message, error_message"
                    ).eq("id", task_id).single().execute()

                    if not result.data:
                        yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                        break

                    job = result.data
                    progress_data = {
                        "current": job['current_cell'],
                        "total": job['total_cells'],
                        "message": job['progress_message'],
                        "status": job['status']
                    }

                    if job['status'] == 'error':
                        progress_data['message'] = job.get('error_message', 'Unknown error')

                    yield f"data: {json.dumps(progress_data)}\n\n"

                    # Stop streaming if complete or error
                    if job['status'] in ['complete', 'error']:
                        break

                except Exception as e:
                    print(f"Error fetching progress: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    break

                time.sleep(0.5)
                iterations += 1

        except GeneratorExit:
            pass

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/download/<task_id>', methods=['GET'])
def download_result(task_id):
    """Download the translated file from Supabase Storage"""
    try:
        # Fetch job details from database
        result = supabase.table("translation_jobs").select("*").eq("id", task_id).single().execute()

        if not result.data:
            return jsonify({"error": "Translation not found"}), 404

        job = result.data

        if job['status'] != 'complete':
            return jsonify({"error": f"Job is not complete. Current status: {job['status']}"}), 400

        output_path = job['output_file_path']
        if not output_path:
            return jsonify({"error": "Output file not found"}), 404

        # Download file from Supabase Storage
        try:
            file_data = supabase.storage.from_("excel-files").download(output_path)
        except Exception as e:
            return jsonify({"error": f"Failed to download file: {str(e)}"}), 500

        # Save to temporary file and send
        output_filename = f"translated_{job['original_filename'].replace('.xls', '.xlsx')}"

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name

        response = send_file(
            temp_file_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Clean up after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(temp_file_path)
                # Optional: Clean up Supabase files (commented out to keep for 24 hours)
                # supabase.storage.from_("excel-files").remove([job['input_file_path'], output_path])
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
    print("=" * 60)
    print("Excel Translator with Supabase Backend")
    print("=" * 60)
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Server starting on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
