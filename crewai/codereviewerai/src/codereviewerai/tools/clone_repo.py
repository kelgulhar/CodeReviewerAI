import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# Input schema for the tool.
# Defines the expected argument structure when the tool is called by an agent.
class CloneRepoInput(BaseModel):
    repo_url: str = Field(..., description="Git repository URL to clone.")


# Custom CrewAI tool for cloning repositories.
# This tool can be used by agents to fetch a repository locally.
class CloneRepoTool(BaseTool):
    name: str = "clone_repo"
    description: str = "Clones a Git repository into a local cache directory and returns the local path."
    args_schema: Type[BaseModel] = CloneRepoInput

    def _run(self, repo_url: str) -> str:
        # Normalize and validate input.
        repo_url = repo_url.strip()
        if not repo_url:
            raise ValueError("repo_url must not be empty.")

        # Create a deterministic cache directory based on the repo URL.
        # This avoids cloning the same repository multiple times.
        repo_hash = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:16]
        target_dir = Path(tempfile.gettempdir()) / f"repo_{repo_hash}"

        # If the repository already exists and looks valid, reuse it.
        if target_dir.exists() and (target_dir / ".git").exists():
            return str(target_dir)

        # If the directory exists but is incomplete or corrupted, remove it.
        if target_dir.exists():
            # Falls da irgendetwas Halbfertiges liegt
            subprocess.run(["rm", "-rf", str(target_dir)], check=False)

        # Clone the repository with shallow depth to reduce download size and time.
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
        )

        # Return the local path to the cloned repository.
        return str(target_dir)