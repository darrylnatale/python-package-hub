"""
generate_sitemap.py

Scans site/output/ for all index.html files and generates a sitemap.xml.
Also generates a robots.txt pointing to the sitemap.

Usage:
    python pipeline/generate_sitemap.py

Run from the system root: systems/python-package-hub/
"""

import sys
from datetime import date
from pathlib import Path

OUTPUT_DIR = Path("site/output")
SITE_URL = "https://pythonpackagehub.com"


def build_sitemap(output_dir: Path, site_url: str) -> str:
    today = date.today().isoformat()
    urls = []

    # Homepage
    urls.append({"loc": f"{site_url}/", "priority": "1.0", "changefreq": "weekly", "lastmod": today})

    # Package pages — any subdirectory with an index.html
    for index_file in sorted(output_dir.rglob("*/index.html")):
        rel_path = index_file.parent.relative_to(output_dir)
        slug = str(rel_path).replace("\\", "/")
        urls.append({
            "loc": f"{site_url}/{slug}/",
            "priority": "0.8",
            "changefreq": "monthly",
            "lastmod": today,
        })

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url['loc']}</loc>")
        lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        lines.append(f"    <priority>{url['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    return "\n".join(lines)


def build_robots(site_url: str) -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml
"""


def main():
    if not OUTPUT_DIR.exists():
        print(f"ERROR: {OUTPUT_DIR} not found. Run generate_site.py first.")
        sys.exit(1)

    print("Generating sitemap.xml...")
    sitemap = build_sitemap(OUTPUT_DIR, SITE_URL)
    sitemap_path = OUTPUT_DIR / "sitemap.xml"
    sitemap_path.write_text(sitemap, encoding="utf-8")
    print(f"  Written to {sitemap_path}")

    print("Generating robots.txt...")
    robots = build_robots(SITE_URL)
    robots_path = OUTPUT_DIR / "robots.txt"
    robots_path.write_text(robots, encoding="utf-8")
    print(f"  Written to {robots_path}")

    # Count URLs
    url_count = sitemap.count("<url>")
    print(f"\nDone. {url_count} URLs in sitemap.")


if __name__ == "__main__":
    main()
