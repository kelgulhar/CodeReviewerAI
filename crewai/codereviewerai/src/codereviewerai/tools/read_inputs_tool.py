from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json


class ReadResearchAreasInput(BaseModel):
    """Input schema for ReadResearchAreasTool."""
    path: str = Field(..., description="Path to research areas file.")


class ReadResearchAreasTool(BaseTool):
    name: str = "Read Research Areas"
    description: str = (
        "Reads areas of research that the thesis topic should focus on"
    )
    args_schema: Type[BaseModel] = ReadResearchAreasInput


    def _run(self, path: str) -> str:

        with open(path) as f:
            data = json.load(f)

        return data["areas"]
