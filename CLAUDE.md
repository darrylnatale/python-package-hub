# Python Package Hub — System Instructions

## Purpose

Automated programmatic SEO site that generates one page per Python package covering installation, common errors, and troubleshooting. Monetized via display advertising and affiliate links.

## System Type

Programmatic SEO content site

## Monetization

- Google AdSense (primary — developer CPM $15–40)
- JetBrains affiliate (PyCharm)
- DataCamp affiliate (Python courses)
- DigitalOcean referral ($25 per signup)

## Data Source

PyPI JSON API — public, free, no authentication required.
Endpoint: `https://pypi.org/pypi/{package_name}/json`

## Key Files

| File | Purpose |
|---|---|
| `data/top_packages.json` | Seed list of package names to generate pages for |
| `data/package_cache/` | Cached PyPI API responses (never commit to git) |
| `pipeline/fetch_packages.py` | Downloads and caches package metadata |
| `pipeline/generate_site.py` | Renders all HTML pages from cached data |
| `pipeline/generate_sitemap.py` | Generates sitemap.xml |
| `site/output/` | Generated static site (never commit to git) |

## Running the Pipeline

```bash
cd systems/python-package-hub
pip install -r pipeline/requirements.txt

# Step 1: Fetch package metadata from PyPI
python pipeline/fetch_packages.py

# Step 2: Generate all HTML pages
python pipeline/generate_site.py

# Step 3: Generate sitemap
python pipeline/generate_sitemap.py
```

Output is written to `site/output/`. Push this directory to Cloudflare Pages.

## Verification

Before scaling or deployment, the system must validate output quality.

### Required checks

- no duplicated sections (e.g. error lists)
- no raw HTML or markdown artifacts in descriptions
- correct code examples for each package
- no unrelated content (e.g. pandas example on non-pandas pages)
- license field is clean and readable

### Process

- generate a sample of 10 pages
- review content structure and correctness
- identify and fix issues in the generator
- regenerate and re-check

Do not scale until verification passes.

## Verification Requirements

All systems must verify that outputs are correct before deployment.

Verification must include:

- scripts run without errors
- output files are generated as expected
- no duplicated or malformed content

## Deployment

See `deploy/setup.md` for Cloudflare Pages setup instructions.

## Adding More Packages

Add package names (lowercase) to `data/top_packages.json`, then re-run the pipeline.

## Analytics

Run `python analytics/fetch_stats.py` to pull Cloudflare Web Analytics data.

## Search Performance Tracking

Primary performance data must come from Google Search Console.

The system should support:

- tracking indexed pages
- impressions per URL
- clicks per URL
- query data

If API access is available, implement a script:

analytics/fetch_gsc_data.py

This script should:
- pull data from Google Search Console API
- store results locally (CSV or database)
- identify top-performing pages and queries

Cloudflare Analytics is secondary and used only after traffic exists.

## Evaluation Criteria (30-day checkpoint)

- Indexed pages in Google Search Console: target 500+
- Organic impressions: target 10,000+
- AdSense approval status: should be applied for within 30 days

Kill criteria: if after 90 days there are fewer than 200 indexed pages and under 1,000 monthly organic impressions, terminate and reallocate.

## Scaling Rules

Do not scale page count aggressively until the template is validated.

Scaling progression:

- Stage 1: 200–300 pages (initial)
- Stage 2: validate indexing and impressions
- Stage 3: expand to ~1,000 pages
- Stage 4: scale to 5,000–10,000 pages

Only proceed to the next stage if:

- pages are being indexed
- impressions are observed in Google Search Console

If no signal is detected, improve the template before scaling.
