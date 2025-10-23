"""
Vercel Serverless Function - Process Translation Job
This function actually performs the translation work
Can be triggered via webhook or direct call
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import tempfile
from supabase import create_client, Client
from excel_translator import convert_xls_to_xlsx, translate_excel_with_format

# Initialize Supabase client (strip any whitespace/newlines)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def update_job_progress(job_id: str, current: int, total: int, message: str):
    """Update job progress in database"""
    try:
        supabase.table("translation_jobs").update({
            "current_cell": current,
            "total_cells": total,
            "progress_message": message,
            "status": "processing"
        }).eq("id", job_id).execute()
    except Exception as e:
        print(f"Failed to update progress: {e}")


def process_translation_job(job_id: str):
    """Process a translation job"""
    try:
        # Fetch job details from database
        result = supabase.table("translation_jobs").select("*").eq("id", job_id).single().execute()
        job = result.data

        if not job:
            raise Exception(f"Job {job_id} not found")

        if job['status'] != 'pending':
            raise Exception(f"Job {job_id} is not in pending state")

        # Update status to processing
        supabase.table("translation_jobs").update({
            "status": "processing",
            "progress_message": "Starting translation..."
        }).eq("id", job_id).execute()

        # Download input file from Supabase Storage
        input_path = job['input_file_path']
        file_data = supabase.storage.from_("excel-files").download(input_path)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(job['original_filename'])[1]) as temp_input:
            temp_input.write(file_data)
            temp_input_path = temp_input.name

        # Convert .xls to .xlsx if needed
        converted_path = temp_input_path
        if temp_input_path.endswith('.xls'):
            converted_path = convert_xls_to_xlsx(temp_input_path)

        # Prepare output file path
        output_filename = f"translated_{os.path.splitext(job['original_filename'])[0]}.xlsx"
        temp_output_path = tempfile.mktemp(suffix='.xlsx')

        # Define progress callback
        def progress_callback(current, total, message):
            update_job_progress(job_id, current, total, message)

        # Perform translation
        translate_excel_with_format(
            converted_path,
            temp_output_path,
            job['source_lang'],
            job['target_lang'],
            progress_callback
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

        return True

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

        raise e


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            job_id = data.get('job_id')
            if not job_id:
                self.send_error_response(400, "Missing job_id")
                return

            # Process the translation job
            process_translation_job(job_id)

            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "success": True,
                "job_id": job_id,
                "message": "Translation completed successfully"
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
