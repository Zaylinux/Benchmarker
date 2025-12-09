"""
Benchmarking module for performance testing.

This module provides tools for running performance benchmarks using Ollama's
bench tool and aggregating the results.
"""

from evaluators.benchmarking.bench_runner import BenchRunner
from evaluators.benchmarking.aggregator import aggregate_metrics

__all__ = ["BenchRunner", "aggregate_metrics"]
