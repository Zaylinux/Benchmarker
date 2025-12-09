# Ollama Bench Integration Guide

This document explains the integration of Ollama's bench tool (v13.0+) into the evaluation framework.

## Overview

The framework now supports three types of evaluation:

1. **Quality-only**: Traditional accuracy and correctness metrics
2. **Performance-only**: Speed and throughput benchmarks using Ollama bench
3. **Combined**: Quality + performance with composite scoring

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Evaluation Pipeline                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────┐                │
│  │ Query Model  │──────▶│   Outputs    │                │
│  │ (query_*.py) │      │  (JSON file) │                │
│  └──────────────┘      └──────┬───────┘                │
│                                │                          │
│                    ┌───────────┴───────────┐            │
│                    │                         │            │
│           ┌────────▼────────┐    ┌─────────▼──────────┐│
│           │ Quality Eval    │    │ Performance Bench  ││
│           │ (evaluate.py)   │    │ (bench_ollama.py)  ││
│           │                 │    │                    ││
│           │ • Token F1      │    │ • Tokens/sec       ││
│           │ • Exact match   │    │ • Prefill speed    ││
│           │ • JSON validity │    │ • Load time        ││
│           └────────┬────────┘    └─────────┬──────────┘│
│                    │                         │            │
│                    └───────────┬─────────────┘            │
│                                │                          │
│                    ┌───────────▼───────────┐            │
│                    │  Combined Evaluation  │            │
│                    │ (evaluate_combined.py)│            │
│                    │                       │            │
│                    │ • Composite score     │            │
│                    │ • Target checks       │            │
│                    │ • Full report         │            │
│                    └───────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## New Files

### `evaluators/benchmarking/bench_ollama.py`
Wrapper around Ollama's bench command. Provides:
- Per-category benchmarking (fast)
- Per-task benchmarking (thorough)
- CSV parsing and metric aggregation
- Performance summary reports

**Usage:**
```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 5 --mode category
```

### `evaluators/cli/evaluate_combined.py`
Combines quality and performance evaluation:
- Runs quality metrics on existing outputs
- Runs performance benchmarks
- Checks against latency targets (from meta.yaml)
- Calculates composite score (70% quality, 30% performance)

**Usage:**
```bash
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/outputs.json \
    --report outputs/combined_report.json
```

### `evaluators/cli/compare_models.py`
Multi-model comparison tool:
- Runs full pipeline for multiple models
- Generates comparison tables
- Outputs JSON and Markdown reports

**Usage:**
```bash
python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
```

### `evaluators/cli/check_setup.py`
Environment validation:
- Checks Python installation
- Verifies Ollama and bench command
- Validates Python packages

**Usage:**
```bash
python -m evaluators.cli.check_setup
```

## Metrics Explained

### Quality Metrics (from evaluate.py)
- **Token F1**: Overlap between predicted and expected tokens (summarization, reasoning, RAG)
- **Exact Match**: Exact string match (extraction)
- **JSON Validity**: Whether output is valid JSON (extraction)
- **Refusal Rate**: Whether model refuses unsafe requests (safety)

### Performance Metrics (from Ollama bench)
- **Prefill Speed**: Tokens/sec for processing the prompt
- **Generate Speed**: Tokens/sec for generating the response
- **Load Time**: Time to load the model (one-time cost)
- **Total Duration**: End-to-end request time

### Composite Score
```text
Composite = 0.7 × Quality + 0.3 × Performance

Performance Score = (# targets met) / (# total targets)
```

## Latency Targets

Define targets in `taskpacks/meta.yaml`:

```yaml
latency_targets:
  ttft_ms_p95: 1200      # Time to first token (95th percentile)
  tok_per_sec_min: 15    # Minimum generation speed
```

The combined evaluator checks if models meet these targets.

## Benchmark Modes

### Category Mode (Default)
- Benchmarks one representative task per category
- Fast: ~5-10 seconds per model
- Good for quick comparisons

### All Mode
- Benchmarks every task individually
- Thorough: ~1-2 minutes per model
- Good for detailed analysis

## Example Workflows

### Single Model Evaluation
```bash
# 1. Query the model
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/outputs.json

# 2. Run combined evaluation
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/outputs.json \
    --report outputs/report.json
```

### Multi-Model Comparison
```bash
python -m evaluators.cli.compare_models \
    --models "llama3.2,mistral,qwen2.5" \
    --bench-epochs 5 \
    --bench-mode category
```

### Performance-Only Benchmark
```bash
python -m evaluators.benchmarking.bench_ollama \
    --model llama3.2 \
    --epochs 10 \
    --max-tokens 200 \
    --mode all
```

## Output Files

### `outputs/<model>_outputs.json`
Raw model responses for each task:
```json
{
  "task_001": "Model response...",
  "task_002": "Model response..."
}
```

### `outputs/<model>_combined_report.json`
Full evaluation report:
```json
{
  "model": "llama3.2",
  "composite_score": 0.756,
  "quality": {
    "overall_score": 0.823,
    "by_category": {...}
  },
  "performance": {
    "aggregated_metrics": {
      "avg_generate_tokens_per_sec": 45.2,
      "avg_prefill_tokens_per_sec": 1250.5,
      "avg_load_time_ms": 125.3
    },
    "performance_checks": {...}
  }
}
```

### `outputs/comparison.md`
Markdown comparison table for multiple models.

## Requirements

- **Ollama**: For running models
- **Go 1.16+**: For bench tool
- **Python 3.7+**: For evaluation scripts
- **Python packages**: `requests`, `pyyaml`
- **bench.go**: Ollama's benchmark script

### Setup

```bash
# Quick setup (downloads bench.go and optionally builds it)
./setup_bench.sh

# Check setup
python -m evaluators.cli.check_setup
```

### Manual Setup

```bash
# Download bench.go
curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go

# Option 1: Build binary (faster for repeated use)
go build -o ollama-bench bench.go

# Option 2: Use go run (no build needed)
go run bench.go -model llama3.2 -epochs 1
```

## Troubleshooting

### "bench.go not found"
Download the bench script:
```bash
./setup_bench.sh
# Or manually:
curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go
```

### "go: command not found"
Install Go:
```bash
brew install go  # macOS
# Or visit: https://go.dev/doc/install
```

### "ollama: command not found"
Install Ollama:
```bash
brew install ollama  # macOS
# Or visit: https://ollama.ai/download
```

### "Module not found: yaml"
Install Python packages:
```bash
pip install pyyaml requests
```

### Benchmark timeout
Increase timeout for slow models:
```bash
python -m evaluators.benchmarking.bench_ollama --model large-model --timeout 600
```

### Using custom bench.go location
```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --bench-path /path/to/bench.go
```

## Advanced Usage

### Custom Prompts
```bash
python -m evaluators.benchmarking.bench_ollama \
    --model llama3.2 \
    --epochs 5 \
    --max-tokens 500 \
    --temperature 0.7 \
    -p "Write a detailed technical explanation"
```

### Image Benchmarking (Multimodal)
```bash
python -m evaluators.benchmarking.bench_ollama \
    --model llava \
    --image photo.jpg \
    --epochs 3 \
    -p "Describe this image in detail"
```

### Skip Performance Benchmarking
```bash
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/outputs.json \
    --skip-bench
```

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: Model Evaluation
on: [push]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Ollama
        run: curl -fsSL https://ollama.ai/install.sh | sh
      - name: Pull model
        run: ollama pull llama3.2
      - name: Run evaluation
        run: ./example_workflow.sh llama3.2
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: outputs/
```

## Future Enhancements

Potential improvements:
- [ ] Streaming benchmark support
- [ ] Memory usage tracking
- [ ] GPU utilization metrics
- [ ] Batch processing benchmarks
- [ ] Custom metric plugins
- [ ] Web dashboard for results
