from __future__ import annotations

import json

# Reuse repository validation helpers to ensure all file operations
# stay within the prepared repository boundaries.
from codereviewerai.tools.repo_utils import safe_repo_root, safe_target_dir


def find_files_in_repo(
    repo_path: str,
    pattern: str,
    max_results: int = 200,
) -> str:
    # Validate and normalize the repository root path.
    root = safe_repo_root(repo_path)

    # Reject empty or whitespace-only patterns early.
    if not pattern or not pattern.strip():
        raise ValueError("pattern must not be empty")

    # Collect all matching files relative to the repository root.
    matches = []
    for path in root.glob(pattern):
        if path.is_file():
            rel_path = path.relative_to(root).as_posix()
            matches.append(rel_path)

    # Deduplicate, sort for deterministic output, and limit the result size.
    matches = sorted(set(matches))[:max_results]

    # Return the result as a JSON string for MCP/tool consumption.
    return json.dumps(matches, indent=2)


def list_directory_in_repo(
    repo_path: str,
    relative_path: str = ".",
    max_entries: int = 200,
) -> str:
    # Validate that the requested directory exists inside the repository.
    target_dir = safe_target_dir(repo_path, relative_path)

    # Also resolve the repository root for clean relative path reporting.
    root = safe_repo_root(repo_path)

    # Build a structured list of direct child entries in the target directory.
    entries = []
    for entry in sorted(target_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        entries.append(
            {
                "path": entry.relative_to(root).as_posix(),
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            }
        )

    # Return at most max_entries items as structured JSON.
    return json.dumps(entries[:max_entries], indent=2)