"""
update_package_list.py

Fetches the top PyPI packages by monthly download count and merges them
into top_packages.json. Uses the public top-pypi-packages dataset
maintained at https://hugovk.github.io/top-pypi-packages/

Usage:
    python pipeline/update_package_list.py              # top 2000 packages
    python pipeline/update_package_list.py --top 5000   # top N packages
    python pipeline/update_package_list.py --top 5000 --replace  # replace list entirely

Run from the system root: systems/python-package-hub/
"""

import argparse
import json
import sys
import time
from pathlib import Path
import requests

PACKAGES_FILE = Path("data/top_packages.json")
TOP_PYPI_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"

# Packages to always exclude (not real installable packages)
EXCLUDE = {
    "tkinter",       # stdlib, not on PyPI
    "setuptools",    # bundled — already in list
    "pip",           # already in list
    "wheel",         # build tool
    "distribute",    # legacy setuptools shim
    "pkg-resources", # setuptools utility
    "pkg_resources", # setuptools utility
    "distutils",     # stdlib
    "python",        # not a package
    "python3",       # not a package
    "easy-install",  # legacy
}


def fetch_top_packages(top_n: int):
    print(f"Fetching top {top_n} packages from PyPI download stats...")
    try:
        resp = requests.get(TOP_PYPI_URL, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR fetching package list: {e}")
        sys.exit(1)

    data = resp.json()
    rows = data.get("rows", [])
    print(f"  Source contains {len(rows)} packages")

    packages = []
    for row in rows[:top_n]:
        name = row.get("project", "").strip()
        if name and name.lower() not in EXCLUDE:
            packages.append(name)

    return packages


def main():
    parser = argparse.ArgumentParser(description="Update top_packages.json from PyPI download stats")
    parser.add_argument("--top", type=int, default=2000, help="Number of top packages to include (default: 2000)")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace the existing list entirely (default: merge, preserving existing order)",
    )
    args = parser.parse_args()

    top_packages = fetch_top_packages(args.top)

    if args.replace:
        merged = top_packages
    else:
        # Load existing list and merge: keep existing order, append new
        existing = []
        if PACKAGES_FILE.exists():
            with open(PACKAGES_FILE) as f:
                existing = json.load(f)
        existing_lower = {p.lower() for p in existing}
        new_packages = [p for p in top_packages if p.lower() not in existing_lower]
        merged = existing + new_packages
        print(f"  Existing: {len(existing)}, New additions: {len(new_packages)}")

    PACKAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PACKAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {PACKAGES_FILE} now contains {len(merged)} packages.")
    print("Next step: python pipeline/fetch_packages.py")


if __name__ == "__main__":
    main()
