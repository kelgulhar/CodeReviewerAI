import shutil
import subprocess
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RunStaticAnalysisInput(BaseModel):
    repo_path: str = Field(..., description="Local path to the cloned repository.")


class RunStaticAnalysisTool(BaseTool):
    name: str = "run_static_analysis"
    description: str = (
        "Runs installed static analysis tools against a local repository and returns "
        "deterministic findings. Supports Python via ruff/radon and JS/TS via eslint if available."
    )
    args_schema: Type[BaseModel] = RunStaticAnalysisInput

    def _run(self, repo_path: str) -> str:
        root = Path(repo_path)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid repo_path: {repo_path}")

        sections: list[str] = []

        def has_files(*suffixes: str) -> bool:
            return any(p.suffix in suffixes for p in root.rglob("*") if p.is_file())

        def run_cmd(title: str, cmd: list[str]) -> None:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
                output = output.strip() or "(no output)"
                sections.append(
                    f"## {title}\n"
                    f"Command: {' '.join(cmd)}\n"
                    f"Exit code: {result.returncode}\n\n"
                    f"{output[:12000]}"
                )
            except subprocess.TimeoutExpired:
                sections.append(f"## {title}\nCommand timed out.")
            except Exception as e:
                sections.append(f"## {title}\nFailed to execute: {e}")

        # Python
        if has_files(".py"):
            if shutil.which("ruff"):
                run_cmd("Ruff", ["ruff", "check", "."])
            else:
                sections.append("## Ruff\nSkipped: 'ruff' is not installed.")

            if shutil.which("radon"):
                run_cmd("Radon Complexity", ["radon", "cc", ".", "-s", "-n", "B"])
            else:
                sections.append("## Radon Complexity\nSkipped: 'radon' is not installed.")

        # JavaScript / TypeScript
        if has_files(".js", ".jsx", ".ts", ".tsx"):
            if shutil.which("eslint"):
                run_cmd(
                    "ESLint",
                    ["eslint", ".", "--ext", ".js,.jsx,.ts,.tsx"],
                )
            else:
                sections.append("## ESLint\nSkipped: 'eslint' is not installed.")

        if not sections:
            return "No supported source files or analyzers were found."

        return "\n\n".join(sections)[:30000]