from __future__ import annotations

import json

from codereviewerai.tools.repo_utils import safe_repo_root, safe_target_dir


def find_files_in_repo(
    repo_path: str,
    pattern: str,
    max_results: int = 200,
) -> str:
    root = safe_repo_root(repo_path)

    if not pattern or not pattern.strip():
        raise ValueError("pattern must not be empty")

    matches = []
    for path in root.glob(pattern):
        if path.is_file():
            rel_path = path.relative_to(root).as_posix()
            matches.append(rel_path)

    matches = sorted(set(matches))[:max_results]
    return json.dumps(matches, indent=2)


def list_directory_in_repo(
    repo_path: str,
    relative_path: str = ".",
    max_entries: int = 200,
) -> str:
    target_dir = safe_target_dir(repo_path, relative_path)
    root = safe_repo_root(repo_path)

    entries = []
    for entry in sorted(target_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        entries.append(
            {
                "path": entry.relative_to(root).as_posix(),
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            }
        )

    return json.dumps(entries[:max_entries], indent=2)