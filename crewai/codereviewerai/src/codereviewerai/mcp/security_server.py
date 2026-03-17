from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

# Import of reusable security-related analysis logic.
# These modules contain the actual implementation of scanning and detection.
# The MCP server only exposes them as callable tools.
from codereviewerai.tools.dependency_inspector import inspect_dependency_files_in_repo
from codereviewerai.tools.security_scanner import (
    find_security_related_files_in_repo,
    scan_for_secrets_in_repo,
)

# Configure logging for the security MCP server.
# Logging is routed to stderr, which is standard for stdio-based MCP communication.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("codereviewerai_security_mcp")

# Initialize MCP server instance for security-related tools.
mcp = FastMCP("codereviewerai-security")


@mcp.tool()
async def scan_for_secrets(
    repo_path: str,
    max_results: int = 100,
    max_file_size_kb: int = 256,
) -> str:
    """Scan a prepared repository for likely hardcoded secrets and sensitive material."""
    # Delegates secret detection to the reusable scanner logic.
    # This includes pattern-based detection of API keys, passwords, tokens, etc.
    # The result is returned as a JSON string containing findings.
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
    # Identifies files that are likely security-relevant based on naming heuristics.
    # Examples: auth, config, credentials, environment files, etc.
    # This helps guide the agent toward critical areas of the codebase.
    return find_security_related_files_in_repo(
        repo_path=repo_path,
        max_results=max_results,
    )


@mcp.tool()
async def inspect_dependency_files(repo_path: str) -> str:
    """Locate dependency definition files and provide lightweight metadata for review."""
    # Analyzes dependency-related files such as requirements.txt, package.json, etc.
    # Provides metadata (e.g., number of dependencies, sample entries)
    # that can be used to assess potential supply chain risks.
    return inspect_dependency_files_in_repo(repo_path=repo_path)


def main() -> None:
    # Start the MCP server using stdio transport.
    # This allows CrewAI agents to communicate with the server.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # Entry point for running the security MCP server directly.
    main()