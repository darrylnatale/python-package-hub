"""
generate_tools.py — Track C: Database Connection String Builder
Generates static pages into site/output/tools/
Run: python pipeline/generate_tools.py
"""

import json
from pathlib import Path
import jinja2

HERE      = Path(__file__).parent.parent
DATA_FILE = HERE / "data/tools/databases.json"
TMPL_DIR  = HERE / "templates/tools"
OUT_DIR   = HERE / "site/output/tools"
SITE_URL  = "https://pip.dev-guides.com"

data = json.loads(DATA_FILE.read_text())
env  = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TMPL_DIR)),
    autoescape=True,
)


def write_page(out_path: Path, html: str):
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "index.html").write_text(html, encoding="utf-8")
    print(f"  wrote {out_path / 'index.html'}")


# Tools homepage
write_page(
    OUT_DIR,
    env.get_template("index.html").render(databases=data),
)

# Per-database page
for db_slug, db in data.items():
    write_page(
        OUT_DIR / db_slug,
        env.get_template("database.html").render(db_slug=db_slug, db=db),
    )

    # Per-driver combination page
    for driver_slug, driver in db["drivers"].items():
        write_page(
            OUT_DIR / db_slug / driver_slug,
            env.get_template("combination.html").render(
                db_slug=db_slug,
                db=db,
                driver_slug=driver_slug,
                driver=driver,
            ),
        )

# Tools-only sitemap
urls = [f"{SITE_URL}/tools/"]
for db_slug, db in data.items():
    urls.append(f"{SITE_URL}/tools/{db_slug}/")
    for driver_slug in db["drivers"]:
        urls.append(f"{SITE_URL}/tools/{db_slug}/{driver_slug}/")

sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in urls:
    sitemap_lines.append(f"  <url><loc>{url}</loc></url>")
sitemap_lines.append("</urlset>")
sitemap_path = OUT_DIR / "sitemap.xml"
sitemap_path.write_text("\n".join(sitemap_lines), encoding="utf-8")
print(f"  wrote {sitemap_path}")

print(f"\nDone — {len(urls)} pages generated in {OUT_DIR}")
