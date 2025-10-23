"""
Vercel Serverless Function - Get Job Status
Returns current status and progress of a translation job
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
            # Extract job_id from path: /api/status?job_id=xxx
            parsed_path = urlparse(self.path)
            query = parsed_path.query
            params = dict(qc.split("=") for qc in query.split("&")) if query else {}

            job_id = params.get('job_id')
            if not job_id:
                self.send_error_response(400, "Missing job_id parameter")
                return

            # Fetch job details from database
            result = supabase.table("translation_jobs").select(
                "id, status, current_cell, total_cells, progress_percentage, progress_message, error_message, created_at, updated_at"
            ).eq("id", job_id).single().execute()

            job = result.data

            if not job:
                self.send_error_response(404, "Job not found")
                return

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "job_id": job['id'],
                "status": job['status'],
                "current": job['current_cell'],
                "total": job['total_cells'],
                "percentage": job['progress_percentage'],
                "message": job['progress_message'],
                "error": job['error_message'],
                "created_at": job['created_at'],
                "updated_at": job['updated_at']
            }

            self.wfile.write(json.dumps(response).encode())

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
