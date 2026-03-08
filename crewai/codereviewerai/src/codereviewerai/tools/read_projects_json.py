from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json

class ReadProjectInput(BaseModel):
    path: str = Field(..., description="Path to projects.json file.")

class ReadProjectTool(BaseTool):
    name: str = "read_project"
    description: str = "Reads a repository URL from a projects.json file and returns it."
    args_schema: Type[BaseModel] = ReadProjectInput

    def _run(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return str(data["project"])