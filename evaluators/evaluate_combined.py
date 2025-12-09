#!/usr/bin/env python3
"""
Combined Evaluation: Quality + Performance
Runs both quality metrics (from evaluate.py) and performance benchmarks (from bench_ollama.py)
to provide a comprehensive model evaluation report.
"""
import argparse
import json
import os
import subprocess
import sys


def run_quality_evaluation(outputs_file: str, task_root: str, meta_file: str) -> dict:
    """Run the quality evaluation using evaluate.py"""
    temp_report = "outputs/temp_quality_report.json"
    
    cmd = [
        sys.executable,
        "evaluators/evaluate.py",
        "--outputs", outputs_file,
        "--report", temp_report,
        "--meta", meta_file,
        "--task_root", task_root,
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        with open(temp_report) as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        print(f"Quality evaluation failed: {e.stderr}")
        return {"error": "Quality evaluation failed"}
    finally:
        if os.path.exists(temp_report):
            os.remove(temp_report)


def run_performance_benchmark(
    model: str,
    task_root: str,
    epochs: int,
    max_tokens: int,
    mode: str
) -> dict:
    """Run the performance benchmark using bench_ollama.py"""
    temp_bench = "outputs/temp_bench_results.json"
    
    cmd = [
        sys.executable,
        "evaluators/bench_ollama.py",
        "--model", model,
        "--task_root", task_root,
        "--out", temp_bench,
        "--epochs", str(epochs),
        "--max-tokens", str(max_tokens),
        "--mode", mode,
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        with open(temp_bench) as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        print(f"Performance benchmark failed: {e.stderr}")
        return {"error": "Performance benchmark failed"}
    finally:
        if os.path.exists(temp_bench):
            os.remove(temp_bench)


def check_latency_targets(perf_metrics: dict, targets: dict) -> dict:
    """
    Check if performance meets latency targets from meta.yaml
    """
    results = {}
    
    # Check tokens per second minimum
    if "tok_per_sec_min" in targets:
        min_tps = targets["tok_per_sec_min"]
        actual_tps = perf_metrics.get("avg_generate_tokens_per_sec", 0)
        results["tokens_per_sec"] = {
            "target": min_tps,
            "actual": actual_tps,
            "meets_target": actual_tps >= min_tps,
        }
    
    # Check time to first token (using prefill as proxy)
    if "ttft_ms_p95" in targets:
        target_ttft = targets["ttft_ms_p95"]
        # Estimate TTFT from prefill speed (rough approximation)
        prefill_tps = perf_metrics.get("avg_prefill_tokens_per_sec", 0)
        # Assume ~50 token prompt
        estimated_ttft = (50 / prefill_tps * 1000) if prefill_tps > 0 else float('inf')
        results["ttft_ms"] = {
            "target": target_ttft,
            "estimated": estimated_ttft,
            "meets_target": estimated_ttft <= target_ttft,
        }
    
    return results


def calculate_composite_score(quality_score: float, perf_metrics: dict, targets: dict) -> dict:
    """
    Calculate a composite score that combines quality and performance.
    Quality is weighted 70%, performance 30%.
    """
    quality_weight = 0.7
    perf_weight = 0.3
    
    # Performance score based on meeting targets
    perf_score = 0.0
    perf_checks = check_latency_targets(perf_metrics, targets)
    
    if perf_checks:
        met_targets = sum(1 for check in perf_checks.values() if check.get("meets_target", False))
        perf_score = met_targets / len(perf_checks)
    
    composite = quality_weight * quality_score + perf_weight * perf_score
    
    return {
        "composite_score": composite,
        "quality_score": quality_score,
        "quality_weight": quality_weight,
        "performance_score": perf_score,
        "performance_weight": perf_weight,
        "performance_checks": perf_checks,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Combined quality and performance evaluation for Ollama models"
    )
    ap.add_argument("--model", required=True, help="Ollama model name")
    ap.add_argument("--outputs", required=True, help="Path to outputs.json from query run")
    ap.add_argument("--report", default="outputs/combined_report.json", help="Output report file")
    ap.add_argument("--task_root", default="taskpacks", help="Path to taskpacks")
    ap.add_argument("--meta", default="taskpacks/meta.yaml", help="Path to meta.yaml")
    ap.add_argument("--bench-epochs", type=int, default=3, help="Benchmark epochs")
    ap.add_argument("--bench-max-tokens", type=int, default=100, help="Benchmark max tokens")
    ap.add_argument(
        "--bench-mode",
        choices=["category", "all"],
        default="category",
        help="Benchmark mode"
    )
    ap.add_argument("--skip-bench", action="store_true", help="Skip performance benchmarking")
    args = ap.parse_args()
    
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    
    print("="*60)
    print("COMBINED EVALUATION: Quality + Performance")
    print("="*60)
    print(f"Model: {args.model}\n")
    
    # Run quality evaluation
    print("Step 1/2: Running quality evaluation...")
    quality_results = run_quality_evaluation(args.outputs, args.task_root, args.meta)
    
    if "error" in quality_results:
        print(f"Error: {quality_results['error']}")
        sys.exit(1)
    
    print(f"✓ Quality Score: {quality_results['overall']:.3f}\n")
    
    # Run performance benchmark
    perf_results = {}
    if not args.skip_bench:
        print("Step 2/2: Running performance benchmark...")
        perf_results = run_performance_benchmark(
            model=args.model,
            task_root=args.task_root,
            epochs=args.bench_epochs,
            max_tokens=args.bench_max_tokens,
            mode=args.bench_mode,
        )
        
        if "error" in perf_results:
            print(f"Warning: {perf_results['error']}")
        else:
            agg = perf_results.get("aggregated_metrics", {})
            print(f"✓ Avg Generate Speed: {agg.get('avg_generate_tokens_per_sec', 0):.2f} tok/s\n")
    else:
        print("Step 2/2: Skipped (--skip-bench)\n")
    
    # Load latency targets
    targets = {}
    try:
        import yaml
        with open(args.meta) as f:
            meta = yaml.safe_load(f)
            targets = meta.get("latency_targets", {})
    except Exception:
        pass
    
    # Calculate composite score
    perf_metrics = perf_results.get("aggregated_metrics", {})
    composite = calculate_composite_score(
        quality_results["overall"],
        perf_metrics,
        targets
    )
    
    # Build final report
    report = {
        "model": args.model,
        "composite_score": composite["composite_score"],
        "quality": {
            "overall_score": quality_results["overall"],
            "by_category": quality_results.get("by_category", {}),
            "weights": quality_results.get("weights", {}),
        },
        "performance": {
            "aggregated_metrics": perf_metrics,
            "latency_targets": targets,
            "performance_checks": composite.get("performance_checks", {}),
        },
        "scoring_breakdown": composite,
    }
    
    # Add detailed bench results if available
    if "detailed_results" in perf_results:
        report["performance"]["detailed_results"] = perf_results["detailed_results"]
    
    with open(args.report, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Composite Score: {composite['composite_score']:.3f}")
    print(f"  Quality ({composite['quality_weight']*100:.0f}%): {composite['quality_score']:.3f}")
    print(f"  Performance ({composite['performance_weight']*100:.0f}%): {composite['performance_score']:.3f}")
    print()
    
    if composite.get("performance_checks"):
        print("Performance Targets:")
        for metric, check in composite["performance_checks"].items():
            status = "✓" if check["meets_target"] else "✗"
            print(f"  {status} {metric}: {check.get('actual', check.get('estimated', 0)):.2f} "
                  f"(target: {check['target']})")
    
    print(f"\nFull report saved to: {args.report}")


if __name__ == "__main__":
    main()
