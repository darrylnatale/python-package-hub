# Deployment Setup

## Overview

The site is deployed as a static site to Cloudflare Pages. Every push to the main branch triggers a rebuild and redeploy automatically.

---

## Step 1 — Create a GitHub Repository

1. Create a new GitHub repository (public or private)
2. Push the contents of `systems/python-package-hub/` to the repo root:

```bash
cd systems/python-package-hub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/python-package-hub.git
git push -u origin main
```

**Important:** Add these entries to `.gitignore` before pushing:

```
data/package_cache/
site/output/
analytics/reports/
```

---

## Step 2 — Connect to Cloudflare Pages

1. Log in to Cloudflare dashboard → **Workers & Pages** → **Create application** → **Pages**
2. Connect to GitHub and select the repository
3. Set build configuration:
   - **Build command:** `pip install -r pipeline/requirements.txt && python pipeline/fetch_packages.py && python pipeline/generate_site.py && python pipeline/generate_sitemap.py`
   - **Build output directory:** `site/output`
4. Click **Save and Deploy**

The first build fetches PyPI data and generates all pages. Subsequent builds use the cache.

---

## Step 3 — Set Up a Custom Domain (Optional)

1. Register a domain (e.g., `pip.dev-guides.com` — configured via Cloudflare Pages → Custom domains)
2. In Cloudflare Pages → **Custom domains** → Add your domain
3. Cloudflare automatically provisions HTTPS

Update `SITE_URL` in `pipeline/generate_site.py` and `pipeline/generate_sitemap.py` to match your domain, then redeploy.

---

## Step 4 — Submit to Google Search Console

1. Go to https://search.google.com/search-console
2. Add your site and verify ownership (Cloudflare Pages makes this easy via the HTML file method)
3. Submit `https://yourdomain.com/sitemap.xml`
4. Monitor **Coverage** report to confirm pages are being indexed

---

## Step 5 — Apply for Google AdSense

Requirements before applying:
- Site must be live for at least 30 days
- At least 50+ pages of original content
- Site must comply with AdSense policies

Once approved:
1. Get your AdSense publisher ID (`ca-pub-XXXXXXXXXXXXXXXX`)
2. Uncomment the AdSense script tag in `site/templates/base.html`
3. Replace `ca-pub-XXXXXXXXXXXXXXXX` with your publisher ID
4. Uncomment and configure the ad units in `base.html` and `package.html`
5. Redeploy

---

## Step 6 — Set Up Analytics

1. Add Cloudflare Web Analytics to the site:
   - Cloudflare Dashboard → **Web Analytics** → Add site
   - Copy the beacon token
   - Uncomment the analytics script in `site/templates/base.html`
   - Replace `TOKEN` with your beacon token
2. Redeploy

To run the analytics fetch script locally:
```bash
export CLOUDFLARE_API_TOKEN=your_token
export CLOUDFLARE_ACCOUNT_ID=your_account_id
export CLOUDFLARE_SITE_TAG=your_site_tag
python analytics/fetch_stats.py
```

---

## Step 7 — Set Up Automatic Daily Rebuilds

To keep package versions current, trigger a Cloudflare Pages rebuild daily.

Option A — Cloudflare Cron Trigger (via Worker):
1. Create a Worker that calls the Cloudflare Pages deploy hook URL
2. Set a Cron Trigger on the Worker for `0 6 * * *` (6am UTC daily)

Option B — GitHub Actions:
Create `.github/workflows/daily_rebuild.yml`:

```yaml
name: Daily Rebuild
on:
  schedule:
    - cron: '0 6 * * *'
jobs:
  rebuild:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Cloudflare Pages deploy
        run: curl -X POST "${{ secrets.CF_DEPLOY_HOOK_URL }}"
```

Set `CF_DEPLOY_HOOK_URL` as a GitHub Actions secret (get the URL from Cloudflare Pages → Settings → Deploy hooks).

---

## Environment Variables Required

| Variable | Purpose |
|---|---|
| `CLOUDFLARE_API_TOKEN` | For analytics fetching (Analytics:Read permission) |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare account ID |
| `CLOUDFLARE_SITE_TAG` | Web Analytics site tag |

Never commit these to the repository. Store in environment variables or a `.env` file (gitignored).

---

## Cost Summary

| Item | Cost |
|---|---|
| Cloudflare Pages hosting | Free |
| Cloudflare Web Analytics | Free |
| GitHub repository | Free |
| Domain name (optional) | ~$10/year |
| **Total** | **$0/month** |
