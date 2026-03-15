from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

CACHE_ROOT = Path(tempfile.gettempdir()) / "codereviewerai_repos"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)

SKIP_TREE_NAMES = {".git", "node_modules", ".venv", "__pycache__"}


def repo_cache_path(repo_url: str) -> Path:
    repo_hash = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:16]
    return CACHE_ROOT / f"repo_{repo_hash}"


def safe_repo_root(repo_path: str) -> Path:
    root = Path(repo_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid repo_path: {repo_path}")
    return root


def safe_target_file(repo_path: str, relative_path: str) -> Path:
    root = safe_repo_root(repo_path)
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError("relative_path escapes repository root")

    if not target.exists() or not target.is_file():
        raise ValueError(f"File not found: {relative_path}")

    return target


def safe_target_dir(repo_path: str, relative_path: str = ".") -> Path:
    root = safe_repo_root(repo_path)
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError("relative_path escapes repository root")

    if not target.exists() or not target.is_dir():
        raise ValueError(f"Directory not found: {relative_path}")

    return target


def render_tree(root: Path, max_depth: int = 4) -> str:
    lines: list[str] = [f"{root.name}/"]

    def walk(current: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return

        children = sorted(
            [p for p in current.iterdir() if p.name not in SKIP_TREE_NAMES],
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )

        for idx, child in enumerate(children):
            connector = "+-- " if idx < len(children) - 1 else "`-- "
            lines.append(f"{prefix}{connector}{child.name}{'/' if child.is_dir() else ''}")

            if child.is_dir():
                extension = "|   " if idx < len(children) - 1 else "    "
                walk(child, prefix + extension, depth + 1)

    walk(root, "", 1)
    return "\n".join(lines)


def detect_languages(root: Path) -> set[str]:
    langs: set[str] = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix == ".py":
            langs.add("python")
        elif p.suffix in {".js", ".jsx", ".ts", ".tsx"}:
            langs.add("javascript/typescript")
        elif p.suffix == ".java":
            langs.add("java")
        elif p.suffix == ".go":
            langs.add("go")
        elif p.suffix == ".rs":
            langs.add("rust")
    return langs


def resolve_project(path: str) -> str:
    """Resolve the repository URL from a projects.json file."""
    file_path = Path(path).resolve()
    if not file_path.exists():
        raise ValueError(f"projects.json not found: {path}")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    project = data.get("project")

    if not isinstance(project, str) or not project.strip():
        raise ValueError("projects.json must contain a non-empty string field 'project'")

    return project.strip()


def clone_repo(repo_url: str) -> str:
    """Clone a Git repository into a local cache directory and return the local path."""
    repo_url = repo_url.strip()
    if not repo_url:
        raise ValueError("repo_url must not be empty")

    target_dir = repo_cache_path(repo_url)

    if target_dir.exists() and (target_dir / ".git").exists():
        return str(target_dir)

    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)

    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed: {result.stderr.strip() or result.stdout.strip()}")

    return str(target_dir)


def summarize_manifests_in_repo(repo_path: str) -> str:
    """Summarize architecture-relevant manifest/config files in the repository."""
    root = safe_repo_root(repo_path)
    findings: list[str] = []

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            findings.append(
                "package.json:\n"
                f"- name: {data.get('name')}\n"
                f"- dependencies: {', '.join(list((data.get('dependencies') or {}).keys())[:25]) or '(none)'}\n"
                f"- devDependencies: {', '.join(list((data.get('devDependencies') or {}).keys())[:25]) or '(none)'}"
            )
        except Exception as e:
            findings.append(f"package.json parse failed: {e}")

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            findings.append(
                "pyproject.toml:\n"
                f"- top-level keys: {', '.join(list(data.keys())[:20])}"
            )
        except Exception as e:
            findings.append(f"pyproject.toml parse failed: {e}")

    requirements = root / "requirements.txt"
    if requirements.exists():
        try:
            pkgs = [
                line.strip()
                for line in requirements.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            findings.append(
                "requirements.txt:\n"
                f"- packages: {', '.join(pkgs[:30]) or '(none)'}"
            )
        except Exception as e:
            findings.append(f"requirements.txt parse failed: {e}")

    tsconfig = root / "tsconfig.json"
    if tsconfig.exists():
        try:
            data = json.loads(tsconfig.read_text(encoding="utf-8"))
            compiler = data.get("compilerOptions", {})
            findings.append(
                "tsconfig.json:\n"
                f"- module: {compiler.get('module')}\n"
                f"- target: {compiler.get('target')}\n"
                f"- baseUrl: {compiler.get('baseUrl')}\n"
                f"- paths configured: {'paths' in compiler}"
            )
        except Exception as e:
            findings.append(f"tsconfig.json parse failed: {e}")

    langs = ", ".join(sorted(detect_languages(root))) or "(unknown)"
    findings.insert(0, f"Detected languages: {langs}")

    return "\n\n".join(findings) if findings else "No known manifest/config files found."