# Design Document: Repository Cleanup and Organization

## Overview

This design outlines a comprehensive cleanup and reorganization of the SLM Taskpack evaluation framework to make it more presentable, maintainable, and reusable for developers who want to fork the repository. The cleanup will focus on improving code quality, documentation consistency, project structure, and developer experience while preserving all existing functionality.

The approach follows these principles:
- **Non-breaking**: All existing functionality must continue to work
- **Incremental**: Changes can be applied progressively
- **Standards-based**: Follow Python PEP 8, markdown best practices, and common conventions
- **Developer-friendly**: Prioritize clarity and ease of use for new contributors

## Architecture

### Current State

The repository currently has:
- Python evaluation scripts in `evaluators/` directory
- Task definitions in `taskpacks/` directory
- Multiple documentation files in the root
- Shell scripts for setup and workflows
- Go-based benchmarking tool integration
- Multiple virtual environment directories (`.venv`, `venv`)
- Minimal `.gitignore` configuration

### Target State

The reorganized repository will have:
- Clean, well-documented Python code with type hints and docstrings
- Consistent documentation with proper formatting
- Comprehensive `.gitignore` for generated files
- Single virtual environment approach
- Organized scripts directory
- Clear dependency management with `requirements.txt`
- Licensing and contribution guidelines
- Automated code quality checks

### Directory Structure

```
slm-taskpack-evaluator/
├── .github/                    # GitHub-specific files
│   └── workflows/              # CI/CD workflows (future)
├── .kiro/                      # Kiro specs
│   └── specs/
├── .trunk/                     # Trunk linting configuration
├── docs/                       # Documentation
│   ├── GETTING_STARTED.md
│   ├── SETUP.md
│   ├── BENCHMARKING.md
│   ├── QUICK_REFERENCE.md
│   └── ARCHITECTURE.md
├── evaluators/                 # Python evaluation modules
│   ├── __init__.py
│   ├── core/                   # Core evaluation logic
│   │   ├── __init__.py
│   │   ├── metrics.py          # Scoring functions
│   │   ├── evaluator.py        # Main evaluation logic
│   │   └── loader.py           # Task loading utilities
│   ├── benchmarking/           # Performance benchmarking
│   │   ├── __init__.py
│   │   ├── bench_runner.py     # Bench tool wrapper
│   │   └── aggregator.py       # Metrics aggregation
│   ├── querying/               # Model querying
│   │   ├── __init__.py
│   │   ├── ollama_client.py    # Ollama API client
│   │   └── openai_client.py    # OpenAI-compatible client
│   ├── reporting/              # Report generation
│   │   ├── __init__.py
│   │   ├── json_reporter.py    # JSON output
│   │   └── markdown_reporter.py # Markdown tables
│   └── cli/                    # Command-line interfaces
│       ├── __init__.py
│       ├── evaluate.py         # Main evaluation CLI
│       ├── benchmark.py        # Benchmarking CLI
│       ├── compare.py          # Model comparison CLI
│       └── check_setup.py      # Setup validation CLI
├── scripts/                    # Shell scripts
│   ├── setup_bench.sh
│   ├── setup_benchstat.sh
│   └── example_workflow.sh
├── taskpacks/                  # Test data
│   ├── meta.yaml
│   ├── extraction/
│   ├── rag/
│   ├── reasoning/
│   ├── safety/
│   └── summarization/
├── tests/                      # Unit tests (future)
│   └── __init__.py
├── outputs/                    # Generated reports (gitignored)
├── .gitignore                  # Comprehensive ignore rules
├── .python-version             # Python version specification
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup (optional)
├── LICENSE                     # License file
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # Main documentation
```

## Components and Interfaces

### 1. Core Evaluation Module (`evaluators/core/`)

**Purpose**: Centralize evaluation logic and metrics calculation

**Components**:

- `metrics.py`: Pure functions for scoring
  - `token_f1(pred: str, gold: str) -> float`
  - `exact_match(pred: str, gold: str) -> bool`
  - `is_json_valid(pred: str) -> bool`
  - `calculate_category_score(category: str, tasks: List[Dict], outputs: Dict) -> float`

- `evaluator.py`: Main evaluation orchestration
  - `class Evaluator`: Manages evaluation workflow
  - `evaluate(outputs: Dict, tasks: Dict, weights: Dict) -> Dict`

- `loader.py`: Task and configuration loading
  - `load_tasks(root: str) -> Dict[str, List[Dict]]`
  - `load_meta(path: str) -> Dict`
  - `load_outputs(path: str) -> Dict`

### 2. Benchmarking Module (`evaluators/benchmarking/`)

**Purpose**: Wrap Ollama bench tool and aggregate performance metrics

**Components**:

- `bench_runner.py`: Execute bench tool
  - `class BenchRunner`: Manages bench execution
  - `find_bench_tool() -> Optional[Path]`
  - `run_benchmark(model: str, prompt: str, **kwargs) -> Dict`

- `aggregator.py`: Aggregate performance data
  - `aggregate_metrics(results: Dict) -> Dict`
  - `calculate_performance_score(metrics: Dict, targets: Dict) -> float`

### 3. Querying Module (`evaluators/querying/`)

**Purpose**: Abstract model querying interfaces

**Components**:

- `ollama_client.py`: Ollama-specific client
  - `class OllamaClient`: Native Ollama API
  - `query(model: str, prompt: str, **kwargs) -> str`

- `openai_client.py`: OpenAI-compatible client
  - `class OpenAIClient`: Generic OpenAI API
  - `query(model: str, prompt: str, **kwargs) -> str`

### 4. Reporting Module (`evaluators/reporting/`)

**Purpose**: Generate output reports in various formats

**Components**:

- `json_reporter.py`: JSON report generation
  - `class JSONReporter`
  - `generate_report(data: Dict, output_path: str)`

- `markdown_reporter.py`: Markdown table generation
  - `class MarkdownReporter`
  - `generate_comparison_table(results: List[Dict]) -> str`

### 5. CLI Module (`evaluators/cli/`)

**Purpose**: Command-line interfaces for all operations

**Components**:

- `evaluate.py`: Main evaluation CLI (replaces `evaluate.py`)
- `benchmark.py`: Benchmarking CLI (replaces `bench_ollama.py`)
- `compare.py`: Model comparison CLI (replaces `compare_models.py`)
- `check_setup.py`: Setup validation CLI

## Data Models

### Task Definition

```python
from typing import TypedDict, Optional

class Task(TypedDict):
    id: str
    input: str
    expected_output: str
    context: Optional[str]  # For RAG tasks
    category: str
```

### Evaluation Result

```python
class EvaluationResult(TypedDict):
    overall_score: float
    by_category: Dict[str, float]
    weights: Dict[str, float]
    metadata: Dict[str, Any]
```

### Benchmark Result

```python
class BenchmarkMetrics(TypedDict):
    avg_prefill_tokens_per_sec: float
    avg_generate_tokens_per_sec: float
    avg_load_time_ms: float
    sample_count: int
```

### Combined Report

```python
class CombinedReport(TypedDict):
    model: str
    composite_score: float
    quality: EvaluationResult
    performance: BenchmarkMetrics
    performance_checks: Dict[str, Dict]
    scoring_breakdown: Dict[str, float]
```

## Error Handling

### Error Categories

1. **Setup Errors**: Missing dependencies, tools not found
2. **Runtime Errors**: Model not available, API failures
3. **Data Errors**: Invalid task format, missing files
4. **Validation Errors**: Invalid configuration, bad parameters

### Error Handling Strategy

```python
class EvaluatorError(Exception):
    """Base exception for evaluator errors"""
    pass

class SetupError(EvaluatorError):
    """Raised when setup validation fails"""
    pass

class ModelError(EvaluatorError):
    """Raised when model operations fail"""
    pass

class DataError(EvaluatorError):
    """Raised when data loading/parsing fails"""
    pass
```

### Error Messages

All error messages should:
- Clearly describe what went wrong
- Provide actionable guidance for resolution
- Include relevant context (file paths, command suggestions)
- Use consistent formatting

Example:
```
Error: Bench tool not found

The Ollama bench tool is required for performance benchmarking.

To fix this:
  1. Run: ./scripts/setup_bench.sh
  2. Or manually download: curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go

For more help, see: docs/SETUP.md
```

## Documentation Structure

### README.md

- Project overview and purpose
- Quick start (3-5 commands)
- Key features
- Links to detailed documentation
- License and contribution info

### docs/GETTING_STARTED.md

- 5-minute quick start guide
- Step-by-step setup
- First evaluation walkthrough
- Common workflows
- Troubleshooting basics

### docs/SETUP.md

- Detailed installation instructions
- Platform-specific guidance
- Dependency management
- Verification steps
- Advanced configuration

### docs/BENCHMARKING.md

- Comprehensive usage guide
- All CLI options explained
- Performance tuning
- Interpreting results
- Advanced scenarios

### docs/QUICK_REFERENCE.md

- Command cheat sheet
- Common patterns
- Quick lookup table

### docs/ARCHITECTURE.md

- System design
- Component interactions
- Data flow diagrams
- Extension points

### CONTRIBUTING.md

- How to contribute
- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

## Code Quality Standards

### Python Style

- Follow PEP 8 strictly
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings (Google style) for all public functions
- Use f-strings for string formatting
- Prefer pathlib over os.path

### Documentation Style

- Use consistent markdown formatting
- Specify language for all code blocks
- Use tables with consistent alignment
- Keep line length reasonable (80-100 chars)
- Use relative links for internal references

### Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

### Import Organization

```python
# Standard library
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import yaml
import requests

# Local
from evaluators.core import metrics
from evaluators.core.loader import load_tasks
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Markdown formatting compliance

*For any* markdown file in the repository, all fenced code blocks should specify a language identifier, and all tables should use consistent column alignment.

**Validates: Requirements 2.3, 2.4**

### Property 2: Python code standards compliance

*For any* Python file in the evaluators directory, the file should include docstrings for all public modules, classes, and functions, follow PEP 8 style guidelines, and include type hints for all function parameters and return values.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 3: Gitignore coverage

*For any* generated file type (outputs, virtual environments, compiled binaries, temporary files, cache files, or IDE-specific files), the .gitignore file should contain patterns that exclude those files from version control.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 4: Consistent naming conventions

*For any* Python file, the filename should use snake_case, and for any shell script, the filename should use kebab-case. Additionally, for any constant in Python code, the name should use UPPER_CASE.

**Validates: Requirements 6.1, 6.4**

### Property 5: Shell script structure

*For any* shell script in the scripts directory, the script should define functions for reusable logic and include checks for required commands before execution.

**Validates: Requirements 7.4, 7.5**

## Testing Strategy

### Overview

The repository cleanup will be validated through a combination of:
1. **Automated linting and validation** - Using existing tools to verify code quality
2. **Unit tests** - Testing specific examples of correct structure
3. **Property-based tests** - Verifying universal properties across all files
4. **Manual review** - For subjective quality aspects

### Unit Testing Approach

Unit tests will verify specific examples and edge cases:

- **Directory structure tests**: Verify expected directories exist with correct contents
- **File existence tests**: Check that required files (LICENSE, CONTRIBUTING.md, requirements.txt) exist
- **Configuration tests**: Verify specific configuration files have expected content
- **Documentation tests**: Check that specific documentation sections exist

Example unit tests:
- Test that `scripts/` directory contains all .sh files
- Test that `requirements.txt` exists and contains valid package specifications
- Test that README.md contains links to all documentation files
- Test that LICENSE file exists
- Test that .gitignore contains `outputs/` pattern

### Property-Based Testing Approach

Property-based tests will verify universal rules across all files of a given type. We will use **pytest** with **Hypothesis** for property-based testing in Python.

**Configuration**: Each property-based test should run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Test Organization**: Property-based tests will be located in `tests/properties/` directory, organized by the type of property being tested:
- `test_markdown_properties.py` - Markdown formatting properties
- `test_python_properties.py` - Python code quality properties
- `test_gitignore_properties.py` - Gitignore coverage properties
- `test_naming_properties.py` - Naming convention properties
- `test_script_properties.py` - Shell script structure properties

**Property Test Implementations**:

Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document using this format: `# Feature: repo-cleanup, Property {number}: {property_text}`

1. **Property 1 Test** (Markdown formatting):
   - Generate: List all markdown files in repository
   - Test: Parse each file and verify all code blocks have language specifiers and tables have consistent alignment
   - Tag: `# Feature: repo-cleanup, Property 1: Markdown formatting compliance`

2. **Property 2 Test** (Python code standards):
   - Generate: List all Python files in evaluators/
   - Test: Parse AST and verify docstrings exist, run flake8 for PEP 8, check type hints with mypy
   - Tag: `# Feature: repo-cleanup, Property 2: Python code standards compliance`

3. **Property 3 Test** (Gitignore coverage):
   - Generate: List of file patterns that should be ignored (outputs/*, venv/, *.pyc, etc.)
   - Test: Verify each pattern is covered by .gitignore rules
   - Tag: `# Feature: repo-cleanup, Property 3: Gitignore coverage`

4. **Property 4 Test** (Naming conventions):
   - Generate: List all Python files and shell scripts
   - Test: Verify Python files use snake_case, scripts use kebab-case, constants use UPPER_CASE
   - Tag: `# Feature: repo-cleanup, Property 4: Consistent naming conventions`

5. **Property 5 Test** (Shell script structure):
   - Generate: List all shell scripts in scripts/
   - Test: Parse scripts and verify function definitions exist and dependency checks are present
   - Tag: `# Feature: repo-cleanup, Property 5: Shell script structure`

### Automated Linting

The project will use existing `.trunk` configuration for automated code quality checks:

- **Python**: flake8, black, mypy, isort
- **Markdown**: markdownlint
- **YAML**: yamllint
- **Shell**: shellcheck

These tools will be run as part of the development workflow and can be integrated into CI/CD pipelines.

### Testing Workflow

1. **During Development**:
   - Run linters before committing: `trunk check`
   - Run unit tests: `pytest tests/unit/`
   - Run property tests: `pytest tests/properties/`

2. **Before Pull Request**:
   - Run full test suite: `pytest`
   - Run linters on all files: `trunk check --all`
   - Manually review documentation for clarity

3. **Continuous Integration** (future):
   - Automated test execution on all PRs
   - Linting checks as required status
   - Documentation build verification

### Test Coverage Goals

- **Unit tests**: Cover all specific requirements (examples)
- **Property tests**: Cover all universal rules (properties)
- **Linting**: Catch style and formatting issues
- **Manual review**: Ensure subjective quality aspects

### Testing Tools and Dependencies

**Required**:
- pytest (testing framework)
- hypothesis (property-based testing)
- flake8 (PEP 8 linting)
- mypy (type checking)
- black (code formatting)

**Optional**:
- pytest-cov (coverage reporting)
- pytest-xdist (parallel test execution)

These will be specified in `requirements-dev.txt`.

## Implementation Phases

### Phase 1: Foundation (Non-breaking)

1. Add missing files (LICENSE, CONTRIBUTING.md, requirements.txt)
2. Improve .gitignore
3. Add type hints to existing code
4. Add docstrings to existing code
5. Fix markdown formatting issues

### Phase 2: Reorganization (Potentially breaking)

1. Create new directory structure
2. Refactor Python code into modules
3. Move scripts to scripts/ directory
4. Move documentation to docs/ directory
5. Update import paths

### Phase 3: Enhancement

1. Add comprehensive tests
2. Set up CI/CD
3. Add more documentation
4. Create examples and tutorials

### Phase 4: Polish

1. Final code review
2. Documentation review
3. Performance optimization
4. Release preparation

## Migration Strategy

To ensure existing users can continue using the repository:

1. **Maintain backward compatibility**: Keep old script locations as symlinks initially
2. **Provide migration guide**: Document how to update existing workflows
3. **Version the changes**: Use git tags to mark major reorganization
4. **Deprecation warnings**: Add warnings to old script locations
5. **Gradual transition**: Allow time for users to adapt

## Success Criteria

The cleanup will be considered successful when:

1. All linting checks pass without warnings
2. All property-based tests pass
3. All unit tests pass
4. Documentation is complete and consistent
5. New contributors can set up and understand the project in < 30 minutes
6. Code coverage is > 80% for core modules
7. All existing functionality continues to work

## Future Enhancements

After the initial cleanup:

1. **CI/CD Pipeline**: Automated testing and deployment
2. **Package Distribution**: Publish to PyPI for easy installation
3. **Docker Support**: Containerized evaluation environment
4. **Web Interface**: Browser-based evaluation dashboard
5. **Plugin System**: Allow custom metrics and evaluators
6. **Performance Optimization**: Parallel evaluation, caching
7. **Extended Documentation**: Video tutorials, blog posts
8. **Community Building**: Discord/Slack, regular releases

## References

- PEP 8: https://peps.python.org/pep-0008/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
- Hypothesis Documentation: https://hypothesis.readthedocs.io/
- Trunk Documentation: https://docs.trunk.io/
