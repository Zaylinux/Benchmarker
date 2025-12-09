# Ollama Bench Integration Summary

## Important Note

**The Ollama bench tool is a separate Go script (`bench.go`), not a built-in Ollama command.**

You need to:
1. Download `bench.go` from the Ollama repository
2. Have Go installed to run it
3. Either use `go run bench.go` or build it with `go build`

Run `./setup_bench.sh` to automate this process.

## What Was Added

### 🆕 New Evaluator Scripts (4 files)

1. **`evaluators/benchmarking/bench_ollama.py`** (200 lines)
   - Wraps Ollama's bench command
   - Parses CSV output into structured metrics
   - Supports per-category and per-task benchmarking
   - Aggregates performance metrics

2. **`evaluators/cli/evaluate_combined.py`** (180 lines)
   - Combines quality and performance evaluation
   - Checks latency targets from meta.yaml
   - Calculates composite scores (70% quality, 30% performance)
   - Generates comprehensive reports

3. **`evaluators/cli/compare_models.py`** (200 lines)
   - Multi-model comparison pipeline
   - Generates JSON and Markdown reports
   - Creates comparison tables automatically
   - Runs full evaluation for each model

4. **`evaluators/cli/check_setup.py`** (80 lines)
   - Validates environment setup
   - Checks Ollama installation and version
   - Verifies Python packages
   - Tests bench command availability

### 📚 Documentation (5 files)

1. **`SETUP.md`** (NEW - 8KB)
   - Complete setup instructions
   - Step-by-step installation guide
   - Troubleshooting common issues
   - Testing procedures

2. **`BENCHMARKING.md`** (9KB)
   - Complete integration guide
   - Architecture diagrams
   - Detailed metric explanations
   - Example workflows
   - Troubleshooting guide

3. **`QUICK_REFERENCE.md`** (3.6KB)
   - One-liner commands
   - Common options reference
   - Output file descriptions
   - Quick troubleshooting table

4. **`INTEGRATION_SUMMARY.md`**
   - What was added and why
   - Feature overview
   - Technical details

5. **Updated `README.md`**
   - Added prerequisites section
   - New performance benchmarking section
   - Model comparison examples
   - Links to detailed guides

### 🔧 Utility Scripts (2 files)

1. **`setup_bench.sh`** (NEW)
   - Automated setup script
   - Downloads bench.go from GitHub
   - Optionally builds binary
   - Interactive prompts

2. **`example_workflow.sh`**
   - Complete evaluation pipeline
   - Checks for bench.go
   - Setup check → query → combined evaluation
   - Single command for full workflow

## Integration Features

### ✅ What It Does

- **Performance Benchmarking**: Measures tokens/sec, prefill speed, load time
- **Quality Metrics**: Existing accuracy, F1, JSON validity checks
- **Combined Scoring**: Composite score combining quality and performance
- **Target Validation**: Checks if models meet latency requirements
- **Multi-Model Comparison**: Automated comparison with table generation
- **Two Benchmark Modes**: Fast (category) and thorough (all tasks)

### 🎯 Key Capabilities

1. **Standalone Performance Testing**
   ```bash
   python -m evaluators.benchmarking.bench_ollama --model llama3.2
   ```

2. **Combined Quality + Performance**
   ```bash
   python -m evaluators.cli.evaluate_combined --model llama3.2 --outputs outputs/out.json
   ```

3. **Multi-Model Comparison**
   ```bash
   python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
   ```

4. **Environment Validation**
   ```bash
   python -m evaluators.cli.check_setup
   ```

## Technical Details

### Dependencies
- **Ollama**: For running models
- **Go 1.16+**: For bench tool
- **bench.go**: Ollama's benchmark script (downloaded separately)
- **Python 3.7+**: For scripts
- **Python packages**: `requests`, `pyyaml`

### Metrics Collected

#### Performance (from Ollama bench)
- Prefill tokens/sec
- Generate tokens/sec  
- Load time (ms)
- Total duration

#### Quality (existing)
- Token F1 (summarization, reasoning, RAG)
- Exact match (extraction)
- JSON validity (extraction)
- Refusal rate (safety)

### Composite Scoring
```text
Composite Score = 0.7 × Quality Score + 0.3 × Performance Score

Performance Score = (# targets met) / (# total targets)
```

### Benchmark Modes

| Mode       | Speed      | Use Case           |
|------------|------------|--------------------|
| `category` | ~5-10 sec  | Quick comparisons  |
| `all`      | ~1-2 min   | Detailed analysis  |

## File Structure

```text
Benchmarker/
├── evaluators/
│   ├── bench_ollama.py          ← NEW: Performance benchmarking
│   ├── evaluate_combined.py     ← NEW: Combined evaluation
│   ├── compare_models.py        ← NEW: Multi-model comparison
│   ├── check_setup.py           ← NEW: Setup validation
│   ├── evaluate.py              (existing)
│   ├── query_model.py           (existing)
│   └── query_ollama.py          (existing)
├── taskpacks/
│   └── meta.yaml                (updated with latency_targets)
├── outputs/                     (generated reports)
├── BENCHMARKING.md              ← NEW: Detailed guide
├── QUICK_REFERENCE.md           ← NEW: Quick commands
├── README.md                    (updated)
└── example_workflow.sh          ← NEW: Complete workflow
```

## Usage Examples

### Example 0: Initial Setup
```bash
# Download and setup bench.go
./setup_bench.sh

# Verify setup
python -m evaluators.cli.check_setup
```

### Example 1: Single Model Evaluation
```bash
# Query model
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json

# Run combined evaluation
python -m evaluators.cli.evaluate_combined \
    --model llama3.2 \
    --outputs outputs/out.json \
    --report outputs/report.json
```

**Output:**
```text
Composite Score: 0.756
  Quality (70%): 0.823
  Performance (30%): 0.550

Performance Targets:
  ✓ tokens_per_sec: 45.2 (target: 15)
  ✗ ttft_ms: 1450 (target: 1200)
```

### Example 2: Compare Multiple Models
```bash
python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
```

**Output:** `outputs/comparison.md`
```markdown
| Model | Composite | Quality | Perf | Gen Speed (tok/s) |
|-------|-----------|---------|------|-------------------|
| llama3.2 | 0.756 | 0.823 | 0.550 | 45.2 |
| mistral | 0.782 | 0.801 | 0.720 | 52.1 |
| qwen2.5 | 0.791 | 0.845 | 0.650 | 48.3 |
```

### Example 3: Performance-Only Benchmark
```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 10 --mode all
```

**Output:**
```text
PERFORMANCE SUMMARY
Model: llama3.2
Avg Prefill Speed: 1250.45 tokens/sec
Avg Generate Speed: 45.23 tokens/sec
Avg Load Time: 125.34 ms
```

## Integration Benefits

### For Users
- ✅ Single command for complete evaluation
- ✅ Automatic comparison tables
- ✅ Clear performance vs quality tradeoffs
- ✅ Validates against latency targets

### For Development
- ✅ Modular design (can use components separately)
- ✅ Extensible (easy to add new metrics)
- ✅ Well-documented (3 documentation files)
- ✅ Error handling and validation

### For CI/CD
- ✅ Scriptable workflows
- ✅ JSON output for automation
- ✅ Exit codes for pass/fail
- ✅ Environment validation

## Next Steps

To use the integration:

1. **Check setup**
   ```bash
   python -m evaluators.cli.check_setup
   ```

2. **Run example workflow**
   ```bash
   ./example_workflow.sh llama3.2
   ```

3. **Compare models**
   ```bash
   python -m evaluators.cli.compare_models --models "model1,model2"
   ```

4. **Read the guides**
   - `BENCHMARKING.md` for detailed information
   - `QUICK_REFERENCE.md` for command cheat sheet

## Compatibility

- ✅ Works with existing evaluation framework
- ✅ Backward compatible (old scripts still work)
- ✅ Optional (can skip performance benchmarking)
- ✅ Requires Ollama v13.0+ for bench features

## Summary

The integration adds **comprehensive performance benchmarking** to your existing quality evaluation framework, providing:

- 4 new Python scripts (660 lines of code)
- 3 documentation files (16KB)
- 1 workflow automation script
- Combined quality + performance scoring
- Multi-model comparison capabilities
- Complete environment validation

All while maintaining backward compatibility with your existing evaluation pipeline.
