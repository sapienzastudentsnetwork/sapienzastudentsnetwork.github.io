#!/usr/bin/env python3
"""Generate source-aware edit links and effective Git metadata for Hugo pages."""
from __future__ import annotations

import configparser
import json
import re
import subprocess
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/page_source_metadata.json"
INCLUDE_RE = re.compile(r'''{{[%<]\s*include(?:WithoutToc)?\s+["']([^"']+)["'][^}]*[>%]}}''')
FENCED_CODE_RE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,}).*?^\s*\1\s*$")
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
DEFAULT_REPOSITORY = "https://github.com/sapienzastudentsnetwork/sapienzastudentsnetwork.github.io"

@dataclass(frozen=True)
class Repository:
    local_path: Path
    web_url: str
    branch: str = "main"

    @property
    def root(self) -> Path:
        return ROOT / self.local_path

def git(repository: Repository, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository.root), *args],
        check=True, text=True, stdout=subprocess.PIPE,
    )
    return result.stdout.strip()

def github_url(remote: str) -> str:
    remote = remote.strip().removesuffix(".git")
    if remote.startswith("git@github.com:"):
        return "https://github.com/" + remote.removeprefix("git@github.com:")
    if remote.startswith("ssh://git@github.com/"):
        return "https://github.com/" + remote.removeprefix("ssh://git@github.com/")
    return remote

def repositories() -> list[Repository]:
    main = Repository(Path("."), DEFAULT_REPOSITORY)
    try:
        main_url = github_url(git(main, "remote", "get-url", "origin"))
    except subprocess.CalledProcessError:
        main_url = DEFAULT_REPOSITORY
    result = [Repository(Path("."), main_url)]

    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules")
    for section in parser.sections():
        local_path = Path(parser[section]["path"])
        if local_path.parts[:1] == ("themes",):
            continue
        result.append(Repository(local_path, github_url(parser[section]["url"])))
    return sorted(result, key=lambda repo: len(repo.local_path.parts), reverse=True)

def content_roots() -> list[Path]:
    with (ROOT / "hugo.toml").open("rb") as stream:
        config = tomllib.load(stream)
    default = config.get("contentDir", "content")
    roots = {
        Path(language.get("contentDir", default))
        for language in config.get("languages", {}).values()
        if not language.get("disabled", False)
    }
    return sorted(roots or {Path(default)})

def locate(path: Path, repos: list[Repository]) -> tuple[Repository, Path]:
    for repository in repos:
        if repository.local_path == Path("."):
            continue
        try:
            return repository, path.relative_to(repository.local_path)
        except ValueError:
            pass
    main = next(repo for repo in repos if repo.local_path == Path("."))
    return main, path

def histories(repos: list[Repository]) -> dict[Path, dict[str, dict[str, str]]]:
    result = {}
    for repository in repos:
        history: dict[str, dict[str, str]] = {}
        current = None
        log = git(repository, "log", "--format=@@%aI%x09%H%x09%an", "--name-only")
        for line in log.splitlines():
            if line.startswith("@@"):
                lastmod, commit, author = line[2:].split("\t", 2)
                current = {
                    "lastmod": lastmod,
                    "commit": commit,
                    "author": author,
                    "commit_url": f"{repository.web_url}/commit/{commit}",
                }
            elif line and current and line not in history:
                history[line] = current
        result[repository.local_path] = history
    return result

def metadata_for(path: Path, repos, history):
    repository, relative = locate(path, repos)
    return history[repository.local_path].get(relative.as_posix())

def edit_source(path: Path, repos: list[Repository]) -> dict[str, str]:
    repository, relative = locate(path, repos)
    return {
        "path": path.as_posix(),
        "repository": repository.web_url.rsplit("/", 1)[-1],
        "edit_url": f"{repository.web_url}/edit/{repository.branch}/{quote(relative.as_posix(), safe='/')}",
    }

def markdown_without_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", text))

def main() -> None:
    repos = repositories()
    history = histories(repos)
    output = {}
    missing = []

    for content_root in content_roots():
        directory = ROOT / content_root
        if not directory.is_dir():
            continue
        for page in directory.rglob("*.md"):
            page_path = page.relative_to(ROOT)
            text = markdown_without_code(page.read_text(encoding="utf-8"))
            included = []
            for value in INCLUDE_RE.findall(text):
                include_path = Path(value.lstrip("/\\"))
                if (ROOT / include_path).is_file():
                    included.append(include_path)
                else:
                    missing.append((page_path, include_path))

            candidates = [page_path, *included]
            changes = [item for path in candidates if (item := metadata_for(path, repos, history))]
            latest = max(changes, key=lambda item: datetime.fromisoformat(item["lastmod"])) if changes else None

            sources = []
            seen = set()
            for path in included or [page_path]:
                source = edit_source(path, repos)
                if source["edit_url"] not in seen:
                    sources.append(source)
                    seen.add(source["edit_url"])
            entry = {"edit_sources": sources}
            if latest:
                entry["last_change"] = latest
            output[page_path.as_posix()] = entry

    if missing:
        details = "\n".join(f"- {page}: {path}" for page, path in missing)
        raise SystemExit(f"Included files not found:\n{details}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated metadata for {len(output)} pages in {OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
