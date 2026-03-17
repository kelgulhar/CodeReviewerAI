import shutil
import subprocess
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# Input schema defining the expected argument for the tool.
# The tool requires a local repository path (already prepared/cloned).
class RunStaticAnalysisInput(BaseModel):
    repo_path: str = Field(..., description="Local path to the cloned repository.")


# Custom CrewAI tool that runs external static analysis tools on the repository.
# It aggregates results from multiple analyzers into a structured report.
class RunStaticAnalysisTool(BaseTool):
    name: str = "run_static_analysis"
    description: str = (
        "Runs installed static analysis tools against a local repository and returns "
        "deterministic findings. Supports Python via ruff/radon and JS/TS via eslint if available."
    )
    args_schema: Type[BaseModel] = RunStaticAnalysisInput

    def _run(self, repo_path: str) -> str:
        # Validate repository path.
        root = Path(repo_path)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid repo_path: {repo_path}")

        # Collect output sections for different analysis tools.
        sections: list[str] = []

        # Helper function to detect if files with certain suffixes exist in the repo.
        # Used to decide which analyzers to run.
        def has_files(*suffixes: str) -> bool:
            return any(p.suffix in suffixes for p in root.rglob("*") if p.is_file())

        # Helper function to execute a subprocess command and collect its output.
        def run_cmd(title: str, cmd: list[str]) -> None:
            try:
                # Execute command in repository directory.
                result = subprocess.run(
                    cmd,
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )

                # Combine stdout and stderr for reporting.
                output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
                output = output.strip() or "(no output)"

                # Append formatted result section.
                sections.append(
                    f"## {title}\n"
                    f"Command: {' '.join(cmd)}\n"
                    f"Exit code: {result.returncode}\n\n"
                    f"{output[:12000]}"
                )

            # Handle timeout explicitly.
            except subprocess.TimeoutExpired:
                sections.append(f"## {title}\nCommand timed out.")

            # Catch-all for unexpected execution errors.
            except Exception as e:
                sections.append(f"## {title}\nFailed to execute: {e}")

        # --- Python analysis ---
        # Only run Python tools if Python files are present.
        if has_files(".py"):
            # Run Ruff if installed (fast linter).
            if shutil.which("ruff"):
                run_cmd("Ruff", ["ruff", "check", "."])
            else:
                sections.append("## Ruff\nSkipped: 'ruff' is not installed.")

            # Run Radon for complexity analysis if available.
            if shutil.which("radon"):
                run_cmd("Radon Complexity", ["radon", "cc", ".", "-s", "-n", "B"])
            else:
                sections.append("## Radon Complexity\nSkipped: 'radon' is not installed.")

        # --- JavaScript / TypeScript analysis ---
        # Only run ESLint if JS/TS files are present.
        if has_files(".js", ".jsx", ".ts", ".tsx"):
            if shutil.which("eslint"):
                run_cmd(
                    "ESLint",
                    ["eslint", ".", "--ext", ".js,.jsx,.ts,.tsx"],
                )
            else:
                sections.append("## ESLint\nSkipped: 'eslint' is not installed.")

        # If no tools were applicable or available, return fallback message.
        if not sections:
            return "No supported source files or analyzers were found."

        # Return combined report, truncated to avoid overly large outputs.
        return "\n\n".join(sections)[:30000]