# Set Up Supabase Database - Step by Step

## Quick Setup (5 minutes)

### Step 1: Open Supabase SQL Editor

1. Go to: **https://supabase.com/dashboard/project/miodbpwlebiidcvrlvmc**
2. Log in to your Supabase account
3. Click **SQL Editor** in the left sidebar
4. Click **New query** button

### Step 2: Copy and Execute SQL Schema

1. Open the file: `supabase-schema.sql` in this folder
2. **Select all** (Ctrl+A) and **copy** (Ctrl+C)
3. **Paste** into the SQL Editor
4. Click the **RUN** button (bottom right corner)

### Step 3: Verify Success

You should see:
```
Success. No rows returned
```

This means all tables, functions, triggers, and policies were created successfully!

---

## What Gets Created

### Tables
- `translation_jobs` - Stores all translation job information and progress

### Functions
- `update_updated_at_column()` - Auto-updates timestamps
- `update_progress_percentage()` - Auto-calculates progress percentage
- `cleanup_expired_jobs()` - Removes expired jobs (24 hours old)

### Triggers
- Auto-update `updated_at` on any change
- Auto-calculate `progress_percentage` from cell counts

### Views
- `active_translation_jobs` - Quick view of ongoing translations

### Security
- Row Level Security (RLS) enabled
- Public access policy (for testing - restrict later with auth)

---

## Alternative: Manual Table Creation

If you prefer to create tables manually:

### Create the translation_jobs table:

```sql
CREATE TABLE translation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    original_filename VARCHAR(255) NOT NULL,
    input_file_path VARCHAR(500),
    output_file_path VARCHAR(500),
    file_size BIGINT,
    source_lang VARCHAR(10) NOT NULL DEFAULT 'fr',
    target_lang VARCHAR(10) NOT NULL DEFAULT 'en',
    current_cell INTEGER DEFAULT 0,
    total_cells INTEGER DEFAULT 0,
    progress_message TEXT DEFAULT 'Starting translation...',
    progress_percentage INTEGER DEFAULT 0,
    error_message TEXT,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);
```

---

## Troubleshooting

### Error: "relation already exists"
✅ This is OK! It means the table was already created. You can proceed.

### Error: "permission denied"
❌ Make sure you're using the service_role key, not the anon key.

### Can't find SQL Editor
1. Make sure you're logged in to Supabase
2. Select your project: **ExcelTranslate**
3. Look for "SQL Editor" in the left menu

---

## Next Steps

After the database is set up:

1. ✅ Database schema created
2. → Create storage bucket (see next section)
3. → Test connection
4. → Deploy to Vercel

Continue to: [SETUP_STORAGE_INSTRUCTIONS.md](SETUP_STORAGE_INSTRUCTIONS.md)
