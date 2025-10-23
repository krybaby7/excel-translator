"""
Vercel Serverless Function - Download Translated File
Returns the translated file from Supabase Storage
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract job_id from path: /api/download?job_id=xxx
            parsed_path = urlparse(self.path)
            query = parsed_path.query
            params = dict(qc.split("=") for qc in query.split("&")) if query else {}

            job_id = params.get('job_id')
            if not job_id:
                self.send_error_response(400, "Missing job_id parameter")
                return

            # Fetch job details from database
            result = supabase.table("translation_jobs").select("*").eq("id", job_id).single().execute()
            job = result.data

            if not job:
                self.send_error_response(404, "Job not found")
                return

            if job['status'] != 'complete':
                self.send_error_response(400, f"Job is not complete. Current status: {job['status']}")
                return

            output_path = job['output_file_path']
            if not output_path:
                self.send_error_response(404, "Output file not found")
                return

            # Download file from Supabase Storage
            try:
                file_data = supabase.storage.from_("excel-files").download(output_path)
            except Exception as e:
                self.send_error_response(500, f"Failed to download file: {str(e)}")
                return

            # Send file response
            output_filename = f"translated_{job['original_filename'].replace('.xls', '.xlsx')}"

            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{output_filename}"')
            self.send_header('Content-Length', str(len(file_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(file_data)

            # Optional: Schedule cleanup of files after successful download
            # This could be done via a separate cleanup function

        except Exception as e:
            self.send_error_response(500, str(e))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_error_response(self, code, message):
        """Helper to send error responses"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
