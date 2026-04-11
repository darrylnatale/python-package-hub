"""
fetch_stats.py

Fetches web analytics from Cloudflare Web Analytics API and writes a
performance report to analytics/reports/YYYY-MM-DD.json.

Usage:
    python analytics/fetch_stats.py

Requires environment variable:
    CLOUDFLARE_API_TOKEN   — Cloudflare API token with Analytics:Read permission
    CLOUDFLARE_ACCOUNT_ID  — Your Cloudflare account ID
    CLOUDFLARE_SITE_TAG    — Cloudflare Web Analytics site tag (from dashboard)

Run from the system root: systems/python-package-hub/
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

REPORTS_DIR = Path("analytics/reports")

GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: Environment variable {key} is not set.")
        sys.exit(1)
    return val


def fetch_analytics(api_token: str, account_id: str, site_tag: str, days: int = 7) -> dict:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    query = """
    query ($accountTag: string, $siteTag: string, $start: string, $end: string) {
      viewer {
        accounts(filter: { accountTag: $accountTag }) {
          rumPageloadEventsAdaptiveGroups(
            filter: {
              AND: [
                { date_geq: $start }
                { date_leq: $end }
                { siteTag: $siteTag }
              ]
            }
            limit: 1000
            orderBy: [count_DESC]
          ) {
            count
            dimensions {
              requestPath
            }
          }
        }
      }
    }
    """

    variables = {
        "accountTag": account_id,
        "siteTag": site_tag,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_top_pages(data: dict) -> list[dict]:
    try:
        groups = (
            data["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
        )
        return [
            {"path": g["dimensions"]["requestPath"], "views": g["count"]}
            for g in groups
        ]
    except (KeyError, IndexError, TypeError):
        return []


def main():
    api_token = get_env("CLOUDFLARE_API_TOKEN")
    account_id = get_env("CLOUDFLARE_ACCOUNT_ID")
    site_tag = get_env("CLOUDFLARE_SITE_TAG")

    print("Fetching Cloudflare Web Analytics (last 7 days)...")
    raw = fetch_analytics(api_token, account_id, site_tag, days=7)

    top_pages = parse_top_pages(raw)
    total_views = sum(p["views"] for p in top_pages)

    report = {
        "date": date.today().isoformat(),
        "period_days": 7,
        "total_pageviews": total_views,
        "top_pages": top_pages[:50],
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{date.today().isoformat()}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Total pageviews (7 days): {total_views}")
    print(f"Top pages:")
    for page in top_pages[:10]:
        print(f"  {page['views']:>6}  {page['path']}")
    print(f"\nFull report saved to {report_file}")


if __name__ == "__main__":
    main()
