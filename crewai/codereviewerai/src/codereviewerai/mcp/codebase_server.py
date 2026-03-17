from __future__ import annotations

import json
import logging
import sys

from mcp.server.fastmcp import FastMCP

# Import of reusable repository file discovery helpers.
# These functions contain the actual logic; this MCP server only exposes them as tools.
from codereviewerai.tools.file_discovery import (
    find_files_in_repo,
    list_directory_in_repo,
)

# Import of reusable repository setup and inspection helpers.
# The server delegates cloning, path validation, tree rendering,
# and manifest summarization to these tool functions.
from codereviewerai.tools.repo_utils import (
    clone_repo,
    render_tree,
    resolve_project,
    safe_repo_root,
    safe_target_file,
    summarize_manifests_in_repo,
)

# Configure basic logging for MCP server execution.
# Logging to stderr is typical for stdio-based MCP servers.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("codereviewerai_mcp")

# Create the MCP server instance that exposes codebase-related tools.
mcp = FastMCP("codereviewerai-codebase")


@mcp.tool()
async def find_files(
    repo_path: str,
    pattern: str,
    max_results: int = 200,
) -> str:
    """Find files in a prepared repository by glob pattern.
    Args:
        repo_path: Local repository path returned by prepare_repository.
        pattern: Glob pattern relative to repository root, e.g. '**/*.py' or '**/*test*.py'.
        max_results: Maximum number of matching files to return.
    """
    # Delegates file lookup to the extracted tool logic.
    # Returns a JSON string with matching relative file paths.
    return find_files_in_repo(
        repo_path=repo_path,
        pattern=pattern,
        max_results=max_results,
    )


@mcp.tool()
async def list_directory(
    repo_path: str,
    relative_path: str = ".",
    max_entries: int = 200,
) -> str:
    """List files and directories directly inside a repository directory.
    Args:
        repo_path: Local repository path returned by prepare_repository.
        relative_path: Directory relative to repository root.
        max_entries: Maximum number of entries to return.
    """
    # Delegates safe directory listing to the extracted tool logic.
    # Returns a JSON string describing files and subdirectories.
    return list_directory_in_repo(
        repo_path=repo_path,
        relative_path=relative_path,
        max_entries=max_entries,
    )


@mcp.tool()
async def prepare_repository(path: str, max_depth: int = 4) -> str:
    """Resolve the repository URL from projects.json, clone the repository, and return shared setup data.
    This tool enforces the required setup order:
    1. Resolve the repository URL from the input path.
    2. Clone the repository.
    3. Build the repository tree.
    4. Summarize manifests.
    Args:
        path: Absolute or relative path to projects.json.
        max_depth: Maximum traversal depth for the repository tree.
    """
    # Resolve the repository URL from the provided projects.json file.
    repo_url = resolve_project(path)

    # Clone the repository into the local cache and return the local path.
    repo_path = clone_repo(repo_url)

    # Build a textual overview of the repository structure for downstream agents.
    repo_tree = render_tree(safe_repo_root(repo_path), max_depth=max_depth)

    # Summarize key manifest/configuration files to provide architectural context.
    manifest_summary = summarize_manifests_in_repo(repo_path)

    # Return all setup data as a structured JSON string.
    # This output is consumed by later tasks and agents.
    return json.dumps(
        {
            "repo_url": repo_url,
            "repo_path": repo_path,
            "repo_tree": repo_tree,
            "manifest_summary": manifest_summary,
        },
        indent=2,
    )


@mcp.tool()
async def get_repo_tree(repo_path: str, max_depth: int = 4) -> str:
    """Return a directory tree of a local cloned repository.
    Args:
        repo_path: Local repository path returned by prepare_repository.
        max_depth: Maximum traversal depth.
    """
    # Validate that the given path points to a valid local repository root.
    root = safe_repo_root(repo_path)

    # Return a textual tree representation of the repository.
    return render_tree(root, max_depth=max_depth)


@mcp.tool()
async def read_file(repo_path: str, relative_path: str, max_chars: int = 20000) -> str:
    """Read a single file from a local cloned repository.
    Args:
        repo_path: Local repository path returned by prepare_repository.
        relative_path: Path relative to repository root.
        max_chars: Maximum number of characters to return.
    """
    # Validate that the requested file stays inside the repository boundary.
    target = safe_target_file(repo_path, relative_path)

    # Read the file content in a fault-tolerant way and truncate the result
    # to keep tool responses bounded for LLM consumption.
    content = target.read_text(encoding="utf-8", errors="ignore")
    return content[:max_chars]


@mcp.tool()
async def summarize_manifests(repo_path: str) -> str:
    """Summarize manifest/config files for a local cloned repository.
    Args:
        repo_path: Local repository path returned by prepare_repository.
    """
    # Delegates manifest summarization to the reusable repository utility logic.
    return summarize_manifests_in_repo(repo_path)


def main() -> None:
    # Start the MCP server using stdio transport so CrewAI can communicate with it.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # Entry point for running the server as a Python module/script.
    main()