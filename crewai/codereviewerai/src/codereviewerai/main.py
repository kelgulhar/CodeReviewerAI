#!/usr/bin/env python
import json
import sys
import warnings

from codereviewerai.crew import Codereviewerai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew locally with the default projects.json input.
    """
    inputs = {
        "path": "./input/projects.json",
    }

    try:
        Codereviewerai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}") from e


def train():
    """
    Train the crew for a given number of iterations.
    Usage:
        python -m codereviewerai.main train <n_iterations> <filename> [path]
    """
    if len(sys.argv) < 4:
        raise Exception(
            "Usage: train <n_iterations> <filename> [path_to_projects_json]"
        )

    input_path = sys.argv[4] if len(sys.argv) > 4 else "./input/projects.json"
    inputs = {
        "path": input_path,
    }

    try:
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
    if len(sys.argv) < 3:
        raise Exception("Usage: replay <task_id>")

    try:
        Codereviewerai().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e


def test():
    """
    Test the crew execution and return the results.
    Usage:
        python -m codereviewerai.main test <n_iterations> <eval_llm> [path]
    """
    if len(sys.argv) < 4:
        raise Exception(
            "Usage: test <n_iterations> <eval_llm> [path_to_projects_json]"
        )

    input_path = sys.argv[4] if len(sys.argv) > 4 else "./input/projects.json"
    inputs = {
        "path": input_path,
    }

    try:
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
    if len(sys.argv) < 3:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        raise Exception("Invalid JSON payload provided as argument") from e

    input_path = trigger_payload.get("path", "./input/projects.json")
    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "path": input_path,
    }

    try:
        return Codereviewerai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(
            f"An error occurred while running the crew with trigger: {e}"
        ) from e