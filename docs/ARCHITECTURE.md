# Architecture: Ollama Bench Integration

## System Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                    SLM Evaluation Framework                      │
│                     (with Ollama Bench v13.0+)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  Taskpacks   │    │   Models     │    │  Meta Config │     │
│  │              │    │              │    │              │     │
│  │ • tasks.json │    │ • llama3.2   │    │ • Weights    │     │
│  │ • 5 categories│   │ • mistral    │    │ • Targets    │     │
│  │ • Expected   │    │ • qwen2.5    │    │ • Metrics    │     │
│  │   outputs    │    │ • custom     │    │              │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  query_model.py    │         │  query_ollama.py   │         │
│  │                    │         │                    │         │
│  │ • OpenAI API       │         │ • Native Ollama    │         │
│  │ • Generic models   │         │ • Optimized        │         │
│  │ • Flexible         │         │ • JSON format      │         │
│  └────────────────────┘         └────────────────────┘         │
│                                                                   │
│                    Generates: outputs.json                       │
│                    { "task_id": "response", ... }                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUATION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    QUALITY METRICS                        │  │
│  │                   (evaluate.py)                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  Summarization  │  Reasoning  │  Extraction  │  RAG  │ Safety│
│  │  ─────────────  │  ─────────  │  ──────────  │  ───  │ ───── │
│  │  • Token F1     │  • Token F1 │  • Exact     │  • F1 │ • Ref │
│  │  • Overlap      │  • Logic    │    Match     │  • Ctx│   use │
│  │                 │             │  • JSON      │       │       │
│  │                 │             │    Valid     │       │       │
│  │                                                            │  │
│  │  Weights: 30%   │    30%      │    20%       │  15%  │  5%  │
│  │                                                            │  │
│  │  Output: Quality Score (0.0 - 1.0)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 PERFORMANCE METRICS                       │  │
│  │                 (bench_ollama.py)                         │  │
│  │                 [NEW - Ollama v13.0+]                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ Prefill  │  │ Generate │  │   Load   │  │  Total   │ │  │
│  │  │  Speed   │  │  Speed   │  │   Time   │  │ Duration │ │  │
│  │  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤ │  │
│  │  │ tok/sec  │  │ tok/sec  │  │    ms    │  │    ms    │ │  │
│  │  │          │  │          │  │          │  │          │ │  │
│  │  │ Prompt   │  │ Response │  │ Model    │  │ End-to-  │ │  │
│  │  │ process  │  │ generate │  │ loading  │  │   end    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  │                                                            │  │
│  │  Modes: category (fast) | all (thorough)                  │  │
│  │  Output: Performance Metrics + Target Checks              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMBINED EVALUATION                           │
│                  (evaluate_combined.py)                          │
│                         [NEW]                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  Quality Score     │         │ Performance Score  │         │
│  │                    │         │                    │         │
│  │  From evaluate.py  │         │ From bench_ollama  │         │
│  │  (0.0 - 1.0)       │         │ (target checks)    │         │
│  └─────────┬──────────┘         └─────────┬──────────┘         │
│            │                              │                      │
│            │  Weight: 70%                 │  Weight: 30%        │
│            │                              │                      │
│            └──────────────┬───────────────┘                      │
│                           │                                      │
│                           ▼                                      │
│              ┌────────────────────────┐                         │
│              │   COMPOSITE SCORE      │                         │
│              │                        │                         │
│              │  0.7×Quality +         │                         │
│              │  0.3×Performance       │                         │
│              │                        │                         │
│              │  (0.0 - 1.0)           │                         │
│              └────────────────────────┘                         │
│                                                                   │
│  Additional Outputs:                                             │
│  • Category breakdown                                            │
│  • Latency target checks (ttft_ms, tok_per_sec)                │
│  • Detailed performance metrics                                 │
│  • Pass/fail indicators                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPARISON LAYER                              │
│                   (compare_models.py)                            │
│                         [NEW]                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: Multiple models (comma-separated)                        │
│                                                                   │
│  For each model:                                                 │
│    1. Query model → outputs.json                                │
│    2. Run combined evaluation → report.json                     │
│    3. Collect results                                            │
│                                                                   │
│  Generate:                                                       │
│    • comparison.json (detailed results)                         │
│    • comparison.md (markdown table)                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Comparison Table                                   │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Model    │ Composite │ Quality │ Perf │ Gen Speed │ ... │  │
│  │──────────┼───────────┼─────────┼──────┼───────────┼─────│  │
│  │ llama3.2 │   0.756   │  0.823  │ 0.55 │  45.2 t/s │ ... │  │
│  │ mistral  │   0.782   │  0.801  │ 0.72 │  52.1 t/s │ ... │  │
│  │ qwen2.5  │   0.791   │  0.845  │ 0.65 │  48.3 t/s │ ... │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  outputs/                                                        │
│  ├── <model>_outputs.json          (raw responses)              │
│  ├── <model>_report.json           (quality only)               │
│  ├── <model>_combined_report.json  (quality + performance)      │
│  ├── bench_results.json            (performance only)           │
│  ├── comparison.json               (multi-model JSON)           │
│  └── comparison.md                 (multi-model table)          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Standalone Usage

```text
1. Quality Only:
   query_ollama.py → evaluate.py → quality_report.json

2. Performance Only:
   bench_ollama.py → bench_results.json

3. Combined:
   query_ollama.py → evaluate_combined.py → combined_report.json
                     (calls evaluate.py + bench_ollama.py internally)

4. Comparison:
   compare_models.py → (runs #3 for each model) → comparison.json + .md
```

### Data Flow

```text
Taskpacks → Query → Outputs → Evaluation → Reports
    ↓                            ↓
Meta.yaml ──────────────────→ Scoring
                                 ↓
                            Composite Score
```

## Key Design Decisions

### 1. Modular Architecture
- Each component can be used independently
- No breaking changes to existing scripts
- Optional performance benchmarking

### 2. Two-Phase Evaluation
- Phase 1: Query model (generate outputs once)
- Phase 2: Evaluate (can run multiple times on same outputs)

### 3. Composite Scoring
- 70% quality, 30% performance
- Configurable via meta.yaml
- Reflects real-world priorities (accuracy > speed)

### 4. Benchmark Modes
- Category mode: Fast, representative sampling
- All mode: Thorough, every task
- Balances speed vs completeness

### 5. Output Formats
- JSON: Machine-readable, automation-friendly
- Markdown: Human-readable, shareable
- Both generated automatically

## Extension Points

### Adding New Metrics
1. Extend `evaluate.py` for quality metrics
2. Extend `bench_ollama.py` for performance metrics
3. Update `meta.yaml` with weights

### Adding New Categories
1. Create `taskpacks/<category>/tasks.json`
2. Add weight to `meta.yaml`
3. Update scoring logic in `evaluate.py`

### Custom Benchmarks
1. Subclass or wrap `bench_ollama.py`
2. Override `run_ollama_bench()` method
3. Add custom metric aggregation

## Performance Characteristics

| Operation             | Time      | Notes                   |
|-----------------------|-----------|-------------------------|
| Query (50 tasks)      | 2-5 min   | Depends on model speed  |
| Quality eval          | <1 sec    | Lightweight metrics     |
| Perf bench (category) | 5-10 sec  | 5 tasks × 3 epochs      |
| Perf bench (all)      | 1-2 min   | 50 tasks × 3 epochs     |
| Combined eval         | 2-7 min   | Query + both evals      |
| Compare 3 models      | 6-21 min  | 3× combined eval        |

## Dependencies

```text
External:
├── Ollama v13.0+ (bench command)
├── Python 3.7+
└── Python packages
    ├── requests (HTTP client)
    └── pyyaml (config parsing)

Internal:
├── taskpacks/ (test data)
├── evaluators/ (Python modules)
│   ├── cli/ (command-line scripts)
│   ├── core/ (evaluation logic)
│   ├── benchmarking/ (performance testing)
│   ├── querying/ (model interfaces)
│   └── reporting/ (report generation)
├── scripts/ (shell scripts)
├── docs/ (documentation)
└── outputs/ (results)
```

## Error Handling

```text
check_setup.py
    ↓
Validates environment
    ↓
    ├─ Ollama installed? ──→ No ──→ Error + install instructions
    ├─ Bench available? ───→ No ──→ Error + upgrade instructions
    └─ Python packages? ───→ No ──→ Error + pip install command
    ↓
All checks pass
    ↓
Ready to benchmark
```

## Summary

The architecture provides:
- ✅ Modular, extensible design
- ✅ Backward compatibility
- ✅ Multiple usage modes
- ✅ Comprehensive error handling
- ✅ Automated comparison workflows
- ✅ Clear separation of concerns
- ✅ Efficient data flow
