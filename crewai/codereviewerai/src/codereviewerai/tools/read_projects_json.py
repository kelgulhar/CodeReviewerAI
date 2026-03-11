import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ReadProjectInput(BaseModel):
    path: str = Field(..., description="Path to projects.json file.")


class ReadProjectTool(BaseTool):
    name: str = "read_project"
    description: str = "Reads the repository URL from a projects.json file and returns it."
    args_schema: Type[BaseModel] = ReadProjectInput

    def _run(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        project = data.get("project")
        if not isinstance(project, str) or not project.strip():
            raise ValueError("projects.json must contain a non-empty string field 'project'.")

        return project.strip()