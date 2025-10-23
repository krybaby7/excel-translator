# Quick Start - Deploy in 30 Minutes

This is the fastest path to getting your Excel Translator running in the cloud.

## Step 1: Supabase Setup (10 min)

1. **Create account**: [supabase.com](https://supabase.com) → Sign up → New Project
2. **Project details**: Name it `excel-translator`, set password, choose region
3. **Wait 2-3 minutes** for project creation

### Create Storage Bucket
1. Go to **Storage** → **New bucket**
2. Name: `excel-files`, Private, Create

### Run Database Schema
1. Go to **SQL Editor**
2. Copy contents of `supabase-schema.sql`
3. Paste and click **Run**

### Enable Realtime
1. **Database** → **Replication**
2. Find `translation_jobs` → Toggle ON

### Get Credentials
1. **Settings** → **API**
2. Copy:
   - Project URL
   - anon/public key
   - service_role key

## Step 2: Update Code (5 min)

### Update Frontend
Edit `static/js/app-cloud.js` lines 4-5:
```javascript
const SUPABASE_URL = 'YOUR_PROJECT_URL';
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY';
```

### Update HTML
Add to `templates/index.html` before closing `</body>`:
```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="/static/js/app-cloud.js"></script>
```

## Step 3: Deploy to Vercel (10 min)

### Push to GitHub
```bash
git init
git add .
git commit -m "Cloud migration"
# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/excel-translator.git
git push -u origin main
```

### Deploy
```bash
npm install -g vercel
vercel login
vercel
```

### Add Environment Variables
```bash
vercel env add SUPABASE_URL
# Paste your Supabase URL

vercel env add SUPABASE_SERVICE_KEY
# Paste your service role key

vercel --prod
```

## Step 4: Test (5 min)

Visit your Vercel URL and test translation!

---

## Need Help?

See full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
