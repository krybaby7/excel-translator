# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - Project name: `excel-translator`
   - Database password: (generate a strong password and save it)
   - Region: Choose closest to your users
5. Wait for project to be created (2-3 minutes)

## Step 2: Configure Storage Buckets

1. In your Supabase dashboard, go to **Storage** in the left sidebar
2. Click **Create a new bucket**
3. Create bucket named: `excel-files`
4. Settings:
   - Public bucket: **No** (keep private)
   - File size limit: 50 MB
   - Allowed MIME types: Leave empty (allow all) or add:
     - `application/vnd.ms-excel`
     - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
5. Click **Create bucket**

## Step 3: Set Up Storage Policies

Go to **Storage > Policies** and add these policies for the `excel-files` bucket:

### Policy 1: Allow Authenticated Uploads
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'excel-files');
```

### Policy 2: Allow Public Downloads (or authenticated if you prefer)
```sql
CREATE POLICY "Allow public downloads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'excel-files');
```

**OR** for authenticated-only downloads:
```sql
CREATE POLICY "Allow authenticated downloads"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'excel-files');
```

### Policy 3: Allow Authenticated Deletes
```sql
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'excel-files');
```

## Step 4: Create Database Schema

1. Go to **SQL Editor** in the left sidebar
2. Copy and paste the SQL from `supabase-schema.sql`
3. Click **Run** to execute

## Step 5: Get Your Credentials

1. Go to **Settings > API** in the left sidebar
2. Copy these values (you'll need them for `.env` file):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Project API Key** (anon/public): `eyJhbG...`
   - **Service Role Key** (keep secret!): `eyJhbG...`

## Step 6: Enable Realtime (for progress tracking)

1. Go to **Database > Replication** in the left sidebar
2. Find the `translation_jobs` table
3. Click the toggle to enable Realtime for this table

## Step 7: Create Environment Variables File

Create a `.env` file in your project root with:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_KEY=eyJhbG...
```

**IMPORTANT**: Add `.env` to your `.gitignore` to keep credentials secure!

## Step 8: Test Connection (Optional)

You can test the connection by running:

```bash
pip install supabase
python test_supabase_connection.py
```

Your Supabase backend is now ready!
