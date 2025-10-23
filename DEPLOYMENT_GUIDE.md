# Excel Translator - Cloud Deployment Guide
## Migrate to Supabase + Vercel

This guide will walk you through deploying your Excel Translator app to the cloud using Supabase (backend/database/storage) and Vercel (serverless functions/hosting).

---

## Prerequisites

Before starting, make sure you have:
- A GitHub account (for code hosting)
- Git installed on your computer
- Node.js installed (for Vercel CLI)

---

## Part 1: Set Up Supabase (15 minutes)

### 1. Create Supabase Account & Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" and sign up
3. Click "New Project"
4. Fill in:
   - **Organization**: Create a new one or use existing
   - **Project name**: `excel-translator`
   - **Database password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to your users (e.g., US East, EU Central)
   - **Pricing plan**: Free (perfect for starting)
5. Click "Create new project" (takes 2-3 minutes)

### 2. Configure Storage

1. In your Supabase dashboard, go to **Storage** (left sidebar)
2. Click "Create a new bucket"
3. Bucket name: `excel-files`
4. Set as **Private** (uncheck Public bucket)
5. Click "Create bucket"

### 3. Set Storage Policies

1. Go to **Storage > Policies**
2. Click on `excel-files` bucket
3. Click "New Policy" and add these three policies:

**Policy 1: Allow uploads**
```sql
CREATE POLICY "Allow uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'excel-files');
```

**Policy 2: Allow downloads**
```sql
CREATE POLICY "Allow downloads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'excel-files');
```

**Policy 3: Allow deletes**
```sql
CREATE POLICY "Allow deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'excel-files');
```

### 4. Create Database Schema

1. Go to **SQL Editor** (left sidebar)
2. Open the file `supabase-schema.sql` from your project
3. Copy the entire contents
4. Paste into the SQL Editor
5. Click "Run" (bottom right)
6. You should see "Success. No rows returned"

### 5. Enable Realtime

1. Go to **Database > Replication** (left sidebar)
2. Find the `translation_jobs` table in the list
3. Toggle it **ON** to enable Realtime

### 6. Get Your API Credentials

1. Go to **Settings > API** (left sidebar)
2. Copy these values (you'll need them soon):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbG...` (long string)
   - **service_role key**: `eyJhbG...` (keep this SECRET!)

---

## Part 2: Prepare Your Code for Deployment (10 minutes)

### 1. Update HTML to Use Supabase Client

Open `templates/index.html` and add the Supabase client library before the closing `</body>` tag:

```html
<!-- Add Supabase Client -->
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

<!-- Switch to cloud version of app.js -->
<script src="/static/js/app-cloud.js"></script>
```

### 2. Configure Frontend with Your Supabase Credentials

Open `static/js/app-cloud.js` and update lines 4-5:

```javascript
const SUPABASE_URL = 'https://xxxxx.supabase.co'; // Your Project URL
const SUPABASE_ANON_KEY = 'eyJhbG...'; // Your anon/public key
```

### 3. Create Environment Variables File

1. Copy `.env.example` to `.env`
2. Fill in your Supabase credentials:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_SERVICE_KEY=eyJhbG...
```

**IMPORTANT**: Never commit `.env` to Git! (It's already in `.gitignore`)

### 4. Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - cloud migration"
```

### 5. Push to GitHub

1. Create a new repository on GitHub: [https://github.com/new](https://github.com/new)
2. Name it: `excel-translator`
3. Make it **Private** (recommended)
4. Don't initialize with README (we already have code)
5. Click "Create repository"
6. Run these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/excel-translator.git
git branch -M main
git push -u origin main
```

---

## Part 3: Deploy to Vercel (10 minutes)

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate (opens browser).

### 3. Deploy Your Project

From your project directory:

```bash
vercel
```

Answer the prompts:
- **Set up and deploy?** Y
- **Which scope?** Your personal account
- **Link to existing project?** N
- **Project name?** excel-translator (or press Enter)
- **Directory?** ./ (press Enter)
- **Override settings?** N

Vercel will deploy your project! You'll get a URL like: `https://excel-translator-xxxxx.vercel.app`

### 4. Configure Environment Variables

You need to add your Supabase credentials to Vercel:

**Option A: Via CLI**
```bash
vercel env add SUPABASE_URL
# Paste your Supabase URL when prompted

vercel env add SUPABASE_SERVICE_KEY
# Paste your service role key when prompted
```

**Option B: Via Dashboard**
1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Click on your `excel-translator` project
3. Go to **Settings > Environment Variables**
4. Add these variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_KEY`: Your service role key
5. Click "Save"

### 5. Redeploy with Environment Variables

```bash
vercel --prod
```

This creates your production deployment with environment variables configured!

---

## Part 4: Test Your Cloud App (5 minutes)

1. Visit your Vercel URL: `https://excel-translator-xxxxx.vercel.app`
2. Upload a test Excel file
3. Select source/target languages
4. Click "Translate"
5. Watch the progress bar (powered by Supabase Realtime!)
6. Download the translated file

---

## Architecture Overview

Your new cloud architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                       │
│  (HTML + CSS + app-cloud.js + Supabase JS Client)      │
└────────────┬────────────────────────────────────────────┘
             │
             ├──→ Supabase Realtime (progress updates)
             │
             ├──→ Vercel Serverless Functions
             │    ├─ /api/translate.py     (start job)
             │    ├─ /api/process_job.py   (do translation)
             │    ├─ /api/status.py        (check progress)
             │    └─ /api/download.py      (get result)
             │
             └──→ Supabase Backend
                  ├─ PostgreSQL (job tracking)
                  └─ Storage (files)
```

**Key Benefits:**
- **Fully serverless** - No servers to manage
- **Auto-scaling** - Handles traffic spikes automatically
- **Global CDN** - Fast loading worldwide
- **Free tier** - Generous limits for both platforms
- **Real-time updates** - Live progress tracking

---

## Cost Estimation

### Free Tier Limits:
- **Vercel**: 100GB bandwidth/month, 100 hours serverless execution
- **Supabase**: 500MB database, 1GB storage, 2GB bandwidth

### Typical Usage:
- Small Excel file (100KB): ~2 seconds processing
- Large Excel file (5MB): ~30 seconds processing
- With free tiers: ~200-300 translations/month

### If You Exceed Free Tier:
- **Vercel Pro**: $20/month (1TB bandwidth, more execution time)
- **Supabase Pro**: $25/month (8GB database, 100GB storage)

---

## Monitoring & Maintenance

### View Logs
**Vercel Logs:**
```bash
vercel logs
```
Or check the dashboard: [https://vercel.com/dashboard](https://vercel.com/dashboard)

**Supabase Logs:**
- Go to **Logs** in your Supabase dashboard
- Filter by API, Database, or Storage

### Database Cleanup
Old translation jobs expire after 24 hours. To manually clean them:

1. Go to Supabase **SQL Editor**
2. Run:
```sql
SELECT cleanup_expired_jobs();
```

### Set Up Automatic Cleanup (Recommended)
Use Supabase Edge Functions or Vercel Cron Jobs to run cleanup daily.

---

## Troubleshooting

### "Job not found" error
- Check that Supabase credentials are correct in Vercel environment variables
- Verify the database schema was created properly

### Translation times out
- Increase `maxDuration` in `vercel.json` for `process_job.py`
- Vercel free tier limits functions to 10s, Pro allows 60s+

### "Failed to upload file" error
- Check Supabase Storage policies are set correctly
- Verify the `excel-files` bucket exists

### Progress bar not updating
- Ensure Realtime is enabled for `translation_jobs` table
- Check browser console for connection errors
- Verify Supabase anon key in `app-cloud.js` is correct

---

## Next Steps

### Add Authentication
1. Enable Supabase Auth (Email/Password or OAuth)
2. Update storage policies to check `auth.uid()`
3. Add login/signup to frontend

### Custom Domain
1. Buy a domain (e.g., excelTranslator.com)
2. In Vercel dashboard: **Settings > Domains**
3. Add your custom domain and follow DNS instructions

### Add Payment (for premium features)
- Integrate Stripe for paid translations
- Add usage limits based on subscription tier

---

## Support

- **Vercel Docs**: [https://vercel.com/docs](https://vercel.com/docs)
- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Issues**: Create an issue in your GitHub repository

---

## Summary

You've successfully migrated your Excel Translator to the cloud! 🎉

Your app is now:
- ✅ Serverless and auto-scaling
- ✅ Globally distributed via CDN
- ✅ Real-time progress updates
- ✅ No server maintenance required
- ✅ Free tier for moderate usage

**Your URLs:**
- **App**: `https://excel-translator-xxxxx.vercel.app`
- **Supabase Dashboard**: `https://supabase.com/dashboard/project/xxxxx`
- **Vercel Dashboard**: `https://vercel.com/dashboard`

Enjoy your cloud-powered translation app!
