from crewai import Agent, Crew, Process, Task, LLM
from codereviewerai.tools.clone_repo import CloneRepoTool
from codereviewerai.tools.read_files import ReadRepoFilesTool
from codereviewerai.tools.read_projects_json import ReadProjectTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool

import os

# MCP Integration - falls verfügbar
try:
    from codereviewerai.mcp.mcp_server import get_mcp_tools
    MCP_AVAILABLE = True
except Exception as e:
    print(f"Warning: MCP tools not available: {e}")
    MCP_AVAILABLE = False


@CrewBase
class Codereviewerai():
    """Codereviewerai crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # LLM Konfiguration - kann auch lokaler LLM verwendet werden
    # Hinweis: Bei Python 3.12 und litellm gibt es bekannte Logging-Fehler beim Shutdown, die ignoriert werden können
    local_llm = LLM(
        model=os.getenv("MODEL"),
        base_url="https://api.openai.com/v1",
        #base_url="https://daystrom.ditm.at:4000/v1",  # für lokalen LLM
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    def _get_mcp_tools(self):
        """Lädt MCP Tools falls verfügbar."""
        if not MCP_AVAILABLE:
            return []
        try:
            return get_mcp_tools()
        except Exception as e:
            print(f"Warning: Could not load MCP tools: {e}")
            return []

    @agent
    def static_analyst(self) -> Agent:
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["static_analyst"],  # type: ignore[index]
            llm=self.local_llm,
            tools=[
                ReadProjectTool(),
                CloneRepoTool(),
                ReadRepoFilesTool(),
                SerperDevTool(api_key=os.getenv("SERPER_API_KEY")),
            ]
            + mcp_tools,
            verbose=True,
        )

    @agent
    def security_reviewer(self) -> Agent:
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["security_reviewer"],  # type: ignore[index]
            llm=self.local_llm,
            tools=[
                CloneRepoTool(),
                ReadRepoFilesTool(),
                SerperDevTool(api_key=os.getenv("SERPER_API_KEY")),
            ]
            + mcp_tools,
            verbose=True,
        )

    @agent
    def architecture_design_analyst(self) -> Agent:
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["architecture_design_analyst"],  # type: ignore[index]
            llm=self.local_llm,
            tools=[CloneRepoTool(), ReadRepoFilesTool()] + mcp_tools,
            verbose=True,
        )

    @agent
    def performance_optimizer(self) -> Agent:
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["performance_optimizer"],  # type: ignore[index]
            llm=self.local_llm,
            tools=[CloneRepoTool(), ReadRepoFilesTool()] + mcp_tools,
            verbose=True,
        )

    @agent
    def code_quality_documentation_agent(self) -> Agent:
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["code_quality_documentation_agent"],  # type: ignore[index]
            llm=self.local_llm,
            tools=[CloneRepoTool(), ReadRepoFilesTool()] + mcp_tools,
            verbose=True,
        )

    @agent
    def report_agent(self) -> Agent:
        """Fasst die Ergebnisse der Analyse-Agenten zu einem Abschlussbericht zusammen."""
        mcp_tools = self._get_mcp_tools()
        return Agent(
            config=self.agents_config["report_agent"],  # type: ignore[index]
            llm=self.local_llm,
            tools=mcp_tools,
            verbose=True,
        )

    @task
    def static_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["static_analysis_task"],  # type: ignore[index]
            output_file="output/static_analysis.md",
        )

    @task
    def security_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["security_review_task"],  # type: ignore[index]
            output_file="output/security_review.md",
        )

    @task
    def architecture_design_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["architecture_design_review_task"],  # type: ignore[index]
            output_file="output/architecture_review.md",
        )

    @task
    def performance_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["performance_analysis_task"],  # type: ignore[index]
            output_file="output/performance_analysis.md",
        )

    @task
    def code_quality_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_quality_documentation_task"],  # type: ignore[index]
            output_file="output/code_quality_review.md",
        )

    @task
    def reporting_task(self) -> Task:
        """Erstellt den abschließenden Gesamtbericht auf Basis der vorherigen Analysen."""
        return Task(
            config=self.tasks_config["reporting_task"],  # type: ignore[index]
            output_file="output/final_report.md",
        )

    @crew
    def crew(self) -> Crew:
        """Erstellt die Codereviewerai Crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
