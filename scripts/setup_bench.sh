#!/bin/bash
# Setup script for Ollama bench tool
# Downloads bench.go and optionally builds it
#
# This script:
# 1. Checks for required dependencies (curl, go)
# 2. Downloads the Ollama bench.go file
# 3. Initializes Go modules
# 4. Optionally builds the binary
#
# Usage: ./scripts/setup_bench.sh

set -e

# Configuration
BENCH_URL="https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go"
BENCH_FILE="bench.go"

#######################################
# Print error message and exit
# Arguments:
#   Error message
# Returns:
#   Exit code 1
#######################################
error_exit() {
    echo "✗ Error: $1" >&2
    exit 1
}

#######################################
# Check if a command exists
# Arguments:
#   Command name
# Returns:
#   0 if exists, 1 otherwise
#######################################
check_command() {
    command -v "$1" &> /dev/null
}

#######################################
# Check for required dependencies
# Globals:
#   None
# Returns:
#   Exit code 1 if dependencies missing
#######################################
check_dependencies() {
    local missing_deps=()
    
    # Check for curl
    if ! check_command curl; then
        missing_deps+=("curl")
    fi
    
    # Check for go
    if ! check_command go; then
        missing_deps+=("go")
    fi
    
    # Report missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "✗ Missing required dependencies: ${missing_deps[*]}"
        echo
        for dep in "${missing_deps[@]}"; do
            case "$dep" in
                curl)
                    echo "Install curl:"
                    echo "  - macOS: brew install curl"
                    echo "  - Ubuntu/Debian: sudo apt-get install curl"
                    echo "  - Fedora: sudo dnf install curl"
                    ;;
                go)
                    echo "Install Go:"
                    echo "  - Visit: https://go.dev/doc/install"
                    echo "  - macOS: brew install go"
                    echo "  - Ubuntu: sudo snap install go --classic"
                    ;;
            esac
            echo
        done
        return 1
    fi
    
    return 0
}

#######################################
# Download bench.go file
# Globals:
#   BENCH_URL, BENCH_FILE
# Returns:
#   0 on success, 1 on failure
#######################################
download_bench() {
    # Check if bench.go already exists
    if [ -f "$BENCH_FILE" ]; then
        echo "✓ bench.go already exists"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping download"
            return 0
        fi
    fi
    
    echo "Downloading bench.go..."
    if curl -fsSL "$BENCH_URL" -o "$BENCH_FILE"; then
        echo "✓ Downloaded bench.go"
        return 0
    else
        echo "✗ Failed to download bench.go"
        return 1
    fi
}

#######################################
# Initialize Go modules
# Globals:
#   None
# Returns:
#   0 on success, 1 on failure
#######################################
setup_go_modules() {
    # Initialize Go modules if needed
    if [ ! -f "go.mod" ]; then
        echo "Initializing Go modules..."
        go mod init benchmarker 2>/dev/null || true
        echo "Getting Ollama API dependency..."
        if ! go get github.com/ollama/ollama/api@latest; then
            echo "✗ Failed to get dependencies"
            return 1
        fi
        go mod tidy
        echo "✓ Go modules initialized"
    else
        echo "✓ Go modules already initialized"
        echo "Updating dependencies..."
        if ! go get github.com/ollama/ollama/api@latest; then
            echo "✗ Failed to update dependencies"
            return 1
        fi
        go mod tidy
    fi
    echo
    return 0
}

#######################################
# Build the ollama-bench binary
# Globals:
#   BENCH_FILE
# Returns:
#   0 on success, 1 on failure
#######################################
build_binary() {
    read -p "Build binary (ollama-bench)? (Y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "Building ollama-bench..."
        if go build -o ollama-bench "$BENCH_FILE"; then
            echo "✓ Built ollama-bench binary"
            echo
            echo "You can now use either:"
            echo "  1. ./ollama-bench -model <model> -epochs 3"
            echo "  2. go run bench.go -model <model> -epochs 3"
            return 0
        else
            echo "✗ Build failed. Check errors above."
            echo "You can still try:"
            echo "  go run bench.go -model <model> -epochs 3"
            return 1
        fi
    else
        echo "Skipping build. You can build later with:"
        echo "  go build -o ollama-bench bench.go"
        echo
        echo "Or use directly with:"
        echo "  go run bench.go -model <model> -epochs 3"
        return 0
    fi
}

#######################################
# Print usage instructions
# Globals:
#   None
#######################################
print_usage() {
    echo
    echo "=========================================="
    echo "Setup complete!"
    echo "=========================================="
    echo
    echo "Test the bench tool:"
    echo "  go run bench.go -model llama3.2 -epochs 1 -max-tokens 10"
    echo
    echo "Or run the full evaluation:"
    echo "  python -m evaluators.benchmarking.bench_ollama --model llama3.2"
}

#######################################
# Main function
#######################################
main() {
    echo "=========================================="
    echo "Ollama Bench Setup"
    echo "=========================================="
    echo
    
    # Check dependencies first
    if ! check_dependencies; then
        error_exit "Please install missing dependencies and try again"
    fi
    
    echo "✓ All dependencies found"
    echo "  - curl: $(curl --version | head -n 1)"
    echo "  - go: $(go version)"
    echo
    
    # Download bench.go
    if ! download_bench; then
        error_exit "Failed to download bench.go"
    fi
    echo
    
    # Setup Go modules
    if ! setup_go_modules; then
        error_exit "Failed to setup Go modules"
    fi
    
    # Build binary (optional)
    build_binary
    
    # Print usage instructions
    print_usage
}

# Run main function
main
