# Python Package Hub — Architecture

## Overview

A static site generation pipeline that fetches Python package metadata from the PyPI public API, renders SEO-optimized HTML pages, and deploys to Cloudflare Pages for free global hosting.

## Data Flow

```
PyPI JSON API
     │
     ▼
fetch_packages.py  ──►  data/package_cache/{name}.json
                                    │
                                    ▼
                         generate_site.py  ──►  site/output/{name}/index.html
                                    │
                                    ▼
                        generate_sitemap.py  ──►  site/output/sitemap.xml
                                    │
                                    ▼
                          git push  ──►  Cloudflare Pages  ──►  live site
```

## Components

### 1. Data Fetch Layer (`pipeline/fetch_packages.py`)
- Reads package names from `data/top_packages.json`
- For each package, requests `https://pypi.org/pypi/{name}/json`
- Caches response to `data/package_cache/{name}.json`
- Rate limits to 1 request per 500ms to respect PyPI
- Skips packages with existing cache (use `--refresh` flag to force update)

### 2. Site Generation Layer (`pipeline/generate_site.py`)
- Loads all cached package JSON files
- Extracts: name, version, summary, description, author, license, classifiers, requires_python
- Derives package category from PyPI classifiers
- Generates per-package content:
  - Installation commands (pip, conda, poetry)
  - Verification command
  - Common errors and fixes (category-based templates)
  - Related packages
- Renders HTML using Jinja2 templates
- Writes to `site/output/{package-name}/index.html`
- Generates `site/output/index.html` (homepage with package grid)

### 3. Sitemap Layer (`pipeline/generate_sitemap.py`)
- Scans `site/output/` for all `index.html` files
- Generates `site/output/sitemap.xml` with all page URLs
- Includes `<lastmod>` timestamps

### 4. Site Templates (`site/templates/`)
- `base.html` — base layout (nav, AdSense placeholders, footer, affiliate CTAs)
- `package.html` — extends base, per-package content block
- `index.html` — homepage template

### 5. Static Assets (`site/static/`)
- `style.css` — minimal responsive CSS, no external dependencies

### 6. Analytics (`analytics/fetch_stats.py`)
- Queries Cloudflare Analytics API
- Outputs top pages, traffic sources, and visitor counts

## Infrastructure

| Component | Service | Cost |
|---|---|---|
| Static hosting | Cloudflare Pages | Free |
| Domain (optional) | Cloudflare Registrar | ~$10/year |
| Build trigger | Cloudflare Pages Git integration | Free |
| Analytics | Cloudflare Web Analytics | Free |
| Source control | GitHub | Free |

**Total monthly cost: $0** (until scale requires paid tier features)

## SEO Strategy

Each page targets queries like:
- `how to install {package} python`
- `pip install {package} not working`
- `{package} ModuleNotFoundError`
- `{package} ImportError`

Page structure is optimized for these queries:
- Title: `Install {Package} in Python — Guide & Error Fixes`
- H1: `How to Install {Package} in Python`
- H2 sections: What is it, Installation, Verify, Common Errors
- JSON-LD HowTo schema markup

## Monetization Integration

- AdSense: script tag in `<head>`, ad unit divs in sidebar and after first H2
- Affiliate links: static section in footer and sidebar of `base.html`
- No per-page customization needed — affiliate links are generic Python/dev resources

## Scaling Path

Once analytics show top-performing packages:
1. Expand those package pages with more detailed content
2. Add version history pages (`/{package}/versions/`)
3. Add category landing pages (`/category/data-science/`)
4. Add comparison pages (`/{package-a}-vs-{package-b}/`)

Scale infrastructure only if Cloudflare Pages limits are hit (unlikely for first year).
