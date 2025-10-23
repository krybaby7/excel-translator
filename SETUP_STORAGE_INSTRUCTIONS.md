# Set Up Supabase Storage - Step by Step

## Quick Setup (5 minutes)

### Step 1: Create Storage Bucket

1. Go to: **https://supabase.com/dashboard/project/miodbpwlebiidcvrlvmc/storage/buckets**
2. Click **New bucket** button
3. Enter these settings:
   - **Name**: `excel-files`
   - **Public bucket**: Leave **UNCHECKED** (keep it private)
   - **File size limit**: `50 MB` (or leave default)
   - **Allowed MIME types**: Leave empty (allow all)
4. Click **Create bucket**

### Step 2: Set Storage Policies

1. After creating the bucket, click on the **excel-files** bucket
2. Click the **Policies** tab
3. Click **New policy**

**Policy 1: Allow Uploads**
```sql
CREATE POLICY "Allow uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'excel-files');
```

**Policy 2: Allow Downloads**
```sql
CREATE POLICY "Allow downloads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'excel-files');
```

**Policy 3: Allow Deletes**
```sql
CREATE POLICY "Allow deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'excel-files');
```

### Step 3: Verify Bucket

1. Go back to **Storage** in the left sidebar
2. You should see the `excel-files` bucket listed
3. Click on it - it should be empty (ready for files!)

---

## What This Does

- **excel-files bucket**: Stores input Excel files and translated output files
- **Upload policy**: Allows anyone to upload files (you can restrict this later with auth)
- **Download policy**: Allows anyone to download files
- **Delete policy**: Allows file cleanup after translation

---

## Alternative: Using Supabase Dashboard UI

If you prefer using the UI instead of SQL policies:

1. Go to **Storage** → **excel-files** bucket
2. Click **Policies** tab
3. Toggle these permissions:
   - ✅ **SELECT** (read files)
   - ✅ **INSERT** (upload files)
   - ✅ **DELETE** (remove files)
4. Set target to **public** (or **authenticated** if you add auth later)

---

## Troubleshooting

### Can't see Storage menu
- Make sure you're logged in
- Select your project: **ExcelTranslate**
- Look for "Storage" icon in left sidebar (looks like a folder)

### Policy creation fails
- Make sure the bucket is created first
- Use the exact bucket name: `excel-files`
- Check you're using the service_role key if doing this via API

### Bucket already exists
✅ That's fine! Just proceed to setting policies.

---

## Folder Structure (Automatic)

Your bucket will organize files like this:
```
excel-files/
├── input/
│   └── [job-id]/
│       └── original-file.xlsx
└── output/
    └── [job-id]/
        └── translated-file.xlsx
```

This keeps input/output files organized by job ID.

---

## Security Note

For production, you should:
1. Add authentication (Supabase Auth)
2. Restrict policies to authenticated users only
3. Add Row Level Security based on user ID
4. Set up automatic file cleanup after 24 hours

For now, public access is fine for testing/educational purposes.

---

## Next Steps

After storage is set up:

1. ✅ Database schema created
2. ✅ Storage bucket configured
3. → Test connection with Python script
4. → Deploy to Vercel

Continue to: Run `python test_supabase_connection.py`
