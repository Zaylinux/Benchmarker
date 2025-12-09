"""
Bench runner for executing Ollama performance benchmarks.

This module provides the BenchRunner class for finding and executing the
Ollama bench tool, which measures model performance metrics like tokens/sec
and load times.
"""

import os
import subprocess
from typing import Any, Dict, Optional, Tuple


class BenchRunner:
    """
    Manages execution of Ollama bench tool for performance benchmarking.
    
    The bench tool can be used in two ways:
    1. Pre-built binary: ./ollama-bench (if built with 'go build')
    2. Go run: go run bench.go (no build required)
    """
    
    def __init__(self, bench_path: Optional[str] = None):
        """
        Initialize the BenchRunner.
        
        Args:
            bench_path: Optional path to bench.go or pre-built binary.
                       If not provided, will auto-detect.
        """
        self.bench_path = bench_path
        self.cmd_type = None
        
        if bench_path:
            self.cmd_type = "go_run" if bench_path.endswith(".go") else "binary"
    
    def find_bench_script(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the bench script in common locations.
        
        Returns:
            Tuple of (command_type, path) where command_type is either
            "binary" or "go_run", or (None, None) if not found.
            
        Priority:
            1. Pre-built binary (./ollama-bench)
            2. bench.go in current directory
            3. bench.go in bench/ subdirectory
        """
        # Check for pre-built binary
        if os.path.exists("ollama-bench"):
            return ("binary", "./ollama-bench")
        
        # Check for bench.go in current directory
        if os.path.exists("bench.go"):
            return ("go_run", "bench.go")
        
        # Check in bench/ subdirectory
        if os.path.exists("bench/bench.go"):
            return ("go_run", "bench/bench.go")
        
        return (None, None)
    
    def run_benchmark(
        self,
        model: str,
        prompt: str,
        epochs: int = 3,
        max_tokens: int = 0,
        temperature: float = 0.0,
        seed: int = 0,
        timeout: int = 300,
        image: Optional[str] = None,
        output_format: str = "csv",
    ) -> Dict[str, Any]:
        """
        Run ollama bench tool and parse the output.
        
        Args:
            model: Name of the Ollama model to benchmark
            prompt: Input prompt for the model
            epochs: Number of benchmark iterations (default: 3)
            max_tokens: Maximum tokens to generate (default: 0 for unlimited)
            temperature: Sampling temperature (default: 0.0)
            seed: Random seed for reproducibility (default: 0)
            timeout: Timeout in seconds (default: 300)
            image: Optional path to image for vision models
            output_format: Output format - "csv", "benchstat", or "markdown"
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if benchmark succeeded
                - metrics: Dict of performance metrics by step (prefill, generate, load)
                - raw_output: Raw stdout from bench tool
                - error: Error message if success is False
        """
        # Find bench script if not already set
        if not self.bench_path:
            self.cmd_type, self.bench_path = self.find_bench_script()
            if not self.bench_path:
                return {
                    "success": False,
                    "error": "Bench script not found. Please download bench.go from "
                             "https://github.com/ollama/ollama/blob/main/cmd/bench/bench.go"
                }
        
        # Build command based on type
        if self.cmd_type == "go_run":
            cmd = ["go", "run", self.bench_path]
        else:
            cmd = [self.bench_path]
        
        # Add bench arguments
        cmd.extend([
            "-model", model,
            "-epochs", str(epochs),
            "-max-tokens", str(max_tokens),
            "-temperature", str(temperature),
            "-seed", str(seed),
            "-timeout", str(timeout),
            "-format", output_format,
            "-p", prompt,
        ])
        
        if image:
            cmd.extend(["-image", image])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10,
                check=True
            )
            
            # Parse CSV output
            lines = result.stdout.strip().split('\n')
            metrics = {}
            
            for line in lines[1:]:  # Skip header
                if not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) >= 5:
                    name, step, count, ns_per_count, token_per_sec = parts[:5]
                    metrics[step] = {
                        "count": int(count),
                        "ns_per_token": float(ns_per_count),
                        "tokens_per_sec": float(token_per_sec) if token_per_sec != "0" else None,
                    }
            
            return {
                "success": True,
                "metrics": metrics,
                "raw_output": result.stdout
            }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Benchmark timeout"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Bench command failed: {e.stderr}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def find_bench_script() -> Tuple[Optional[str], Optional[str]]:
    """
    Find the bench script. Returns (command_type, path).
    
    This is a convenience function that creates a BenchRunner instance
    and calls its find_bench_script method.
    
    Returns:
        Tuple of (command_type, path) where command_type is either
        "binary" or "go_run", or (None, None) if not found.
        
    Priority:
        1. Pre-built binary (./ollama-bench)
        2. bench.go in current directory  
        3. bench.go in bench/ subdirectory
    """
    runner = BenchRunner()
    return runner.find_bench_script()


def run_ollama_bench(
    model: str,
    prompt: str,
    epochs: int = 3,
    max_tokens: int = 0,
    temperature: float = 0.0,
    seed: int = 0,
    timeout: int = 300,
    image: Optional[str] = None,
    bench_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run ollama bench Go script and parse the output.
    
    This is a convenience function that creates a BenchRunner instance
    and calls its run_benchmark method.
    
    Args:
        model: Name of the Ollama model to benchmark
        prompt: Input prompt for the model
        epochs: Number of benchmark iterations (default: 3)
        max_tokens: Maximum tokens to generate (default: 0 for unlimited)
        temperature: Sampling temperature (default: 0.0)
        seed: Random seed for reproducibility (default: 0)
        timeout: Timeout in seconds (default: 300)
        image: Optional path to image for vision models
        bench_path: Optional path to bench.go or pre-built binary
    
    Returns:
        Dictionary containing performance metrics: prefill, generate, load
        durations and tokens/sec.
    """
    runner = BenchRunner(bench_path=bench_path)
    return runner.run_benchmark(
        model=model,
        prompt=prompt,
        epochs=epochs,
        max_tokens=max_tokens,
        temperature=temperature,
        seed=seed,
        timeout=timeout,
        image=image,
    )
