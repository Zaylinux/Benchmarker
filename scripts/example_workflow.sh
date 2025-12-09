#!/bin/bash
# Example workflow: Complete evaluation of a model
#
# This script demonstrates a complete evaluation workflow:
# 1. Checks for required dependencies (python, bench tool)
# 2. Validates setup with check_setup
# 3. Queries the model on all tasks
# 4. Runs combined quality + performance evaluation
#
# Usage: ./scripts/example_workflow.sh [model_name]
# Example: ./scripts/example_workflow.sh llama3.2

set -e

# Configuration
MODEL=${1:-"llama3.2"}
OUTPUT_DIR="outputs"

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
    
    # Check for python
    if ! check_command python && ! check_command python3; then
        missing_deps+=("python")
    fi
    
    # Report missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "✗ Missing required dependencies: ${missing_deps[*]}"
        echo
        for dep in "${missing_deps[@]}"; do
            case "$dep" in
                python)
                    echo "Install Python:"
                    echo "  - Visit: https://www.python.org/downloads/"
                    echo "  - macOS: brew install python"
                    echo "  - Ubuntu/Debian: sudo apt-get install python3"
                    ;;
            esac
            echo
        done
        return 1
    fi
    
    return 0
}

#######################################
# Check if bench tool is available
# Globals:
#   None
# Returns:
#   0 if available, 1 otherwise
#######################################
check_bench_tool() {
    # Check if bench.go or ollama-bench binary exists
    if [ ! -f "bench.go" ] && [ ! -f "ollama-bench" ]; then
        echo "⚠️  Bench tool not found!"
        echo "Run: ./scripts/setup_bench.sh"
        echo
        read -p "Run setup now? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            if ! ./scripts/setup_bench.sh; then
                return 1
            fi
        else
            echo "Exiting. Run ./scripts/setup_bench.sh first."
            return 1
        fi
    fi
    return 0
}

#######################################
# Create output directory if needed
# Globals:
#   OUTPUT_DIR
# Returns:
#   0 on success
#######################################
setup_output_directory() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        echo "Creating output directory: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
    fi
    return 0
}

#######################################
# Run setup validation
# Globals:
#   None
# Returns:
#   0 on success, 1 on failure
#######################################
run_setup_check() {
    echo "Step 1: Checking setup..."
    if python -m evaluators.cli.check_setup; then
        echo "✓ Setup check passed"
        return 0
    else
        echo "✗ Setup check failed"
        return 1
    fi
}

#######################################
# Query the model on all tasks
# Arguments:
#   Model name
# Globals:
#   OUTPUT_DIR
# Returns:
#   0 on success, 1 on failure
#######################################
query_model() {
    local model=$1
    local output_file="${OUTPUT_DIR}/${model}_outputs.json"
    
    echo "Step 2: Querying model on all tasks..."
    echo "  Model: $model"
    echo "  Output: $output_file"
    
    if python -m evaluators.querying.query_ollama \
        --model "$model" \
        --out "$output_file"; then
        echo "✓ Model querying completed"
        return 0
    else
        echo "✗ Model querying failed"
        return 1
    fi
}

#######################################
# Run combined evaluation
# Arguments:
#   Model name
# Globals:
#   OUTPUT_DIR
# Returns:
#   0 on success, 1 on failure
#######################################
run_evaluation() {
    local model=$1
    local outputs_file="${OUTPUT_DIR}/${model}_outputs.json"
    local report_file="${OUTPUT_DIR}/${model}_combined_report.json"
    
    echo "Step 3: Running combined quality + performance evaluation..."
    echo "  Model: $model"
    echo "  Outputs: $outputs_file"
    echo "  Report: $report_file"
    
    if python -m evaluators.cli.evaluate_combined \
        --model "$model" \
        --outputs "$outputs_file" \
        --report "$report_file" \
        --bench-epochs 5 \
        --bench-max-tokens 100; then
        echo "✓ Evaluation completed"
        return 0
    else
        echo "✗ Evaluation failed"
        return 1
    fi
}

#######################################
# Print results summary
# Arguments:
#   Model name
# Globals:
#   OUTPUT_DIR
#######################################
print_summary() {
    local model=$1
    local report_file="${OUTPUT_DIR}/${model}_combined_report.json"
    
    echo
    echo "=========================================="
    echo "Evaluation complete!"
    echo "=========================================="
    echo "Model: $model"
    echo "Results saved to: $report_file"
    echo
    echo "View results:"
    echo "  cat $report_file | python -m json.tool"
}

#######################################
# Main function
#######################################
main() {
    echo "=========================================="
    echo "Complete Evaluation Workflow"
    echo "Model: $MODEL"
    echo "=========================================="
    echo
    
    # Check dependencies
    if ! check_dependencies; then
        error_exit "Please install missing dependencies and try again"
    fi
    
    # Check bench tool
    if ! check_bench_tool; then
        error_exit "Bench tool setup failed or was cancelled"
    fi
    
    # Setup output directory
    setup_output_directory
    echo
    
    # Run setup check
    if ! run_setup_check; then
        error_exit "Setup validation failed. Please fix issues and try again"
    fi
    echo
    
    # Query model
    if ! query_model "$MODEL"; then
        error_exit "Model querying failed"
    fi
    echo
    
    # Run evaluation
    if ! run_evaluation "$MODEL"; then
        error_exit "Evaluation failed"
    fi
    
    # Print summary
    print_summary "$MODEL"
}

# Run main function
main
