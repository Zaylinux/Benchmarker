# SLM Taskpack (Starter)

**Purpose:** Evaluate small language models (SLMs) for an *on-device* assistant that runs on Raspberry Pi–class hardware and
works over a user’s personal “legacy” documents (summaries, Q&A, structured extraction, instruction following) with RAG.

## Contents
```text
taskpacks/
  meta.yaml
  summarization/tasks.json
  reasoning/tasks.json
  extraction/tasks.json
  rag/tasks.json
  safety/tasks.json
evaluators/
  evaluate.py              # Quality metrics
  query_model.py           # OpenAI-compatible querying
  query_ollama.py          # Native Ollama querying
  bench_ollama.py          # Performance benchmarking (NEW)
  evaluate_combined.py     # Quality + performance (NEW)
  compare_models.py        # Multi-model comparison (NEW)
  check_setup.py           # Environment validation (NEW)
outputs/
  (model outputs and reports)
```

📖 **Documentation:**
- [GETTING_STARTED.md](docs/GETTING_STARTED.md) - 5-minute quick start ⭐
- [SETUP.md](docs/SETUP.md) - Complete setup instructions
- [BENCHMARKING.md](docs/BENCHMARKING.md) - Detailed usage guide
- [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Command cheat sheet
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design

## Prerequisites

- Python 3.7+
- Ollama (for running models)
- Go 1.16+ (for bench tool)
- Python packages: `requests`, `pyyaml`

### Quick Setup

```bash
# 1. Download and setup bench tool
./scripts/setup_bench.sh

# 2. Check your setup
python -m evaluators.cli.check_setup
```

### Manual Installation

```bash
# Install Ollama (macOS)
brew install ollama

# Install Go (macOS)
brew install go

# Download bench.go
curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go

# Install Python packages
pip install requests pyyaml
```

## Quick Start

1. **Run a model** (e.g., llama.cpp server or vLLM) with an OpenAI-compatible endpoint.

2. **Query the model** over the taskpack (set your endpoint in `evaluators/querying/query_model.py`):
```bash
python -m evaluators.querying.query_model --base_url http://localhost:8080/v1 --model llama.cpp --out outputs/outputs.json
```

3. **Evaluate** the outputs:
```bash
python -m evaluators.cli.evaluate --outputs outputs/outputs.json --report outputs/report.json
```

4. **Read the scores** from `outputs/report.json`. You’ll get per-category metrics and an overall weighted score
based on `taskpacks/meta.yaml`.

## Notes
- Metrics are intentionally **lightweight** for offline use: exact match, JSON validity, and a simple token F1 overlap.
- You can extend with embedding-based similarity or ROUGE if you have those packages available.
- The **RAG** set includes a small in-pack "corpus" field for each item to simulate retrieval. Your runner should prepend
the provided `context` text to the model prompt before asking the question.


## Ollama Quick Start

1. Install and start Ollama:
   ```bash
   ollama serve  # default listens on http://localhost:11434
   ```
2. Pull a model (examples):
   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ollama pull qwen2.5
   ```
3. Option A — use OpenAI-compatible Chat Completions:
   ```bash
   python -m evaluators.querying.query_model --base_url http://localhost:11434/v1 --model llama3.2 --out outputs/outputs.json
   ```
4. Option B — use native Ollama REST API:
   ```bash
   python -m evaluators.querying.query_ollama --host http://localhost:11434 --model llama3.2 --out outputs/outputs.json
   ```
5. Evaluate:
   ```bash
   python -m evaluators.cli.evaluate --outputs outputs/outputs.json --report outputs/report.json
   ```

## Performance Benchmarking

The framework integrates Ollama's bench Go script for performance metrics.

**Note:** The bench tool is a separate Go script, not a built-in Ollama command. Run `./scripts/setup_bench.sh` to download and set it up.

### Option 1: Performance-only benchmark
```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 5 --max-tokens 100
```

### Option 2: Combined quality + performance evaluation
```bash
# First, generate outputs
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/outputs.json

# Then run combined evaluation
python -m evaluators.cli.evaluate_combined --model llama3.2 --outputs outputs/outputs.json --report outputs/combined_report.json
```

The combined evaluation provides:
- Quality scores (accuracy, JSON validity, token F1)
- Performance metrics (tokens/sec, prefill speed, load time)
- Latency target checks (from `taskpacks/meta.yaml`)
- Composite score (70% quality, 30% performance)

### Benchmark modes
- `--bench-mode category`: Fast, benchmarks one task per category (default)
- `--bench-mode all`: Thorough, benchmarks every task (slower)

### Compare multiple models
```bash
python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5" --bench-epochs 5
```

This generates:
- `outputs/comparison.json`: Detailed results for all models
- `outputs/comparison.md`: Markdown comparison table

### Quick workflow script
```bash
./scripts/example_workflow.sh llama3.2
```

This runs the complete pipeline: setup check → query → combined evaluation.

## How It Works

The bench tool is Ollama's official Go-based benchmark script:

1. **Download bench.go**: `./scripts/setup_bench.sh` downloads it from the Ollama repo
2. **Run benchmarks**: Either use `go run bench.go` or build with `go build`
3. **Python wrapper**: `evaluators/benchmarking/bench_ollama.py` wraps the Go script for easy integration
4. **Auto-detection**: The wrapper automatically finds bench.go or ollama-bench binary

```text
bench.go (Go script) → Python wrapper → Combined evaluation → Reports
```
