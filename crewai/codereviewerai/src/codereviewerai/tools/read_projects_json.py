import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Input schema defining the expected argument for the tool.
# Ensures that the tool is called with a valid path to a projects.json file.
class ReadProjectInput(BaseModel):
    path: str = Field(..., description="Path to projects.json file.")


# Custom CrewAI tool that extracts the repository URL from a projects.json file.
class ReadProjectTool(BaseTool):
    name: str = "read_project"
    description: str = "Reads the repository URL from a projects.json file and returns it."
    args_schema: Type[BaseModel] = ReadProjectInput

    def _run(self, path: str) -> str:
        # Open and parse the JSON file containing the project configuration.
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract the "project" field, which should contain the repository URL.
        project = data.get("project")

        # Validate that the field exists and is a non-empty string.
        if not isinstance(project, str) or not project.strip():
            raise ValueError("projects.json must contain a non-empty string field 'project'.")

        # Return the cleaned repository URL.
        return project.strip()