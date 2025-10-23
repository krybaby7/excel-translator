# How to Test Locally with Supabase Backend

Your Excel Translator now has **three versions** you can run:

---

## Option 1: Flask + Supabase Backend (Recommended for Testing)

**Best for**: Testing the full cloud architecture locally before deploying to Vercel

### What It Does:
- **Backend**: Flask API running on your computer
- **Storage**: Supabase Storage (cloud) - files stored in your `excel-files` bucket
- **Database**: Supabase PostgreSQL (cloud) - jobs tracked in `translation_jobs` table
- **Progress**: Server-Sent Events (SSE) reading from Supabase database
- **Frontend**: Uses `app.js` (original JavaScript)

### How to Run:

```bash
# Start the Flask app with Supabase backend
python app_supabase.py

# Open in browser
# http://localhost:5000
```

### What Happens:
1. Upload Excel file → Stored in Supabase Storage
2. Job created → Recorded in Supabase database
3. Translation happens → Progress updated in database
4. Download file → Retrieved from Supabase Storage
5. Files remain in Supabase for 24 hours (auto-cleanup)

### Verify It's Working:
- Visit http://localhost:5000/health
- Should see: `{"status": "healthy", "supabase": "connected"}`
- Check Supabase Dashboard → Storage to see uploaded files
- Check Supabase Dashboard → Database to see job records

---

## Option 2: Original Local Version (No Cloud)

**Best for**: Testing without internet or Supabase

### What It Does:
- **Backend**: Flask API (local)
- **Storage**: Temporary files on disk
- **Database**: In-memory dictionaries
- **Progress**: Server-Sent Events (SSE)
- **Frontend**: Uses `app.js`

### How to Run:

```bash
# Start the original Flask app
python app.py

# Open in browser
# http://localhost:5000
```

### What Happens:
- Everything runs locally
- Files stored in temp folders
- No cloud dependencies
- Files deleted after download

---

## Option 3: Cloud Version (For After Deployment)

**Best for**: After deploying to Vercel

### What It Does:
- **Backend**: Vercel serverless functions
- **Storage**: Supabase Storage
- **Database**: Supabase PostgreSQL
- **Progress**: Supabase Realtime (live updates!)
- **Frontend**: Uses `app-cloud.js`

### How to Access:
- Your Vercel URL: `https://excel-translator-xxxxx.vercel.app`

---

## Comparison

| Feature | app.py (Local) | app_supabase.py (Hybrid) | Vercel (Cloud) |
|---------|----------------|--------------------------|----------------|
| **Backend** | Flask (local) | Flask (local) | Serverless |
| **Storage** | Temp files | Supabase Storage | Supabase Storage |
| **Database** | In-memory | Supabase PostgreSQL | Supabase PostgreSQL |
| **Progress** | SSE | SSE from DB | Realtime |
| **Internet needed** | No | Yes | Yes |
| **Files persist** | No | Yes (24h) | Yes (24h) |
| **Test cloud setup** | No | Yes ✓ | N/A (production) |

---

## Testing Workflow

### 1. Start with app_supabase.py
```bash
python app_supabase.py
```

### 2. Upload a Test File
- Go to http://localhost:5000
- Upload a small Excel file (.xlsx)
- Select languages (e.g., French → English)
- Click "Translate"

### 3. Monitor in Supabase Dashboard

**Check Storage:**
1. Go to: https://supabase.com/dashboard/project/miodbpwlebiidcvrlvmc/storage/buckets
2. Click on `excel-files` bucket
3. You should see folders:
   - `input/{job-id}/` - Original file
   - `output/{job-id}/` - Translated file

**Check Database:**
1. Go to: https://supabase.com/dashboard/project/miodbpwlebiidcvrlvmc/editor
2. Click on `translation_jobs` table
3. You should see your job record with:
   - Status: pending → processing → complete
   - Progress updates in real-time
   - File paths stored

### 4. Download Result
- Click "Download Translated File"
- File should download from Supabase Storage
- Open and verify translation worked

### 5. Verify Everything
✓ File uploaded to Supabase Storage
✓ Job tracked in Supabase Database
✓ Translation completed successfully
✓ File downloaded from cloud
✓ Files remain in Supabase (until 24h expiry)

---

## Troubleshooting

### Server won't start
**Error**: `Missing Supabase credentials`
**Fix**: Make sure `.env` file exists with:
```env
SUPABASE_URL=https://miodbpwlebiidcvrlvmc.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### Health check fails
**Error**: `"supabase": "error"`
**Fix**:
1. Check internet connection
2. Verify Supabase credentials in `.env`
3. Test connection: `python test_supabase_connection.py`

### File upload fails
**Error**: `Failed to upload file`
**Fix**:
1. Check `excel-files` bucket exists in Supabase
2. Verify storage policies are set
3. Check file size (max 16MB)

### Translation times out
**Issue**: Large files taking too long
**Solution**:
- Start with small test files (< 100KB)
- Large files work but take longer locally

### Can't see files in Supabase
**Check**:
1. Correct bucket name: `excel-files`
2. Files are under `input/` and `output/` folders
3. Refresh the Supabase Storage page

---

## Development Tips

### Watch Database Changes in Real-Time
1. Open Supabase Dashboard → SQL Editor
2. Run:
```sql
SELECT id, status, progress_percentage, progress_message, original_filename
FROM translation_jobs
ORDER BY created_at DESC
LIMIT 10;
```
3. Refresh while translation is running

### Clean Up Old Jobs
```sql
-- Delete old test jobs
DELETE FROM translation_jobs
WHERE created_at < NOW() - INTERVAL '1 hour';
```

### Clean Up Storage Files
1. Go to Storage → excel-files
2. Select folders
3. Click Delete

---

## Next Steps

Once local testing works:

1. ✓ Local testing successful
2. → Deploy to Vercel (`vercel`)
3. → Add environment variables to Vercel
4. → Test live deployment
5. → Share with users!

---

## Quick Reference

### Start Testing:
```bash
python app_supabase.py
```

### Check Health:
```bash
curl http://localhost:5000/health
```

### View Logs:
- Terminal shows Flask logs
- Supabase Dashboard shows DB queries

### Stop Server:
- Press `Ctrl+C` in terminal

---

## Files Used

- `app_supabase.py` - Flask app with Supabase backend
- `templates/index_local.html` - HTML for local testing
- `static/js/app.js` - Frontend JavaScript (SSE)
- `.env` - Supabase credentials
- `excel_translator.py` - Core translation logic

---

## Summary

**app_supabase.py** lets you:
- ✓ Test Supabase integration locally
- ✓ Verify file storage works
- ✓ Verify database tracking works
- ✓ Debug issues before deployment
- ✓ Keep Flask's familiar API
- ✓ Avoid deploying broken code

**Perfect for local development and testing before going live on Vercel!**

---

*Ready to test? Run:* `python app_supabase.py`
