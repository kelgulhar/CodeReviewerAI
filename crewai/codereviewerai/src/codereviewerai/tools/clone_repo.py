import subprocess, tempfile, os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class CloneRepoInput(BaseModel):
    repo_url: str = Field(..., description="Git repository URL to clone.")

class CloneRepoTool(BaseTool):
    name: str = "clone_repo"
    description: str = "Clones a Git repo into a temporary directory and returns the local path."
    args_schema: Type[BaseModel] = CloneRepoInput

    def _run(self, repo_url: str) -> str:
        tmp_dir = tempfile.mkdtemp(prefix="repo_")
        subprocess.check_call(["git", "clone", "--depth", "1", repo_url, tmp_dir])
        return tmp_dir