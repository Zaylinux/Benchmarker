#!/bin/bash
# Fix Go modules for bench.go

echo "=========================================="
echo "Fixing Go Modules for bench.go"
echo "=========================================="
echo

# Check if bench.go exists
if [ ! -f "bench.go" ]; then
    echo "✗ bench.go not found"
    echo "Run: ./scripts/setup_bench.sh"
    exit 1
fi

# Initialize Go modules
echo "Initializing Go modules..."
go mod init benchmarker 2>/dev/null || echo "go.mod already exists"

echo "Getting Ollama API dependency..."
go get github.com/ollama/ollama/api@latest

echo "Tidying modules..."
go mod tidy

echo
echo "✓ Go modules fixed!"
echo
echo "Now you can:"
echo "  1. Build: go build -o ollama-bench bench.go"
echo "  2. Run: go run bench.go -model llama3.2 -epochs 1"
echo "  3. Use Python wrapper: python -m evaluators.benchmarking.bench_ollama --model llama3.2"
