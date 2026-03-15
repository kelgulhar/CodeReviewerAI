from __future__ import annotations

import json
from pathlib import Path

from codereviewerai.tools.security_scanner import iter_candidate_files, safe_repo_root


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
    root = safe_repo_root(repo_path)
    results = []

    for path in iter_candidate_files(root):
        if path.name not in DEPENDENCY_FILES:
            continue

        rel = path.relative_to(root).as_posix()
        entry = {
            "file": rel,
            "type": path.name,
        }

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            entry["size_chars"] = len(content)

            if path.name == "requirements.txt":
                packages = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                entry["package_count"] = len(packages)
                entry["sample_packages"] = packages[:20]

            elif path.name == "package.json":
                data = json.loads(content)
                dependencies = list((data.get("dependencies") or {}).keys())
                dev_dependencies = list((data.get("devDependencies") or {}).keys())
                entry["dependency_count"] = len(dependencies)
                entry["dev_dependency_count"] = len(dev_dependencies)
                entry["sample_dependencies"] = dependencies[:20]
                entry["sample_dev_dependencies"] = dev_dependencies[:20]

            elif path.name == "pyproject.toml":
                entry["note"] = "pyproject.toml found; inspect dependency sections manually or extend parser later."

            else:
                entry["note"] = "Dependency file found; inspect manually or extend parser later."

        except Exception as e:
            entry["error"] = str(e)

        results.append(entry)

    return json.dumps(results, indent=2)