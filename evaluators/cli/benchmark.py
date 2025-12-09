#!/usr/bin/env python3
"""
Benchmarking CLI for running performance tests using Ollama's bench tool.

This script runs performance benchmarks on Ollama models and generates
detailed performance reports including token generation speed and load times.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from evaluators.benchmarking import BenchRunner, aggregate_metrics


def load_all_tasks(task_root: str) -> List[Dict[str, Any]]:
    """
    Load all tasks from taskpacks directory.

    Args:
        task_root: Path to the taskpacks root directory

    Returns:
        List of all tasks with category information added

    Examples:
        >>> tasks = load_all_tasks("taskpacks")
        >>> all("_category" in task for task in tasks)
        True
    """
    tasks = []
    for cat in os.listdir(task_root):
        tasks_file = os.path.join(task_root, cat, "tasks.json")
        if os.path.isfile(tasks_file):
            with open(tasks_file, "r") as f:
                items = json.load(f)
            for item in items:
                item["_category"] = cat
            tasks.extend(items)
    return tasks


def benchmark_per_category(
    model: str,
    task_root: str,
    epochs: int = 3,
    max_tokens: int = 100,
    bench_path: str = None,
) -> Dict[str, Any]:
    """
    Run benchmarks for each task category using representative prompts.

    Uses the first task in each category as a representative sample for benchmarking.

    Args:
        model: Ollama model name
        task_root: Path to taskpacks directory
        epochs: Number of benchmark iterations
        max_tokens: Maximum tokens to generate
        bench_path: Optional path to bench tool

    Returns:
        Dictionary mapping category names to benchmark results
    """
    tasks = load_all_tasks(task_root)

    # Group by category
    by_category = {}
    for task in tasks:
        cat = task.get("_category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(task)

    results = {}
    runner = BenchRunner(bench_path=bench_path)

    for cat, cat_tasks in by_category.items():
        # Use first task as representative prompt
        if not cat_tasks:
            continue

        sample_task = cat_tasks[0]
        prompt = sample_task.get("input", "Write a short response.")

        # Add context for RAG tasks
        if cat == "rag" and "context" in sample_task:
            prompt = f"Context: {sample_task['context']}\n\nQuestion: {prompt}"

        print(f"Benchmarking {cat} with {len(cat_tasks)} tasks...")
        bench_result = runner.run_benchmark(
            model=model,
            prompt=prompt,
            epochs=epochs,
            max_tokens=max_tokens,
        )

        results[cat] = bench_result

    return results


def benchmark_all_tasks(
    model: str,
    task_root: str,
    epochs: int = 1,
    max_tokens: int = 100,
    bench_path: str = None,
) -> Dict[str, Any]:
    """
    Run benchmarks for every individual task.

    Warning: This can be slow for large taskpacks.

    Args:
        model: Ollama model name
        task_root: Path to taskpacks directory
        epochs: Number of benchmark iterations
        max_tokens: Maximum tokens to generate
        bench_path: Optional path to bench tool

    Returns:
        Dictionary mapping task IDs to benchmark results
    """
    tasks = load_all_tasks(task_root)
    results = {}
    runner = BenchRunner(bench_path=bench_path)

    for i, task in enumerate(tasks, 1):
        task_id = task.get("id", f"task_{i}")
        prompt = task.get("input", "")

        # Add context for RAG tasks
        if task.get("_category") == "rag" and "context" in task:
            prompt = f"Context: {task['context']}\n\nQuestion: {prompt}"

        print(f"[{i}/{len(tasks)}] Benchmarking {task_id}...")
        bench_result = runner.run_benchmark(
            model=model,
            prompt=prompt,
            epochs=epochs,
            max_tokens=max_tokens,
        )

        results[task_id] = bench_result

    return results


def main() -> None:
    """
    Main entry point for the benchmarking CLI.

    Parses command-line arguments, runs benchmarks, and generates performance reports.
    """
    parser = argparse.ArgumentParser(
        description="Run Ollama bench tool on taskpack and generate performance report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark per category (fast)
  %(prog)s --model llama3.2 --out outputs/bench_results.json

  # Benchmark all tasks (slow but detailed)
  %(prog)s --model llama3.2 --mode all --out outputs/bench_all.json

  # Custom epochs and token limit
  %(prog)s --model mistral --epochs 5 --max-tokens 200
        """,
    )

    parser.add_argument("--model", required=True, help="Ollama model name")
    parser.add_argument(
        "--task_root",
        default="taskpacks",
        help="Path to taskpacks directory (default: taskpacks)",
    )
    parser.add_argument(
        "--out",
        default="outputs/bench_results.json",
        help="Output JSON file (default: outputs/bench_results.json)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of benchmark iterations (default: 3)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=100,
        help="Max tokens to generate (default: 100)",
    )
    parser.add_argument(
        "--mode",
        choices=["category", "all"],
        default="category",
        help="Benchmark per category (fast) or all tasks (slow) (default: category)",
    )
    parser.add_argument(
        "--bench-path",
        help="Path to bench.go or pre-built ollama-bench binary (auto-detected if not specified)",
    )

    args = parser.parse_args()

    try:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

        print(f"Running Ollama bench for model: {args.model}")
        print(f"Mode: {args.mode}, Epochs: {args.epochs}, Max tokens: {args.max_tokens}\n")

        if args.mode == "category":
            bench_results = benchmark_per_category(
                model=args.model,
                task_root=args.task_root,
                epochs=args.epochs,
                max_tokens=args.max_tokens,
                bench_path=args.bench_path,
            )
        else:
            bench_results = benchmark_all_tasks(
                model=args.model,
                task_root=args.task_root,
                epochs=args.epochs,
                max_tokens=args.max_tokens,
                bench_path=args.bench_path,
            )

        aggregated = aggregate_metrics(bench_results)

        report = {
            "model": args.model,
            "mode": args.mode,
            "epochs": args.epochs,
            "max_tokens": args.max_tokens,
            "aggregated_metrics": aggregated,
            "detailed_results": bench_results,
        }

        with open(args.out, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*60}")
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Model: {args.model}")
        print(
            f"Avg Prefill Speed: {aggregated['avg_prefill_tokens_per_sec']:.2f} tokens/sec"
        )
        print(
            f"Avg Generate Speed: {aggregated['avg_generate_tokens_per_sec']:.2f} tokens/sec"
        )
        print(f"Avg Load Time: {aggregated['avg_load_time_ms']:.2f} ms")
        print(f"\nFull report saved to: {args.out}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
