#!/bin/bash
# Install and setup benchstat tool
#
# This script:
# 1. Checks for required dependencies (go)
# 2. Checks if benchstat is already installed
# 3. Installs or updates benchstat
#
# Usage: ./scripts/setup_benchstat.sh

set -e

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
    # Check for go
    if ! check_command go; then
        echo "✗ Go is not installed"
        echo
        echo "Install Go:"
        echo "  - Visit: https://go.dev/doc/install"
        echo "  - macOS: brew install go"
        echo "  - Ubuntu: sudo snap install go --classic"
        echo "  - Fedora: sudo dnf install golang"
        return 1
    fi
    
    echo "✓ Go is installed: $(go version)"
    return 0
}

#######################################
# Check if benchstat is already installed
# Globals:
#   None
# Returns:
#   0 if should proceed, 1 if should skip
#######################################
check_existing_installation() {
    if check_command benchstat; then
        echo "✓ benchstat is already installed"
        benchstat -h 2>&1 | head -n 1
        echo
        read -p "Reinstall/update? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping installation"
            return 1
        fi
    fi
    return 0
}

#######################################
# Install benchstat tool
# Globals:
#   None
# Returns:
#   0 on success, 1 on failure
#######################################
install_benchstat() {
    echo "Installing benchstat..."
    
    if go install golang.org/x/perf/cmd/benchstat@latest; then
        echo "✓ benchstat installed"
        
        # Verify installation
        if check_command benchstat; then
            echo "✓ benchstat is available in PATH"
        else
            echo "⚠️  benchstat installed but not in PATH"
            echo "Add Go bin directory to PATH:"
            echo "  export PATH=\$PATH:\$(go env GOPATH)/bin"
        fi
        return 0
    else
        echo "✗ Installation failed"
        return 1
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
    echo "Setup Complete!"
    echo "=========================================="
    echo
    echo "Usage examples:"
    echo
    echo "1. Run bench and save output:"
    echo "   python -m evaluators.benchmarking.bench_benchstat --models qwen2.5 --output results.bench"
    echo
    echo "2. Analyze with benchstat:"
    echo "   benchstat results.bench"
    echo
    echo "3. Compare two models:"
    echo "   python -m evaluators.benchmarking.bench_benchstat --models qwen2.5,llama3.2 --output compare.bench"
    echo "   benchstat -col /name compare.bench"
    echo
    echo "4. Compare two runs:"
    echo "   benchstat old.bench new.bench"
}

#######################################
# Main function
#######################################
main() {
    echo "=========================================="
    echo "Benchstat Setup"
    echo "=========================================="
    echo
    
    # Check dependencies
    if ! check_dependencies; then
        error_exit "Please install Go and try again"
    fi
    echo
    
    # Check existing installation
    if ! check_existing_installation; then
        # User chose to skip installation
        print_usage
        exit 0
    fi
    
    # Install benchstat
    if ! install_benchstat; then
        error_exit "Failed to install benchstat"
    fi
    
    # Print usage instructions
    print_usage
}

# Run main function
main
