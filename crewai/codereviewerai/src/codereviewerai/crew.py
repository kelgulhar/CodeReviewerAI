from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from codereviewerai.tools.read_projects_json import ReadProjectTool
from codereviewerai.tools.clone_repo import CloneRepoTool
from codereviewerai.tools.run_static_analysis import RunStaticAnalysisTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import DirectoryReadTool, FileReadTool
# from crewai_tools import SerperDevTool
from crewai.mcp import MCPServerStdio
from crewai.mcp.filters import create_static_tool_filter

import os
import sys

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

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

class RepoSetup(BaseModel):
    repo_url: str
    repo_path: str
    repo_tree: str
    manifest_summary: str

@CrewBase
class Codereviewerai():
    """Codereviewerai crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    local_llm = LLM(
        model=os.getenv("MODEL"),
        base_url="https://api.openai.com/v1",
        #base_url="https://daystrom.ditm.at:4000/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    @agent
    def repo_setup_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["repo_setup_agent"],
            llm=self.local_llm,
            mcps=[
                make_codebase_mcp([
                    "prepare_repository",
                ])
            ],
            verbose=True,
            max_iter=3,
            respect_context_window=True,
        )

    @agent
    def static_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['static_analyst'], # type: ignore[index]
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),
                FileReadTool(),
                RunStaticAnalysisTool(),
            ],
            mcps=[
                make_codebase_mcp([
                    "get_repo_tree",
                    "read_file",
                    "summarize_manifests",
                ])
            ],
            verbose=True,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def architecture_design_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_design_analyst'],
            llm=self.local_llm,
            tools=[
                DirectoryReadTool(),  # built-in: Struktur lesen
                FileReadTool(),  # built-in: einzelne Dateien lesen
            ],
            mcps=[
                make_codebase_mcp([
                    "get_repo_tree",
                    "read_file",
                    "summarize_manifests",
                ])
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
            config=self.tasks_config['static_analysis_task'], # type: ignore[index]
            output_file='output/static_analysis.md',
        )

    @task
    def architecture_design_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["architecture_design_review_task"],  # type: ignore[index]
            output_file="output/architecture_review.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Codereviewerai crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
