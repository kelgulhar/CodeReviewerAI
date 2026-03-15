import os
import sys

from typing import List
from pydantic import BaseModel

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.mcp import MCPServerStdio
from crewai.mcp.filters import create_static_tool_filter
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import DirectoryReadTool, FileReadTool

from codereviewerai.tools.run_static_analysis import RunStaticAnalysisTool


def make_codebase_mcp(allowed_tool_names: list[str]) -> MCPServerStdio:
    return MCPServerStdio(
        command=sys.executable,
        args=["-m", "codereviewerai.mcp.codebase_server"],
        env={**os.environ},
        tool_filter=create_static_tool_filter(
            allowed_tool_names=allowed_tool_names
        ),
        cache_tools_list=True,
    )

def make_security_mcp(allowed_tool_names: list[str]) -> MCPServerStdio:
    return MCPServerStdio(
        command=sys.executable,
        args=["-m", "codereviewerai.mcp.security_server"],
        env={**os.environ},
        tool_filter=create_static_tool_filter(
            allowed_tool_names=allowed_tool_names
        ),
        cache_tools_list=True,
    )

class RepoSetup(BaseModel):
    repo_url: str
    repo_path: str
    repo_tree: str
    manifest_summary: str


@CrewBase
class Codereviewerai:
    """Codereviewerai crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    local_llm = LLM(
        model=os.getenv("MODEL"),
        base_url="https://api.openai.com/v1",
        # base_url="https://daystrom.ditm.at:4000/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    @agent
    def repo_setup_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["repo_setup_agent"],
            llm=self.local_llm,
            mcps=[
                make_codebase_mcp(
                    [
                        "prepare_repository",
                    ]
                )
            ],
            verbose=True,
            max_iter=3,
            respect_context_window=True,
        )

    @agent
    def static_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["static_analyst"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
                RunStaticAnalysisTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                )
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def security_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["security_reviewer"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                ),
                make_security_mcp(
                    [
                        "scan_for_secrets",
                        "find_security_related_files",
                        "inspect_dependency_files",
                    ]
                ),
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def architecture_design_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["architecture_design_analyst"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                )
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def performance_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config["performance_optimizer"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                )
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def code_quality_documentation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["code_quality_documentation_agent"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                )
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def test_coverage_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["test_coverage_agent"],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
            ],
            mcps=[
                make_codebase_mcp(
                    [
                        "get_repo_tree",
                        "read_file",
                        "summarize_manifests",
                        "find_files",
                        "list_directory",
                    ]
                )
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @task
    def prepare_repo_task(self) -> Task:
        return Task(
            config=self.tasks_config["prepare_repo_task"],
            output_json=RepoSetup,
            output_file="output/repo_setup.json",
        )

    @task
    def static_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["static_analysis_task"],
            output_file="output/static_analysis.md",
        )

    @task
    def security_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["security_review_task"],
            output_file="output/security_review.md",
        )

    @task
    def architecture_design_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["architecture_design_review_task"],
            output_file="output/architecture_review.md",
        )

    @task
    def performance_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["performance_analysis_task"],
            output_file="output/performance_analysis.md",
        )

    @task
    def code_quality_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_quality_documentation_task"],
            output_file="output/code_quality_documentation.md",
        )

    @task
    def test_coverage_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_coverage_analysis_task"],
            output_file="output/test_coverage_analysis.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Codereviewerai crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )