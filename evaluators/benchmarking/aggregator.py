"""
Metrics aggregation for benchmark results.

This module provides functions for aggregating performance metrics across
multiple benchmark runs to compute average performance statistics.
"""

from typing import Any, Dict, List


def aggregate_metrics(bench_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate performance metrics across all benchmarks.
    
    Computes average prefill speed, generation speed, and load times
    across all successful benchmark runs.
    
    Args:
        bench_results: Dictionary mapping benchmark IDs to result dictionaries.
                      Each result should have the structure:
                      {
                          "success": bool,
                          "metrics": {
                              "prefill": {"tokens_per_sec": float, ...},
                              "generate": {"tokens_per_sec": float, ...},
                              "load": {"ns_per_token": float, ...}
                          }
                      }
    
    Returns:
        Dictionary containing aggregated metrics:
            - avg_prefill_tokens_per_sec: Average prefill speed in tokens/sec
            - avg_generate_tokens_per_sec: Average generation speed in tokens/sec
            - avg_load_time_ms: Average model load time in milliseconds
            - sample_count: Number of successful benchmarks included
    
    Example:
        >>> results = {
        ...     "task1": {
        ...         "success": True,
        ...         "metrics": {
        ...             "prefill": {"tokens_per_sec": 100.0},
        ...             "generate": {"tokens_per_sec": 50.0},
        ...             "load": {"ns_per_token": 1000000.0}
        ...         }
        ...     }
        ... }
        >>> aggregate_metrics(results)
        {
            'avg_prefill_tokens_per_sec': 100.0,
            'avg_generate_tokens_per_sec': 50.0,
            'avg_load_time_ms': 1.0,
            'sample_count': 1
        }
    """
    all_prefill_tps: List[float] = []
    all_generate_tps: List[float] = []
    all_load_times: List[float] = []
    
    for result in bench_results.values():
        if not result.get("success"):
            continue
        
        metrics = result.get("metrics", {})
        
        if "prefill" in metrics and metrics["prefill"].get("tokens_per_sec"):
            all_prefill_tps.append(metrics["prefill"]["tokens_per_sec"])
        
        if "generate" in metrics and metrics["generate"].get("tokens_per_sec"):
            all_generate_tps.append(metrics["generate"]["tokens_per_sec"])
        
        if "load" in metrics:
            # Convert nanoseconds to milliseconds
            load_ms = metrics["load"]["ns_per_token"] / 1_000_000
            all_load_times.append(load_ms)
    
    def avg(lst: List[float]) -> float:
        """Calculate average of a list, returning 0.0 for empty lists."""
        return sum(lst) / len(lst) if lst else 0.0
    
    return {
        "avg_prefill_tokens_per_sec": avg(all_prefill_tps),
        "avg_generate_tokens_per_sec": avg(all_generate_tps),
        "avg_load_time_ms": avg(all_load_times),
        "sample_count": len(bench_results),
    }
