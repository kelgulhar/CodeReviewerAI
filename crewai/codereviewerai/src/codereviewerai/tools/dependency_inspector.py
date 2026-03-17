from __future__ import annotations

import json
from pathlib import Path

# Reuse repository-safe traversal helpers from the security scanner module.
# These helpers ensure that dependency inspection runs only on valid repository paths
# and skips irrelevant/generated directories consistently.
from codereviewerai.tools.security_scanner import iter_candidate_files, safe_repo_root


# Set of known dependency and package management files across multiple ecosystems.
# These files are used as lightweight indicators for dependency structure and supply-chain risk.
DEPENDENCY_FILES = {
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pom.xml",
    "build.gradle",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
}


def inspect_dependency_files_in_repo(repo_path: str) -> str:
    # Validate and normalize the repository root path.
    root = safe_repo_root(repo_path)

    # Collect lightweight metadata for all matching dependency files.
    results = []

    # Iterate only over candidate files that are relevant and not inside skipped folders.
    for path in iter_candidate_files(root):
        if path.name not in DEPENDENCY_FILES:
            continue

        # Store file path relative to repository root for cleaner reporting.
        rel = path.relative_to(root).as_posix()
        entry = {
            "file": rel,
            "type": path.name,
        }

        try:
            # Read file content in a fault-tolerant way to avoid crashes on encoding issues.
            content = path.read_text(encoding="utf-8", errors="ignore")
            entry["size_chars"] = len(content)

            # Basic parsing logic for Python requirements files.
            # Extracts non-comment package lines and provides a short sample.
            if path.name == "requirements.txt":
                packages = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                entry["package_count"] = len(packages)
                entry["sample_packages"] = packages[:20]

            # Basic parsing logic for Node.js package manifests.
            # Separates runtime dependencies and development dependencies.
            elif path.name == "package.json":
                data = json.loads(content)
                dependencies = list((data.get("dependencies") or {}).keys())
                dev_dependencies = list((data.get("devDependencies") or {}).keys())
                entry["dependency_count"] = len(dependencies)
                entry["dev_dependency_count"] = len(dev_dependencies)
                entry["sample_dependencies"] = dependencies[:20]
                entry["sample_dev_dependencies"] = dev_dependencies[:20]

            # pyproject.toml is detected but not deeply parsed yet.
            # This leaves room for future extension with tomllib-based dependency extraction.
            elif path.name == "pyproject.toml":
                entry["note"] = "pyproject.toml found; inspect dependency sections manually or extend parser later."

            # Fallback for dependency files that are recognized but not yet parsed in detail.
            else:
                entry["note"] = "Dependency file found; inspect manually or extend parser later."

        except Exception as e:
            # Preserve errors in the result instead of failing the entire inspection.
            # This keeps the tool robust even if individual files are malformed.
            entry["error"] = str(e)

        results.append(entry)

    # Return the collected dependency metadata as structured JSON.
    return json.dumps(results, indent=2)