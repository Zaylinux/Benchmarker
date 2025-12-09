#!/usr/bin/env python3
"""
Multi-model comparison CLI for evaluating and comparing multiple models.

This script runs full evaluation pipelines on multiple models and generates
comparison reports in both JSON and Markdown formats.
"""

import argparse
import os
import subprocess
import sys
from typing import Any, Dict

from evaluators.reporting import JSONReporter, MarkdownReporter


def run_model_evaluation(
    model: str,
    task_root: str,
    meta: str,
    bench_epochs: int,
    bench_max_tokens: int,
    bench_mode: str,
) -> Dict[str, Any]:
    """
    Run full evaluation pipeline for a single model.

    Executes both quality evaluation and performance benchmarking for the specified model.

    Args:
        model: Ollama model name
        task_root: Path to taskpacks directory
        meta: Path to meta.yaml file
        bench_epochs: Number of benchmark iterations
        bench_max_tokens: Maximum tokens for benchmarking
        bench_mode: Benchmark mode ('category' or 'all')

    Returns:
        Dictionary containing evaluation results or error information
    """
    print(f"\n{'='*60}")
    print(f"Evaluating: {model}")
    print("=" * 60)

    outputs_file = f"outputs/{model.replace(':', '_')}_outputs.json"
    report_file = f"outputs/{model.replace(':', '_')}_report.json"

    # Step 1: Query the model
    print("Step 1: Querying model...")
    query_cmd = [
        sys.executable,
        "evaluators/query_ollama.py",
        "--model",
        model,
        "--task_root",
        task_root,
        "--out",
        outputs_file,
    ]

    try:
        subprocess.run(query_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to query model: {e.stderr}", file=sys.stderr)
        return {"model": model, "error": "Query failed"}

    # Step 2: Run combined evaluation
    print("Step 2: Running combined evaluation...")
    eval_cmd = [
        sys.executable,
        "evaluators/evaluate_combined.py",
        "--model",
        model,
        "--outputs",
        outputs_file,
        "--report",
        report_file,
        "--task_root",
        task_root,
        "--meta",
        meta,
        "--bench-epochs",
        str(bench_epochs),
        "--bench-max-tokens",
        str(bench_max_tokens),
        "--bench-mode",
        bench_mode,
    ]

    try:
        subprocess.run(eval_cmd, check=True, capture_output=True, text=True)
        # Use JSONReporter to load the report
        json_reporter = JSONReporter()
        return json_reporter.load_report(report_file)
    except subprocess.CalledProcessError as e:
        print(f"Failed to evaluate: {e.stderr}", file=sys.stderr)
        return {"model": model, "error": "Evaluation failed"}


def main() -> None:
    """
    Main entry point for the model comparison CLI.

    Parses command-line arguments, runs evaluations on multiple models,
    and generates comparison reports.
    """
    parser = argparse.ArgumentParser(
        description="Compare multiple Ollama models with combined quality + performance evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two models
  %(prog)s --models llama3.2,mistral

  # Compare with custom settings
  %(prog)s --models llama3.2,mistral,qwen2.5 --bench-epochs 5 --bench-mode all

  # Custom output locations
  %(prog)s --models llama3.2,mistral --out results.json --markdown results.md
        """,
    )

    parser.add_argument(
        "--models",
        required=True,
        help="Comma-separated list of model names (e.g., 'llama3.2,mistral,qwen2.5')",
    )
    parser.add_argument(
        "--task_root",
        default="taskpacks",
        help="Path to taskpacks directory (default: taskpacks)",
    )
    parser.add_argument(
        "--meta",
        default="taskpacks/meta.yaml",
        help="Path to meta.yaml (default: taskpacks/meta.yaml)",
    )
    parser.add_argument(
        "--out",
        default="outputs/comparison.json",
        help="Output JSON file (default: outputs/comparison.json)",
    )
    parser.add_argument(
        "--markdown",
        default="outputs/comparison.md",
        help="Output markdown file (default: outputs/comparison.md)",
    )
    parser.add_argument(
        "--bench-epochs",
        type=int,
        default=3,
        help="Benchmark epochs (default: 3)",
    )
    parser.add_argument(
        "--bench-max-tokens",
        type=int,
        default=100,
        help="Benchmark max tokens (default: 100)",
    )
    parser.add_argument(
        "--bench-mode",
        choices=["category", "all"],
        default="category",
        help="Benchmark mode (default: category)",
    )

    args = parser.parse_args()

    try:
        os.makedirs("outputs", exist_ok=True)

        models = [m.strip() for m in args.models.split(",")]

        print(f"Comparing {len(models)} models: {', '.join(models)}")

        results = []
        for model in models:
            result = run_model_evaluation(
                model=model,
                task_root=args.task_root,
                meta=args.meta,
                bench_epochs=args.bench_epochs,
                bench_max_tokens=args.bench_max_tokens,
                bench_mode=args.bench_mode,
            )
            results.append(result)

        # Save JSON report using JSONReporter
        json_reporter = JSONReporter()
        json_reporter.generate_report(results, args.out)

        # Generate markdown report using MarkdownReporter
        markdown_reporter = MarkdownReporter()
        markdown_reporter.generate_report(results, args.markdown)
        markdown = markdown_reporter.generate_comparison_table(results)

        print(f"\n{'='*60}")
        print("COMPARISON COMPLETE")
        print("=" * 60)
        print(f"JSON report: {args.out}")
        print(f"Markdown report: {args.markdown}")
        print(f"\n{markdown}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
