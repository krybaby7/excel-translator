"""
Vercel Serverless Function - Start Translation
Accepts file upload and initiates translation job
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import uuid
import requests
import base64

# Initialize Supabase connection (strip any whitespace/newlines)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, "No file provided")
                return

            # Read the body
            body = self.rfile.read(content_length)

            # Parse multipart form data (simplified - in production use a library)
            # For now, we'll expect JSON with base64 encoded file
            try:
                data = json.loads(body)
                filename = data.get('filename')
                file_content = base64.b64decode(data.get('file'))
                source_lang = data.get('source_lang', 'fr')
                target_lang = data.get('target_lang', 'en')
            except:
                self.send_error_response(400, "Invalid request format. Expected JSON with base64 file.")
                return

            if not filename or not file_content:
                self.send_error_response(400, "Missing filename or file content")
                return

            # Validate file extension
            if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
                self.send_error_response(400, "Only .xls and .xlsx files are supported")
                return

            # Generate unique job ID
            job_id = str(uuid.uuid4())
            input_path = f"input/{job_id}/{filename}"

            # Upload file to Supabase Storage using REST API
            try:
                storage_url = f"{SUPABASE_URL}/storage/v1/object/excel-files/{input_path}"
                headers = {
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }

                upload_response = requests.post(storage_url, data=file_content, headers=headers)

                if upload_response.status_code not in [200, 201]:
                    raise Exception(f"Storage upload failed: {upload_response.text}")

            except Exception as e:
                self.send_error_response(500, f"Failed to upload file: {str(e)}")
                return

            # Create translation job record in database using REST API
            try:
                job_data = {
                    "id": job_id,
                    "original_filename": filename,
                    "input_file_path": input_path,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "status": "pending",
                    "file_size": len(file_content),
                    "progress_message": "Queued for translation..."
                }

                db_url = f"{SUPABASE_URL}/rest/v1/translation_jobs"
                headers = {
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "apikey": SUPABASE_KEY,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }

                db_response = requests.post(db_url, json=job_data, headers=headers)

                if db_response.status_code not in [200, 201]:
                    # Clean up uploaded file if DB insert fails
                    requests.delete(storage_url, headers={"Authorization": f"Bearer {SUPABASE_KEY}"})
                    raise Exception(f"Database insert failed: {db_response.text}")

            except Exception as e:
                self.send_error_response(500, f"Failed to create job: {str(e)}")
                return

            # Send success response
            self.send_response(202)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "task_id": job_id,
                "status": "queued",
                "message": "Translation job created successfully"
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error_response(500, str(e))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_error_response(self, code, message):
        """Helper to send error responses"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
