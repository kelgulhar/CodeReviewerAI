from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Iterator

# Module-level logger for non-fatal scanning problems.
# Warnings are useful here because individual file failures should not abort the full scan.
logger = logging.getLogger(__name__)


# Pattern-based rules for detecting likely secrets or sensitive material.
# Each rule carries a human-readable type label and a severity for reporting.
SECRET_PATTERNS = [
    {
        "name": "AWS Access Key",
        "severity": "high",
        "pattern": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    },
    {
        "name": "GitHub Token",
        "severity": "high",
        "pattern": re.compile(r"\bghp_[A-Za-z0-9]{36,}\b"),
    },
    {
        "name": "GitHub Fine-grained Token",
        "severity": "high",
        "pattern": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    },
    {
        "name": "Slack Token",
        "severity": "high",
        "pattern": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    },
    {
        "name": "Private Key Block",
        "severity": "critical",
        "pattern": re.compile(r"-----BEGIN (RSA|DSA|EC|OPENSSH|PGP)? ?PRIVATE KEY-----"),
    },
    {
        "name": "Hardcoded Password Assignment",
        "severity": "high",
        "pattern": re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
    },
    {
        "name": "Hardcoded Secret Assignment",
        "severity": "high",
        "pattern": re.compile(r"(?i)\b(secret|api[_-]?key|token)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    },
]

# Heuristic keywords used to identify files that are likely security-relevant.
# These are used for discovery, not for confirmed vulnerability findings.
SECURITY_FILE_HINTS = [
    "auth",
    "login",
    "jwt",
    "token",
    "session",
    "permission",
    "role",
    "acl",
    "oauth",
    "security",
    "secret",
    "credential",
    "crypto",
    "middleware",
    "guard",
]

# Directory names that should be ignored during repository traversal.
# These are typically generated, cached, external, or otherwise low-value for source review.
SKIP_PARTS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".next",
    ".nuxt",
    "coverage",
}


def safe_repo_root(repo_path: str) -> Path:
    # Resolve the repository path and verify that it exists and is a directory.
    # This acts as the basic safety check for all later filesystem operations.
    root = Path(repo_path).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid repo_path: {repo_path}")
    return root


def should_skip(path: Path) -> bool:
    # Skip any file or directory path that contains one of the configured ignored parts.
    # This helps reduce noise and avoids scanning vendor/build/cache directories.
    return any(part in SKIP_PARTS for part in path.parts)


def iter_candidate_files(root: Path) -> Iterator[Path]:
    # Yield only real files that are not located in skipped directories.
    # This centralizes traversal rules so they are reused consistently by all scanners.
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        yield path


def scan_for_secrets_in_repo(
    repo_path: str,
    max_results: int = 100,
    max_file_size_kb: int = 256,
) -> str:
    # Validate the repository root and initialize result collection.
    root = safe_repo_root(repo_path)
    findings = []

    # Convert maximum file size threshold to bytes.
    # Very large files are skipped to keep scanning efficient.
    max_bytes = max_file_size_kb * 1024

    # Traverse all candidate files that are worth inspecting.
    for path in iter_candidate_files(root):
        try:
            # Skip unusually large files to reduce runtime and avoid unhelpful scanning noise.
            if path.stat().st_size > max_bytes:
                continue

            # Read file content in a fault-tolerant way so encoding issues do not break the scan.
            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # Check each line against all configured secret patterns.
            for idx, line in enumerate(lines, start=1):
                for rule in SECRET_PATTERNS:
                    if rule["pattern"].search(line):
                        findings.append(
                            {
                                "file": path.relative_to(root).as_posix(),
                                "line": idx,
                                "severity": rule["severity"],
                                "type": rule["name"],
                                "preview": line.strip()[:200],
                            }
                        )
                        # Stop early once the configured maximum number of findings is reached.
                        if len(findings) >= max_results:
                            return json.dumps(findings, indent=2)

        except Exception as e:
            # File-level failures are logged as warnings, but the scan continues.
            logger.warning("Failed to scan file %s: %s", path, e)

    # Return all collected findings as structured JSON.
    return json.dumps(findings, indent=2)


def find_security_related_files_in_repo(
    repo_path: str,
    max_results: int = 200,
) -> str:
    # Validate the repository root and initialize result collection.
    root = safe_repo_root(repo_path)
    results = []

    # Traverse candidate files and look for security-relevant names or paths.
    for path in iter_candidate_files(root):
        rel = path.relative_to(root).as_posix()
        rel_lower = rel.lower()
        name_lower = path.name.lower()

        # Match either on broader path/name hints or on a small set of known configuration filenames.
        if (
            any(hint in rel_lower for hint in SECURITY_FILE_HINTS)
            or name_lower in {
                ".env",
                ".env.example",
                ".env.local",
                "docker-compose.yml",
                "docker-compose.yaml",
                "dockerfile",
                "nginx.conf",
                "apache.conf",
                "settings.py",
                "config.py",
            }
        ):
            results.append(rel)

    # Deduplicate, sort for deterministic output, and cap the number of returned items.
    results = sorted(set(results))[:max_results]

    # Return the discovered security-relevant file paths as structured JSON.
    return json.dumps(results, indent=2)