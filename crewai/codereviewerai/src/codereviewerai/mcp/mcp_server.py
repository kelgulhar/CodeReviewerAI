"""MCP Server Adapter for CodeReviewerAI"""
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from typing import List


def get_mcp_tools() -> List:
    """
    Initializes and returns MCP tools from the Code Metrics MCP Server.
    
    Returns:
        List of MCP tools that can be used by CrewAI agents.
    """
    server_params = [
        StdioServerParameters(
            command="python",
            args=[
                "-m",
                "codereviewerai.mcp.code_metrics_server.server"
            ]
        )
    ]
    
    adapter = MCPServerAdapter(server_params)
    return adapter.tools
