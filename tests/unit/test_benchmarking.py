"""
Unit tests for benchmarking module.

Tests the refactored benchmarking code to ensure it works correctly.
"""
import unittest
from unittest.mock import patch

from evaluators.benchmarking import BenchRunner, aggregate_metrics


class TestBenchRunner(unittest.TestCase):
    """Test cases for BenchRunner class."""
    
    def test_init_with_path(self):
        """Test BenchRunner initialization with a path."""
        runner = BenchRunner(bench_path="bench.go")
        self.assertEqual(runner.bench_path, "bench.go")
        self.assertEqual(runner.cmd_type, "go_run")
    
    def test_init_with_binary(self):
        """Test BenchRunner initialization with a binary path."""
        runner = BenchRunner(bench_path="./ollama-bench")
        self.assertEqual(runner.bench_path, "./ollama-bench")
        self.assertEqual(runner.cmd_type, "binary")
    
    def test_init_without_path(self):
        """Test BenchRunner initialization without a path."""
        runner = BenchRunner()
        self.assertIsNone(runner.bench_path)
        self.assertIsNone(runner.cmd_type)
    
    @patch('os.path.exists')
    def test_find_bench_script_binary(self, mock_exists):
        """Test finding pre-built binary."""
        mock_exists.side_effect = lambda path: path == "ollama-bench"
        runner = BenchRunner()
        cmd_type, path = runner.find_bench_script()
        self.assertEqual(cmd_type, "binary")
        self.assertEqual(path, "./ollama-bench")
    
    @patch('os.path.exists')
    def test_find_bench_script_go_current(self, mock_exists):
        """Test finding bench.go in current directory."""
        mock_exists.side_effect = lambda path: path == "bench.go"
        runner = BenchRunner()
        cmd_type, path = runner.find_bench_script()
        self.assertEqual(cmd_type, "go_run")
        self.assertEqual(path, "bench.go")
    
    @patch('os.path.exists')
    def test_find_bench_script_not_found(self, mock_exists):
        """Test when bench script is not found."""
        mock_exists.return_value = False
        runner = BenchRunner()
        cmd_type, path = runner.find_bench_script()
        self.assertIsNone(cmd_type)
        self.assertIsNone(path)


class TestAggregateMetrics(unittest.TestCase):
    """Test cases for aggregate_metrics function."""
    
    def test_aggregate_empty_results(self):
        """Test aggregation with empty results."""
        result = aggregate_metrics({})
        self.assertEqual(result["avg_prefill_tokens_per_sec"], 0.0)
        self.assertEqual(result["avg_generate_tokens_per_sec"], 0.0)
        self.assertEqual(result["avg_load_time_ms"], 0.0)
        self.assertEqual(result["sample_count"], 0)
    
    def test_aggregate_single_result(self):
        """Test aggregation with a single successful result."""
        bench_results = {
            "task1": {
                "success": True,
                "metrics": {
                    "prefill": {"tokens_per_sec": 100.0},
                    "generate": {"tokens_per_sec": 50.0},
                    "load": {"ns_per_token": 1_000_000.0}
                }
            }
        }
        result = aggregate_metrics(bench_results)
        self.assertEqual(result["avg_prefill_tokens_per_sec"], 100.0)
        self.assertEqual(result["avg_generate_tokens_per_sec"], 50.0)
        self.assertEqual(result["avg_load_time_ms"], 1.0)
        self.assertEqual(result["sample_count"], 1)
    
    def test_aggregate_multiple_results(self):
        """Test aggregation with multiple successful results."""
        bench_results = {
            "task1": {
                "success": True,
                "metrics": {
                    "prefill": {"tokens_per_sec": 100.0},
                    "generate": {"tokens_per_sec": 50.0},
                    "load": {"ns_per_token": 1_000_000.0}
                }
            },
            "task2": {
                "success": True,
                "metrics": {
                    "prefill": {"tokens_per_sec": 200.0},
                    "generate": {"tokens_per_sec": 100.0},
                    "load": {"ns_per_token": 2_000_000.0}
                }
            }
        }
        result = aggregate_metrics(bench_results)
        self.assertEqual(result["avg_prefill_tokens_per_sec"], 150.0)
        self.assertEqual(result["avg_generate_tokens_per_sec"], 75.0)
        self.assertEqual(result["avg_load_time_ms"], 1.5)
        self.assertEqual(result["sample_count"], 2)
    
    def test_aggregate_with_failed_results(self):
        """Test aggregation ignores failed results."""
        bench_results = {
            "task1": {
                "success": True,
                "metrics": {
                    "prefill": {"tokens_per_sec": 100.0},
                    "generate": {"tokens_per_sec": 50.0},
                    "load": {"ns_per_token": 1_000_000.0}
                }
            },
            "task2": {
                "success": False,
                "error": "Benchmark failed"
            }
        }
        result = aggregate_metrics(bench_results)
        self.assertEqual(result["avg_prefill_tokens_per_sec"], 100.0)
        self.assertEqual(result["avg_generate_tokens_per_sec"], 50.0)
        self.assertEqual(result["avg_load_time_ms"], 1.0)
        self.assertEqual(result["sample_count"], 2)
    
    def test_aggregate_with_missing_metrics(self):
        """Test aggregation with missing metrics."""
        bench_results = {
            "task1": {
                "success": True,
                "metrics": {
                    "prefill": {"tokens_per_sec": 100.0}
                    # Missing generate and load
                }
            }
        }
        result = aggregate_metrics(bench_results)
        self.assertEqual(result["avg_prefill_tokens_per_sec"], 100.0)
        self.assertEqual(result["avg_generate_tokens_per_sec"], 0.0)
        self.assertEqual(result["avg_load_time_ms"], 0.0)
        self.assertEqual(result["sample_count"], 1)


if __name__ == "__main__":
    unittest.main()
