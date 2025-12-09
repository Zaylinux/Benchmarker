#!/usr/bin/env python3
"""
Main evaluation CLI for scoring model outputs against taskpacks.

This script evaluates model outputs by comparing them against expected outputs
in the taskpack using category-specific scoring metrics.
"""

import argparse
import json
import sys

from evaluators.core.evaluator import Evaluator
from evaluators.core.loader import load_tasks, load_meta, load_outputs


def main() -> None:
    """
    Main entry point for the evaluation CLI.

    Parses command-line arguments, loads tasks and outputs, runs evaluation,
    and generates a JSON report with overall and per-category scores.
    """
    parser = argparse.ArgumentParser(
        description="Evaluate model outputs against taskpack expected outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic evaluation
  %(prog)s --outputs outputs/model_outputs.json --report outputs/report.json

  # Custom taskpack location
  %(prog)s --outputs outputs.json --report report.json --task_root custom_tasks/

  # Custom weights file
  %(prog)s --outputs outputs.json --report report.json --meta custom_meta.yaml
        """,
    )

    parser.add_argument(
        "--outputs",
        required=True,
        help="Path to outputs.json mapping task id -> model output",
    )
    parser.add_argument(
        "--report", required=True, help="Path where the evaluation report JSON will be written"
    )
    parser.add_argument(
        "--meta",
        default="taskpacks/meta.yaml",
        help="Path to meta.yaml containing category weights (default: taskpacks/meta.yaml)",
    )
    parser.add_argument(
        "--task_root",
        default="taskpacks",
        help="Path to taskpacks root directory (default: taskpacks)",
    )

    args = parser.parse_args()

    try:
        # Load metadata and extract weights
        meta = load_meta(args.meta)
        weights = meta.get("categories", {})

        # Load model outputs
        outputs = load_outputs(args.outputs)

        # Load tasks from taskpacks
        tasks = load_tasks(args.task_root)

        # Run evaluation
        evaluator = Evaluator(tasks, weights)
        report = evaluator.evaluate(outputs)

        # Write report to file
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)

        # Print report to stdout
        print(json.dumps(report, indent=2))

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
