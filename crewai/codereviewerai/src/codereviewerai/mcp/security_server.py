from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from codereviewerai.tools.dependency_inspector import inspect_dependency_files_in_repo
from codereviewerai.tools.security_scanner import (
    find_security_related_files_in_repo,
    scan_for_secrets_in_repo,
)

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("codereviewerai_security_mcp")

mcp = FastMCP("codereviewerai-security")


@mcp.tool()
async def scan_for_secrets(
    repo_path: str,
    max_results: int = 100,
    max_file_size_kb: int = 256,
) -> str:
    """Scan a prepared repository for likely hardcoded secrets and sensitive material."""
    return scan_for_secrets_in_repo(
        repo_path=repo_path,
        max_results=max_results,
        max_file_size_kb=max_file_size_kb,
    )


@mcp.tool()
async def find_security_related_files(
    repo_path: str,
    max_results: int = 200,
) -> str:
    """Find files that are likely relevant for a security review."""
    return find_security_related_files_in_repo(
        repo_path=repo_path,
        max_results=max_results,
    )


@mcp.tool()
async def inspect_dependency_files(repo_path: str) -> str:
    """Locate dependency definition files and provide lightweight metadata for review."""
    return inspect_dependency_files_in_repo(repo_path=repo_path)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()