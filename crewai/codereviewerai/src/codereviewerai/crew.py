from crewai import Agent, Crew, Process, Task, LLM
from codereviewerai.tools.read_projects_json import ReadProjectTool
from codereviewerai.tools.clone_repo import CloneRepoTool
from codereviewerai.tools.run_static_analysis import RunStaticAnalysisTool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import DirectoryReadTool, FileReadTool, DirectorySearchTool
# from crewai_tools import SerperDevTool

import os

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

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
    def static_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['static_analyst'], # type: ignore[index]
            llm=self.local_llm,
            tools=[
                ReadProjectTool(),
                CloneRepoTool(),
                DirectoryReadTool(),
                FileReadTool(),
                RunStaticAnalysisTool(),
            ],
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=2,
            max_iter=12,
            respect_context_window=True,
        )

    @agent
    def architecture_design_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['architecture_design_analyst'],
            llm=self.local_llm,
            tools=[
                ReadProjectTool(),  # custom: projects.json -> repo URL
                CloneRepoTool(),  # custom: repo lokal clonen
                DirectoryReadTool(),  # built-in: Struktur lesen
                FileReadTool(),  # built-in: einzelne Dateien lesen
                # DirectorySearchTool(),  # built-in: semantisch im Repo suchen
                # CodeDocsSearchTool(),  # optional: Framework-/Lib-Doku
            ],
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=2,
            max_iter=12,
            respect_context_window=True,
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
