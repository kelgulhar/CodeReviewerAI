from pathlib import Path
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
class ReadRepoFilesInput(BaseModel):
    repo_path: str = Field(..., description="Local path to a cloned repository.")
class ReadRepoFilesTool(BaseTool):
    name: str = "read_repo_files"
    description: str = "Reads source files from a repository and returns concatenated text."
    args_schema: Type[BaseModel] = ReadRepoFilesInput
    def _run(self, repo_path: str) -> str:
        exts = {".py", ".js", ".ts", ".java", ".go", ".rs"}
        parts = []
        for p in Path(repo_path).rglob("*"):
            if p.is_file() and p.suffix in exts and p.stat().st_size < 200_000:
                try:
                    parts.append(f"\n\n# FILE: {p}\n" + p.read_text(encoding="utf-8", errors="ignore"))
                except Exception:
                    pass
        return "\n".join(parts)[:200_000]  # hart begrenzen