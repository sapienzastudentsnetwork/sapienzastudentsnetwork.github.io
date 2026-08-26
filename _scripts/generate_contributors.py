#!/usr/bin/env python3
"""Generate deterministic contributor rankings from the repository Git history."""

import json
import math
import os
import re
import subprocess
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = os.getenv(
    "GITHUB_REPOSITORY",
    "sapienzastudentsnetwork/sapienzastudentsnetwork.github.io",
)

COURSE_PATHS = {
    "acsai": {"acsai", "30786"},
    "compsci": {"compsci", "29932"},
    "cybersec": {"cybersec", "29389"},
    "datasci": {"datasci"},
    "it": {"it"},
}

# Every current and historical course root must be excluded from the project-wide
# ranking, because those changes belong to the corresponding wiki ranking.
ALL_COURSE_ROOTS = {
    root_directory
    for course_directories in COURSE_PATHS.values()
    for root_directory in course_directories
}

BOT_PATTERN = re.compile(r"\[bot\]|github-actions", re.IGNORECASE)
NOREPLY_PATTERN = re.compile(
    r"^(?:\d+\+)?([^@]+)@users\.noreply\.github\.com$",
    re.IGNORECASE,
)

EXCLUDED_PARTS = {
    ".git",
    "generated",
    "node_modules",
    "public",
    "resources",
    "vendor",
}
EXCLUDED_SUFFIXES = {
    ".lock",
    ".map",
    ".min.css",
    ".min.js",
}

# Exact aliases maintained by the project. Values are canonical GitHub usernames.
# Canonical usernames are trusted when they occur directly in Git author metadata too.
IDENTITY_OVERRIDES = {
    "Alessio Marini": "alem1105",
    "atyion": "atyion",
    "atyon": "atyon",
    "Beray Nil Atabey": "NilAtabey",
    "Dario Loi": "dario-loi",
    "Davide Galilei": "DavideGalilei",
    "ENDERZOMBI102": "ENDERZOMBI102",
    "Francesco De Benedittis": "Fra179",
    "Ionut Cicio": "IonutCicio",
    "Leonardo Biason": "ElBi21",
    "Lorenzo Antonelli": "Lorenzoantonelli",
    "Marcello Galisai": "marcellogalisai",
    "Marco Casu": "CasuFrost",
    "Matteo Collica": "matypist",
    "Michele Palma": "palmaaaa",
    "Oriana Deliallisi": "orianani311",
    "Simone Bianco": "Exyss",
    "Simone Sestito": "simonesestito",
    "marciesmonde-maker": "marciesmonde-maker",
    "sapienzauser420": "sapienzauser420",
    "vitome": "vitome",
}
TRUSTED_USERNAMES = set(IDENTITY_OVERRIDES.values())


def git(*args: str) -> str:
    """Run Git in the repository and return decoded standard output."""
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
        errors="replace",
    )


def trusted_identity(author_name: str):
    """Return a trusted identity for an exact override or canonical username."""
    login = IDENTITY_OVERRIDES.get(author_name)

    if login is None and author_name in TRUSTED_USERNAMES:
        login = author_name

    if login is None:
        return None

    return (
        login.lower(),
        login,
        f"https://github.com/{login}",
        f"https://github.com/{login}.png?size=160",
        False,
    )


def github_identities() -> dict:
    """Map commit SHAs to GitHub accounts using the GitHub commits API."""
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        return {}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "ssn-contributor-rankings",
    }
    identities = {}
    page = 1

    try:
        while True:
            url = (
                f"https://api.github.com/repos/{REPOSITORY}/commits"
                f"?sha=main&per_page=100&page={page}"
            )
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, timeout=30) as response:
                commits = json.load(response)

            if not commits:
                break

            for commit in commits:
                author = commit.get("author")
                if author and author.get("login"):
                    identities[commit["sha"]] = {
                        "login": author["login"],
                        "github": author["html_url"],
                        "avatar": author.get("avatar_url", ""),
                    }

            if len(commits) < 100:
                break

            page += 1
    except Exception as error:
        print(f"warning: GitHub identity lookup unavailable: {error}")

    return identities


def fallback_identity(author_name: str, author_email: str):
    """Resolve an identity from trusted aliases, noreply email, or user search."""
    trusted = trusted_identity(author_name)
    if trusted:
        return trusted

    noreply_match = NOREPLY_PATTERN.match(author_email.strip())
    if noreply_match:
        login = noreply_match.group(1)
        return (
            login.lower(),
            login,
            f"https://github.com/{login}",
            f"https://github.com/{login}.png?size=160",
            False,
        )

    identity_key = f"{author_name.lower()}|{author_email.lower()}"
    search_query = quote(author_name)
    return (
        identity_key,
        author_name,
        f"https://github.com/search?q={search_query}&type=users",
        "",
        True,
    )


def accepted_file(path: str, scope: str) -> bool:
    """Return whether a changed path counts toward the requested ranking."""
    file_path = Path(path)

    if any(part in EXCLUDED_PARTS for part in file_path.parts):
        return False

    if any(path.lower().endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False

    first_part = file_path.parts[0] if file_path.parts else ""
    if scope == "all":
        return True

    if scope == "sitewide":
        return first_part not in ALL_COURSE_ROOTS

    accepted_roots = COURSE_PATHS[scope]
    return first_part in accepted_roots


def collect_contributors(scope: str, identities: dict, git_log: str) -> list:
    """Aggregate commits and line changes for one course or the site-wide scope."""
    contributors = defaultdict(
        lambda: {
            "commits": set(),
            "additions": 0,
            "deletions": 0,
        }
    )
    current_author = None

    for line in git_log.splitlines():
        if line.startswith("@@"):
            fields = line[2:].split("\x1f")
            if len(fields) != 3:
                current_author = None
                continue

            commit_sha, author_name, author_email = fields
            if BOT_PATTERN.search(author_name + author_email):
                current_author = None
                continue

            github_author = identities.get(commit_sha)

            # Prefer GitHub's commit-to-account association whenever available.
            # Repository-maintained overrides are only used by fallback_identity()
            # when the commit has no matched GitHub account; this avoids replacing
            # a verified match while still preventing generic user-search links.
            if github_author:
                login = github_author["login"]
                current_author = (
                    commit_sha,
                    login.lower(),
                    login,
                    github_author["github"],
                    github_author["avatar"],
                    False,
                )
            else:
                current_author = (
                    commit_sha,
                    *fallback_identity(author_name, author_email),
                )
            continue

        if current_author is None or "\t" not in line:
            continue

        numstat_fields = line.split("\t", 2)
        if len(numstat_fields) != 3:
            continue

        additions, deletions, path = numstat_fields
        if additions == "-" or deletions == "-":
            continue

        if not accepted_file(path, scope):
            continue

        (
            commit_sha,
            identity_key,
            display_name,
            github_url,
            avatar_url,
            unresolved,
        ) = current_author

        contributor = contributors[identity_key]
        contributor.update(
            name=display_name,
            github=github_url,
            avatar=avatar_url,
            unresolved=unresolved,
        )
        contributor["commits"].add(commit_sha)
        contributor["additions"] += int(additions)
        contributor["deletions"] += int(deletions)

    ranking = []
    for contributor in contributors.values():
        effective_lines = contributor["additions"] + contributor["deletions"]
        name_words = re.findall(r"[\wÀ-ÿ]+", contributor["name"])
        initials = "".join(word[0] for word in name_words[:2]).upper() or "?"

        ranking.append(
            {
                "name": contributor["name"],
                "github": contributor["github"],
                "avatar": contributor["avatar"],
                "initials": initials,
                "unresolved": contributor["unresolved"],
                "commits": len(contributor["commits"]),
                "additions": contributor["additions"],
                "deletions": contributor["deletions"],
                "effective_lines": effective_lines,
            }
        )

    max_commits = max((item["commits"] for item in ranking), default=1)
    max_lines = max((item["effective_lines"] for item in ranking), default=1)

    for contributor in ranking:
        commit_score = math.log1p(contributor["commits"]) / math.log1p(max_commits)
        line_score = (
            math.log1p(contributor["effective_lines"]) / math.log1p(max_lines)
        )
        contributor["score"] = round(
            100 * (0.40 * commit_score + 0.60 * line_score),
            1,
        )

    ranking.sort(
        key=lambda item: (
            -item["score"],
            -item["effective_lines"],
            -item["commits"],
            item["name"].lower(),
        )
    )

    for rank, contributor in enumerate(ranking, start=1):
        contributor["rank"] = rank

    return ranking


def main() -> None:
    """Generate course, project-wide, and combined contributor rankings."""
    identities = github_identities()
    git_log = git(
        "log",
        "HEAD",
        "--no-merges",
        "--use-mailmap",
        "--format=@@%H%x1f%aN%x1f%aE",
        "--numstat",
    )
    source_commit = git("rev-parse", "HEAD").strip()
    generated_at = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    output_directory = ROOT / "data" / "contributors"
    output_directory.mkdir(parents=True, exist_ok=True)

    ranking_scopes = [*COURSE_PATHS, "sitewide", "all"]
    for scope in ranking_scopes:
        key = scope
        payload = {
            "generated_at": generated_at,
            "source_commit": source_commit,
            "contributors": collect_contributors(scope, identities, git_log),
        }
        output_path = output_directory / f"{key}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
