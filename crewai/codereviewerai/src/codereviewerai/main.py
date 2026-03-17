#!/usr/bin/env python
import json
import sys
import warnings

from codereviewerai.crew import Codereviewerai

# Suppress known syntax warnings from pysbd to keep CLI output cleaner.
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew locally with the default projects.json input.
    """
    # Default input file used for local runs.
    # The path points to the projects.json file that contains the repository URL.
    inputs = {
        "path": "./input/projects.json",
    }

    try:
        # Create the crew and start execution with the configured inputs.
        Codereviewerai().crew().kickoff(inputs=inputs)
    except Exception as e:
        # Wrap any runtime error with a clearer project-specific message.
        raise Exception(f"An error occurred while running the crew: {e}") from e


def train():
    """
    Train the crew for a given number of iterations.
    Usage:
        python -m codereviewerai.main train <n_iterations> <filename> [path]
    """
    # Validate required CLI arguments for training mode.
    if len(sys.argv) < 4:
        raise Exception(
            "Usage: train <n_iterations> <filename> [path_to_projects_json]"
        )

    # Allow overriding the default input file via CLI.
    input_path = sys.argv[4] if len(sys.argv) > 4 else "./input/projects.json"
    inputs = {
        "path": input_path,
    }

    try:
        # Train the crew for the given number of iterations and save results to a file.
        Codereviewerai().crew().train(
            n_iterations=int(sys.argv[2]),
            filename=sys.argv[3],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}") from e


def replay():
    """
    Replay the crew execution from a specific task.
    Usage:
        python -m codereviewerai.main replay <task_id>
    """
    # Validate required CLI arguments for replay mode.
    if len(sys.argv) < 3:
        raise Exception("Usage: replay <task_id>")

    try:
        # Replay execution starting from the specified task ID.
        Codereviewerai().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e


def test():
    """
    Test the crew execution and return the results.
    Usage:
        python -m codereviewerai.main test <n_iterations> <eval_llm> [path]
    """
    # Validate required CLI arguments for test mode.
    if len(sys.argv) < 4:
        raise Exception(
            "Usage: test <n_iterations> <eval_llm> [path_to_projects_json]"
        )

    # Allow overriding the default input file via CLI.
    input_path = sys.argv[4] if len(sys.argv) > 4 else "./input/projects.json"
    inputs = {
        "path": input_path,
    }

    try:
        # Run repeated test executions using the specified evaluation LLM.
        Codereviewerai().crew().test(
            n_iterations=int(sys.argv[2]),
            eval_llm=sys.argv[3],
            inputs=inputs,
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}") from e


def run_with_trigger():
    """
    Run the crew with a trigger payload.
    Usage:
        python -m codereviewerai.main run_with_trigger '<json_payload>'
    """
    # Ensure a trigger payload was passed on the command line.
    if len(sys.argv) < 3:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        # Parse the trigger payload from CLI input.
        trigger_payload = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        raise Exception("Invalid JSON payload provided as argument") from e

    # Use the payload-specific path if present, otherwise fall back to the default input file.
    input_path = trigger_payload.get("path", "./input/projects.json")
    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "path": input_path,
    }

    try:
        # Start the crew using both the trigger payload and the resolved input path.
        return Codereviewerai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the crew with trigger: {e}"
        ) from e