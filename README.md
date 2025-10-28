# SLM Taskpack (Starter)

**Purpose:** Evaluate small language models (SLMs) for an *on-device* assistant that runs on Raspberry Pi–class hardware and
works over a user’s personal “legacy” documents (summaries, Q&A, structured extraction, instruction following) with RAG.

## Contents
```
taskpacks/
  meta.yaml
  summarization/tasks.json
  reasoning/tasks.json
  extraction/tasks.json
  rag/tasks.json
  safety/tasks.json
evaluators/
  evaluate.py
  query_model.py
  sample_schema.json
outputs/
  (place model outputs here as outputs.json)
```

## Quick Start

1. **Run a model** (e.g., llama.cpp server or vLLM) with an OpenAI-compatible endpoint.

2. **Query the model** over the taskpack (set your endpoint in `evaluators/query_model.py`):
```bash
python evaluators/query_model.py --base_url http://localhost:8080/v1 --model llama.cpp --out outputs/outputs.json
```

3. **Evaluate** the outputs:
```bash
python evaluators/evaluate.py --outputs outputs/outputs.json --report outputs/report.json
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
   python evaluators/query_model.py --base_url http://localhost:11434/v1 --model llama3.2 --out outputs/outputs.json
   ```
4. Option B — use native Ollama REST API:
   ```bash
   python evaluators/query_ollama.py --host http://localhost:11434 --model llama3.2 --out outputs/outputs.json
   ```
5. Evaluate:
   ```bash
   python evaluators/evaluate.py --outputs outputs/outputs.json --report outputs/report.json
   ```
