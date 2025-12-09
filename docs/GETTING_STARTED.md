# Getting Started

Quick start guide to get benchmarking in 5 minutes.

## TL;DR

```bash
# 1. Setup (one time)
./setup_bench.sh

# 2. Pull a model
ollama pull llama3.2

# 3. Run evaluation
./example_workflow.sh llama3.2
```

Done! Results in `outputs/llama3.2_combined_report.json`

## Step-by-Step Guide

### Step 1: Install Prerequisites (5 minutes)

**macOS:**
```bash
# Install Ollama
brew install ollama

# Install Go
brew install go

# Install Python packages
pip install requests pyyaml
```

**Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install Go
# Visit: https://go.dev/doc/install

# Install Python packages
pip install requests pyyaml
```

### Step 2: Setup Bench Tool (1 minute)

```bash
# Automated setup
./setup_bench.sh
```

This will:
- Download `bench.go` from Ollama's GitHub
- Ask if you want to build a binary (recommended: yes)
- Create `ollama-bench` executable

**Or manually:**
```bash
curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go
go build -o ollama-bench bench.go
```

### Step 3: Verify Setup (30 seconds)

```bash
python -m evaluators.cli.check_setup
```

Expected output:
```text
✓ Python is installed
✓ Ollama is installed
✓ Go is installed
✓ Bench tool found
✓ Python packages installed
✓ All checks passed!
```

### Step 4: Pull a Model (1-2 minutes)

```bash
# Start Ollama (if not running)
ollama serve

# In another terminal, pull a model
ollama pull llama3.2
```

### Step 5: Run Your First Evaluation (2-5 minutes)

**Option A: Complete workflow (recommended)**
```bash
./example_workflow.sh llama3.2
```

**Option B: Step by step**
```bash
# Query the model
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json

# Run combined evaluation
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/out.json \
    --report outputs/report.json
```

### Step 6: View Results

```bash
# View the report
cat outputs/llama3.2_combined_report.json | python -m json.tool

# Or just the summary
cat outputs/llama3.2_combined_report.json | grep -A 5 "composite_score"
```

## What You Get

After running the evaluation, you'll have:

```json
{
  "model": "llama3.2",
  "composite_score": 0.756,
  "quality": {
    "overall_score": 0.823,
    "by_category": {
      "summarization": 0.85,
      "reasoning": 0.78,
      "extraction": 0.92,
      "rag": 0.81,
      "safety": 1.0
    }
  },
  "performance": {
    "aggregated_metrics": {
      "avg_generate_tokens_per_sec": 45.2,
      "avg_prefill_tokens_per_sec": 1250.5,
      "avg_load_time_ms": 125.3
    }
  }
}
```

## Next Steps

### Compare Multiple Models

```bash
python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
```

Generates a comparison table in `outputs/comparison.md`:

| Model    | Composite | Quality | Perf | Gen Speed |
|----------|-----------|---------|------|-----------|
| llama3.2 | 0.756     | 0.823   | 0.55 | 45.2 t/s  |
| mistral  | 0.782     | 0.801   | 0.72 | 52.1 t/s  |
| qwen2.5  | 0.791     | 0.845   | 0.65 | 48.3 t/s  |

### Performance-Only Benchmark

```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 10
```

### Quality-Only Evaluation

```bash
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json
python -m evaluators.cli.evaluate --outputs outputs/out.json --report outputs/report.json
```

## Common Workflows

### Workflow 1: Quick Model Test
```bash
# Fast evaluation (1-2 minutes)
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/out.json \
    --bench-mode category \
    --bench-epochs 1
```

### Workflow 2: Thorough Evaluation
```bash
# Detailed evaluation (5-10 minutes)
./example_workflow.sh llama3.2
# Uses: category mode, 5 epochs
```

### Workflow 3: Model Selection
```bash
# Compare 3 models (15-30 minutes)
python -m evaluators.cli.compare_models \
    --models "llama3.2,mistral,qwen2.5" \
    --bench-epochs 5
```

### Workflow 4: Performance Testing
```bash
# Just performance metrics (30 seconds)
python -m evaluators.benchmarking.bench_ollama \
    --model llama3.2 \
    --epochs 10 \
    --mode category
```

## Understanding the Scores

### Composite Score (0.0 - 1.0)
- Combines quality (70%) and performance (30%)
- Higher is better
- 0.8+ = Excellent
- 0.7-0.8 = Good
- 0.6-0.7 = Fair
- <0.6 = Needs improvement

### Quality Score (0.0 - 1.0)
- Measures accuracy and correctness
- Based on token overlap, exact matches, JSON validity
- Category-weighted (see `taskpacks/meta.yaml`)

### Performance Score (0.0 - 1.0)
- Based on meeting latency targets
- Checks tokens/sec and time-to-first-token
- Targets defined in `taskpacks/meta.yaml`

## Troubleshooting

### "bench.go not found"
```bash
./setup_bench.sh
```

### "go: command not found"
```bash
brew install go  # macOS
# Or visit: https://go.dev/doc/install
```

### "ollama: command not found"
```bash
brew install ollama  # macOS
# Or visit: https://ollama.ai/download
```

### "connection refused"
```bash
# Start Ollama server
ollama serve
```

### "model not found"
```bash
# Pull the model first
ollama pull llama3.2
```

## File Locations

After setup and first run:

```text
Benchmarker/
├── bench.go                           ← Downloaded by setup
├── ollama-bench                       ← Built binary (optional)
├── outputs/
│   ├── llama3.2_outputs.json         ← Model responses
│   ├── llama3.2_combined_report.json ← Full report
│   └── comparison.md                  ← Multi-model comparison
├── evaluators/                        ← Python scripts
├── taskpacks/                         ← Test tasks
└── *.md                               ← Documentation
```

## Tips

1. **Build the binary**: Faster for repeated use
   ```bash
   go build -o ollama-bench bench.go
   ```

2. **Use category mode**: Much faster for quick tests
   ```bash
   --bench-mode category
   ```

3. **Adjust epochs**: More epochs = more stable metrics
   ```bash
   --bench-epochs 10
   ```

4. **Keep Ollama running**: Start `ollama serve` in a separate terminal

5. **Pull models ahead**: Download models before benchmarking
   ```bash
   ollama pull llama3.2 mistral qwen2.5
   ```

## Learn More

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[BENCHMARKING.md](BENCHMARKING.md)** - Complete usage guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design

## Support

If you get stuck:

1. Run diagnostics: `python -m evaluators.cli.check_setup`
2. Check Ollama: `ollama list`
3. Test bench directly: `go run bench.go -model llama3.2 -epochs 1 -max-tokens 10`
4. Read troubleshooting: See `SETUP.md` or `BENCHMARKING.md`

## Summary

```bash
# One-time setup
./setup_bench.sh && ollama pull llama3.2

# Run evaluation
./example_workflow.sh llama3.2

# View results
cat outputs/llama3.2_combined_report.json
```

That's it! You're benchmarking. 🚀
