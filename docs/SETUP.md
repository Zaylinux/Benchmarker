# Setup Guide

Complete setup instructions for the Ollama Bench integration.

## Overview

The evaluation framework requires:
1. **Ollama** - To run language models
2. **Go** - To run the bench tool
3. **bench.go** - Ollama's benchmark script
4. **Python 3.7+** - For evaluation scripts
5. **Python packages** - requests, pyyaml

## Quick Setup (Recommended)

```bash
# 1. Run the automated setup script
./scripts/setup_bench.sh

# 2. Verify everything is installed
python -m evaluators.cli.check_setup

# 3. Pull a model to test
ollama pull llama3.2

# 4. Run a test evaluation
./scripts/example_workflow.sh llama3.2
```

## Detailed Setup

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

**Verify:**
```bash
ollama --version
```

### Step 2: Install Go

**macOS:**
```bash
brew install go
```

**Linux:**
```bash
# Download from https://go.dev/dl/
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

**Windows:**
Download installer from https://go.dev/dl/

**Verify:**
```bash
go version
```

### Step 3: Get bench.go

**Option A: Automated (Recommended)**
```bash
./scripts/setup_bench.sh
```

**Option B: Manual Download**
```bash
curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go
```

**Option C: Clone Ollama Repo**
```bash
git clone https://github.com/ollama/ollama.git
cp ollama/cmd/bench/bench.go .
```

### Step 4: Build bench (Optional but Recommended)

Building creates a faster binary for repeated use:

```bash
go build -o ollama-bench bench.go
```

Now you can use:
```bash
./ollama-bench -model llama3.2 -epochs 3
```

Instead of:
```bash
go run bench.go -model llama3.2 -epochs 3
```

### Step 5: Install Python Dependencies

```bash
pip install requests pyyaml
```

Or with a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests pyyaml
```

### Step 6: Verify Setup

```bash
python -m evaluators.cli.check_setup
```

Expected output:
```text
==========================================
SETUP CHECK
==========================================

Checking Python...
✓ Python is installed
  Version: Python 3.11.5

Checking Ollama...
✓ Ollama is installed
  Version: ollama version is 0.1.17

Checking Go...
✓ Go is installed: go version go1.21.5 darwin/arm64

Checking Bench Script...
✓ Bench tool found: Pre-built binary at ./ollama-bench

Checking Python packages...
✓ Python package 'requests' is installed
✓ Python package 'yaml' is installed

==========================================
✓ All checks passed! You're ready to benchmark.
```

## Usage Modes

### Mode 1: Using Pre-built Binary (Fastest)

```bash
# Build once
go build -o ollama-bench bench.go

# Use many times
./ollama-bench -model llama3.2 -epochs 5 -format csv
```

### Mode 2: Using go run (No Build Required)

```bash
# Run directly (compiles each time)
go run bench.go -model llama3.2 -epochs 5 -format csv
```

### Mode 3: Through Python Wrapper (Recommended for Framework)

```bash
# Auto-detects bench.go or ollama-bench
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 5

# Or specify path explicitly
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --bench-path ./bench.go
```

## Testing Your Setup

### Test 1: Direct Bench Tool

```bash
# Quick test (1 epoch, 10 tokens)
go run bench.go -model llama3.2 -epochs 1 -max-tokens 10

# Expected output:
# NAME,STEP,COUNT,NS_PER_COUNT,TOKEN_PER_SEC
# llama3.2,prefill,128,78125.00,12800.00
# llama3.2,generate,10,19531.25,51.20
# ...
```

### Test 2: Python Wrapper

```bash
python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 1 --max-tokens 10

# Expected output:
# Running Ollama bench for model: llama3.2
# Mode: category, Epochs: 1, Max tokens: 10
# 
# Benchmarking summarization with 10 tasks...
# ...
```

### Test 3: Full Workflow

```bash
./scripts/example_workflow.sh llama3.2

# Runs: setup check → query → combined evaluation
```

## Common Issues

### Issue: "bench.go not found"

**Solution:**
```bash
./scripts/setup_bench.sh
```

### Issue: "go: command not found"

**Solution:**
```bash
# macOS
brew install go

# Linux
# Visit https://go.dev/doc/install

# Verify
go version
```

### Issue: "ollama: command not found"

**Solution:**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

### Issue: "model not found"

**Solution:**
```bash
# List available models
ollama list

# Pull a model
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2.5
```

### Issue: Bench tool runs but no output

**Check:**
1. Is Ollama running? `ollama serve` (in separate terminal)
2. Is the model pulled? `ollama list`
3. Try with verbose: `go run bench.go -model llama3.2 -v`

### Issue: Python import errors

**Solution:**
```bash
pip install requests pyyaml

# Or in virtual environment
python -m venv venv
source venv/bin/activate
pip install requests pyyaml
```

## Directory Structure

After setup, your directory should look like:

```text
Benchmarker/
├── bench.go                    ← Downloaded bench script
├── ollama-bench               ← Built binary (optional)
├── scripts/
│   ├── setup_bench.sh         ← Setup script
│   └── example_workflow.sh    ← Test workflow
├── evaluators/
│   ├── benchmarking/
│   │   └── bench_ollama.py    ← Python wrapper
│   ├── cli/
│   │   └── check_setup.py     ← Setup validator
│   └── ...
├── taskpacks/
│   └── ...
└── outputs/
    └── (generated reports)
```

## Next Steps

Once setup is complete:

1. **Pull some models:**
   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ollama pull qwen2.5
   ```

2. **Run a quick test:**
   ```bash
   python -m evaluators.benchmarking.bench_ollama --model llama3.2 --epochs 1
   ```

3. **Run full evaluation:**
   ```bash
   ./scripts/example_workflow.sh llama3.2
   ```

4. **Compare models:**
   ```bash
   python -m evaluators.cli.compare_models --models "llama3.2,mistral,qwen2.5"
   ```

5. **Read the guides:**
   - `docs/BENCHMARKING.md` - Detailed usage guide
   - `docs/QUICK_REFERENCE.md` - Command cheat sheet
   - `docs/ARCHITECTURE.md` - System design

## Advanced Configuration

### Custom bench.go Location

```bash
# Store bench.go in a custom location
mkdir -p ~/tools
cp bench.go ~/tools/

# Use with --bench-path
python -m evaluators.benchmarking.bench_ollama \
    --model llama3.2 \
    --bench-path ~/tools/bench.go
```

### Build for Different Platforms

```bash
# Build for Linux
GOOS=linux GOARCH=amd64 go build -o ollama-bench-linux bench.go

# Build for macOS
GOOS=darwin GOARCH=arm64 go build -o ollama-bench-mac bench.go

# Build for Windows
GOOS=windows GOARCH=amd64 go build -o ollama-bench.exe bench.go
```

### Using with Docker

```dockerfile
FROM golang:1.21-alpine

# Install dependencies
RUN apk add --no-cache python3 py3-pip curl

# Copy files
COPY . /app
WORKDIR /app

# Install Python packages
RUN pip3 install requests pyyaml

# Download bench.go
RUN curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go

# Build bench tool
RUN go build -o ollama-bench bench.go

CMD ["python3", "-m", "evaluators.cli.check_setup"]
```

## Support

If you encounter issues:

1. Run diagnostics: `python -m evaluators.cli.check_setup`
2. Check Ollama is running: `ollama list`
3. Verify Go works: `go version`
4. Test bench directly: `go run bench.go -model llama3.2 -epochs 1 -max-tokens 10`
5. Check the troubleshooting sections in `BENCHMARKING.md`

## Summary

Minimum requirements:
- ✅ Ollama installed
- ✅ Go installed
- ✅ bench.go downloaded
- ✅ Python packages installed

Quick setup:
```bash
./scripts/setup_bench.sh && python -m evaluators.cli.check_setup
```

You're ready to benchmark! 🚀
