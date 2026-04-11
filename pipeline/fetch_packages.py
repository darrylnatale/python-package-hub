"""
fetch_packages.py

Downloads and caches PyPI JSON metadata for each package in top_packages.json.
Cached responses are written to data/package_cache/{name}.json.

Usage:
    python pipeline/fetch_packages.py              # skip already-cached packages
    python pipeline/fetch_packages.py --refresh    # re-fetch all packages

Run from the system root: systems/python-package-hub/
"""

import argparse
import json
import sys
import time
from pathlib import Path
import requests

PACKAGES_FILE = Path("data/top_packages.json")
CACHE_DIR = Path("data/package_cache")
PYPI_URL = "https://pypi.org/pypi/{name}/json"
RATE_LIMIT_SECONDS = 0.5


def fetch_package(name: str):
    url = PYPI_URL.format(name=name)
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            print(f"  [404] {name} not found on PyPI — skipping")
            return None
        print(f"  [ERROR {response.status_code}] {name}")
        return None
    except requests.RequestException as e:
        print(f"  [NETWORK ERROR] {name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Fetch PyPI metadata for packages")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch all packages, overwriting existing cache",
    )
    args = parser.parse_args()

    if not PACKAGES_FILE.exists():
        print(f"ERROR: {PACKAGES_FILE} not found. Run from the system root directory.")
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    with open(PACKAGES_FILE) as f:
        packages = json.load(f)

    print(f"Fetching metadata for {len(packages)} packages...")
    fetched = 0
    skipped = 0
    failed = 0

    for name in packages:
        cache_file = CACHE_DIR / f"{name}.json"

        if cache_file.exists() and not args.refresh:
            skipped += 1
            continue

        print(f"  Fetching {name}...")
        data = fetch_package(name)

        if data:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            fetched += 1
        else:
            failed += 1

        time.sleep(RATE_LIMIT_SECONDS)

    print(f"\nDone. Fetched: {fetched}, Skipped (cached): {skipped}, Failed: {failed}")
    print(f"Cache directory: {CACHE_DIR.resolve()}")


if __name__ == "__main__":
    main()
