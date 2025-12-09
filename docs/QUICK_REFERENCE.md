# Quick Reference: Ollama Bench Integration

## One-Liners

### Initial Setup
```bash
./scripts/setup_bench.sh && python -m evaluators.cli.check_setup
```

### Setup Check
```bash
python -m evaluators.cli.check_setup
```

### Single Model - Quality Only
```bash
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json && \
python -m evaluators.cli.evaluate --outputs outputs/out.json --report outputs/report.json
```

### Single Model - Performance Only
```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 5
```

### Single Model - Combined (Quality + Performance)
```bash
python -m evaluators.querying.query_ollama --model llama3.2 --out outputs/out.json && \
python -m evaluators.cli.evaluate_combined --model llama3.2 --outputs outputs/out.json
```

### Compare Multiple Models
```bash
python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
```

### Complete Workflow
```bash
./scripts/example_workflow.sh llama3.2
```

## Common Options

### bench_ollama.py
```bash
--model MODEL          # Required: Ollama model name
--epochs N             # Benchmark iterations (default: 3)
--max-tokens N         # Max tokens to generate (default: 100)
--mode category|all    # Benchmark mode (default: category)
--out FILE             # Output JSON file
```

### evaluate_combined.py
```bash
--model MODEL          # Required: Model name
--outputs FILE         # Required: Path to outputs.json
--report FILE          # Output report file
--bench-epochs N       # Benchmark iterations (default: 3)
--bench-mode MODE      # category or all (default: category)
--skip-bench           # Skip performance benchmarking
```

### compare_models.py
```bash
--models "m1,m2,m3"    # Required: Comma-separated model names
--bench-epochs N       # Benchmark iterations (default: 3)
--bench-mode MODE      # category or all (default: category)
--out FILE             # JSON output (default: outputs/comparison.json)
--markdown FILE        # Markdown output (default: outputs/comparison.md)
```

## Output Files

| File                                       | Description                          |
|--------------------------------------------|--------------------------------------|
| `outputs/<model>_outputs.json`             | Raw model responses                  |
| `outputs/<model>_report.json`              | Quality-only evaluation              |
| `outputs/<model>_combined_report.json`     | Quality + performance                |
| `outputs/bench_results.json`               | Performance-only benchmark           |
| `outputs/comparison.json`                  | Multi-model comparison (JSON)        |
| `outputs/comparison.md`                    | Multi-model comparison (Markdown)    |

## Key Metrics

### Quality Metrics
- **Overall Score**: Weighted average across categories
- **Token F1**: Token overlap (summarization, reasoning, RAG)
- **Exact Match**: String equality (extraction)
- **JSON Validity**: Valid JSON output (extraction)
- **Refusal Rate**: Safety compliance (safety)

### Performance Metrics
- **Generate Speed**: Tokens/sec during generation
- **Prefill Speed**: Tokens/sec during prompt processing
- **Load Time**: Model loading time (ms)

### Composite Score
```text
Composite = 0.7 × Quality + 0.3 × Performance
```

## Troubleshooting

| Issue                       | Solution                                      |
|-----------------------------|-----------------------------------------------|
| `bench.go not found`        | Run setup: `./scripts/setup_bench.sh`         |
| `go: command not found`     | Install Go: `brew install go`                 |
| `ollama: command not found` | Install Ollama: `brew install ollama`         |
| `Module not found: yaml`    | Install packages: `pip install pyyaml requests` |
| Benchmark timeout           | Increase timeout: `--timeout 600`             |
| Model not found             | Pull model: `ollama pull <model>`             |
| Custom bench location       | Use: `--bench-path /path/to/bench.go`         |

## Tips

- Use `--bench-mode category` for quick comparisons (5-10 sec)
- Use `--bench-mode all` for thorough analysis (1-2 min)
- Set `--epochs 10` for more stable performance metrics
- Check `taskpacks/meta.yaml` to adjust category weights
- Use `compare_models.py` to generate comparison tables automatically
