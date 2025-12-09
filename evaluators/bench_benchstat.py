#!/usr/bin/env python3
"""
Ollama Bench - Benchstat Format
Runs benchmarks in benchstat format for use with Go's benchstat tool.
"""
import argparse
import subprocess
import sys

from evaluators.benchmarking import BenchRunner


def find_bench_script():
    """
    Find the bench script.
    
    Deprecated: Use evaluators.benchmarking.BenchRunner instead.
    """
    runner = BenchRunner()
    return runner.find_bench_script()


def run_benchstat(
    models: str,
    epochs: int = 6,
    max_tokens: int = 100,
    prompt: str = None,
    output_file: str = None,
    bench_path: str = None,
):
    """Run bench in benchstat format."""
    
    # Find bench script
    if not bench_path:
        cmd_type, bench_path = find_bench_script()
        if not bench_path:
            print("Error: Bench script not found")
            print("Run: ./setup_bench.sh")
            sys.exit(1)
    else:
        cmd_type = "go_run" if bench_path.endswith(".go") else "binary"
    
    # Build command
    if cmd_type == "go_run":
        cmd = ["go", "run", bench_path]
    else:
        cmd = [bench_path]
    
    # Add arguments
    cmd.extend([
        "-model", models,
        "-epochs", str(epochs),
        "-max-tokens", str(max_tokens),
        "-format", "benchstat",
    ])
    
    if prompt:
        cmd.extend(["-p", prompt])
    
    if output_file:
        cmd.extend(["-output", output_file])
    
    # Run command
    try:
        result = subprocess.run(cmd, check=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running bench: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(
        description="Run Ollama bench in benchstat format for statistical analysis"
    )
    ap.add_argument(
        "--models",
        required=True,
        help="Comma-separated list of models (e.g., 'qwen2.5,llama3.2')"
    )
    ap.add_argument("--epochs", type=int, default=6, help="Number of iterations")
    ap.add_argument("--max-tokens", type=int, default=100, help="Max tokens to generate")
    ap.add_argument("--prompt", help="Custom prompt (optional)")
    ap.add_argument("--output", help="Output file (optional, prints to stdout if not specified)")
    ap.add_argument("--bench-path", help="Path to bench.go or ollama-bench binary")
    args = ap.parse_args()
    
    print(f"Running benchstat for models: {args.models}")
    print(f"Epochs: {args.epochs}, Max tokens: {args.max_tokens}")
    if args.output:
        print(f"Output: {args.output}")
    print()
    
    success = run_benchstat(
        models=args.models,
        epochs=args.epochs,
        max_tokens=args.max_tokens,
        prompt=args.prompt,
        output_file=args.output,
        bench_path=args.bench_path,
    )
    
    if success and args.output:
        print()
        print("="*60)
        print("Benchstat output saved!")
        print("="*60)
        print(f"File: {args.output}")
        print()
        print("To analyze with benchstat:")
        print(f"  benchstat {args.output}")
        print()
        print("To compare two runs:")
        print(f"  benchstat old.bench {args.output}")
        print()
        print("Install benchstat:")
        print("  go install golang.org/x/perf/cmd/benchstat@latest")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
