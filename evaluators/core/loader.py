"""
Data loading utilities for tasks, metadata, and outputs.

This module provides functions to load task definitions, metadata configuration,
and model outputs from the file system.
"""

import json
import os
from typing import Any, Dict, List


def load_tasks(root: str) -> Dict[str, List[Dict]]:
    """
    Load all task definitions from the taskpacks directory.

    Scans the root directory for subdirectories containing tasks.json files
    and loads them into a dictionary keyed by category name.

    Args:
        root: Path to the taskpacks root directory

    Returns:
        Dictionary mapping category names to lists of task dictionaries

    Examples:
        >>> tasks = load_tasks("taskpacks")
        >>> "summarization" in tasks
        True
        >>> isinstance(tasks["summarization"], list)
        True
    """
    categories = {}

    for category in os.listdir(root):
        tasks_path = os.path.join(root, category, "tasks.json")
        if os.path.isfile(tasks_path):
            with open(tasks_path, "r") as f:
                categories[category] = json.load(f)

    return categories


def load_meta(path: str) -> Dict[str, Any]:
    """
    Load metadata configuration from YAML file.

    Loads the meta.yaml file containing category weights and other configuration.
    Falls back to default weights if the file cannot be loaded.

    Args:
        path: Path to the meta.yaml file

    Returns:
        Dictionary containing metadata configuration including category weights

    Examples:
        >>> meta = load_meta("taskpacks/meta.yaml")
        >>> "categories" in meta
        True
    """
    default_weights = {
        "summarization": 0.30,
        "reasoning": 0.30,
        "extraction": 0.20,
        "rag": 0.15,
        "safety": 0.05,
    }

    try:
        import yaml

        with open(path, "r") as f:
            meta = yaml.safe_load(f)
            return meta if meta else {"categories": default_weights}
    except Exception:
        # If YAML loading fails, return default weights
        return {"categories": default_weights}


def load_outputs(path: str) -> Dict[str, str]:
    """
    Load model outputs from JSON file.

    Loads a JSON file mapping task IDs to model-generated outputs.

    Args:
        path: Path to the outputs JSON file

    Returns:
        Dictionary mapping task IDs to output strings

    Raises:
        FileNotFoundError: If the outputs file does not exist
        json.JSONDecodeError: If the file is not valid JSON

    Examples:
        >>> outputs = load_outputs("outputs/model_outputs.json")
        >>> isinstance(outputs, dict)
        True
    """
    with open(path, "r") as f:
        return json.load(f)
