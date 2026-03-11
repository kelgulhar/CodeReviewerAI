import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CloneRepoInput(BaseModel):
    repo_url: str = Field(..., description="Git repository URL to clone.")


class CloneRepoTool(BaseTool):
    name: str = "clone_repo"
    description: str = "Clones a Git repository into a local cache directory and returns the local path."
    args_schema: Type[BaseModel] = CloneRepoInput

    def _run(self, repo_url: str) -> str:
        repo_url = repo_url.strip()
        if not repo_url:
            raise ValueError("repo_url must not be empty.")

        repo_hash = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:16]
        target_dir = Path(tempfile.gettempdir()) / f"repo_{repo_hash}"

        if target_dir.exists() and (target_dir / ".git").exists():
            return str(target_dir)

        if target_dir.exists():
            # Falls da irgendetwas Halbfertiges liegt
            subprocess.run(["rm", "-rf", str(target_dir)], check=False)

        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        return str(target_dir)