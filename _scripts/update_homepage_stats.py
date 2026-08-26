#!/usr/bin/env python3
"""Update the public homepage page and contributor totals."""
from __future__ import annotations

import json
import re
import subprocess
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_ROOTS = {"content", "archetypes", "__pages", "_pages", "homepage", "themes"}
EXCLUDED_FILES = {"readme.md", "contributing.md", "license.md"}


def tracked_files() -> list[str]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [item.decode() for item in output.split(b"\0") if item]


def is_public_markdown_page(path: str) -> bool:
    parts = Path(path).parts
    if not parts or Path(path).suffix.lower() != ".md":
        return False
    if parts[0] in EXCLUDED_ROOTS or any(part.startswith(".") for part in parts):
        return False
    if Path(path).name.lower() in EXCLUDED_FILES:
        return False
    text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")[:4000]
    hidden = re.search(r"(?mi)^\s*(draft|headless|bookHidden)\s*:\s*true\s*$", text)
    index_layout = re.search(r'''(?mi)^\s*layout\s*:\s*['"]?index-page['"]?\s*$''', text)
    return hidden is None and index_layout is None


def contributor_total() -> int:
    request = urllib.request.Request(
        "https://api.github.com/repos/SapienzaStudentsNetwork/sapienzastudentsnetwork.github.io/contributors?anon=1&per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            contributors = json.load(response)
        identities = {
            str(item.get("login") or item.get("name") or item.get("email")).lower()
            for item in contributors
            if item.get("login") or item.get("name") or item.get("email")
        }
        return sum("[bot]" not in identity and "github-actions" not in identity for identity in identities)
    except (OSError, ValueError):
        current = json.loads((ROOT / "data/homepage_stats.json").read_text(encoding="utf-8"))
        return int(current.get("contributors", 0))


def main() -> None:
    pages = sum(is_public_markdown_page(path) for path in tracked_files())
    data = {"pages": pages, "contributors": contributor_total()}
    target = ROOT / "data/homepage_stats.json"
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Homepage stats: {pages} pages, {data['contributors']} contributors")


if __name__ == "__main__":
    main()
