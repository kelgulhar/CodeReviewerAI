"""MCP Server for Code Metrics Analysis"""
import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from codereviewerai.mcp.code_metrics_server.tools.complexity import calculate_complexity, analyze_repository_complexity
from codereviewerai.mcp.code_metrics_server.tools.statistics import get_code_statistics
from codereviewerai.mcp.code_metrics_server.tools.duplication import detect_duplication
from codereviewerai.mcp.code_metrics_server.tools.dependencies import analyze_dependencies
from codereviewerai.mcp.code_metrics_server.tools.security_patterns import scan_security_patterns


# Create MCP server
server = Server("code-metrics-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="calculate_code_metrics",
            description="Calculates code complexity metrics (cyclomatic complexity, function complexity) for a file or repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to a Python file or repository directory"
                    },
                    "analyze_repository": {
                        "type": "boolean",
                        "description": "If true, analyzes entire repository; if false, analyzes single file",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_code_statistics",
            description="Gets general code statistics for a repository (lines of code, file counts, file types)",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="detect_code_duplication",
            description="Detects code duplication in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository"
                    },
                    "min_lines": {
                        "type": "integer",
                        "description": "Minimum number of lines for a duplicate block",
                        "default": 5
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="analyze_dependencies",
            description="Analyzes dependencies between modules/components in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, etc.)",
                        "default": "python"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="scan_security_patterns",
            description="Scans code for known security patterns and vulnerabilities (hardcoded secrets, SQL injection, XSS, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the repository"
                    }
                },
                "required": ["repo_path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "calculate_code_metrics":
            file_path = arguments.get("file_path")
            analyze_repo = arguments.get("analyze_repository", False)
            
            if analyze_repo:
                result = analyze_repository_complexity(file_path)
            else:
                result = calculate_complexity(file_path)
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_code_statistics":
            repo_path = arguments.get("repo_path")
            result = get_code_statistics(repo_path)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "detect_code_duplication":
            repo_path = arguments.get("repo_path")
            min_lines = arguments.get("min_lines", 5)
            result = detect_duplication(repo_path, min_lines)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_dependencies":
            repo_path = arguments.get("repo_path")
            language = arguments.get("language", "python")
            result = analyze_dependencies(repo_path, language)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "scan_security_patterns":
            repo_path = arguments.get("repo_path")
            result = scan_security_patterns(repo_path)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
