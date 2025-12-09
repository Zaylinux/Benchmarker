# Contributing to SLM Taskpack Evaluator

Thank you for your interest in contributing to the SLM Taskpack Evaluator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes and test them
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/slm-taskpack-evaluator.git
   cd slm-taskpack-evaluator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Verify your setup:
   ```bash
   python evaluators/check_setup.py
   ```

## Making Changes

### Branch Naming

Use descriptive branch names that indicate the purpose of your changes:

- `feature/add-new-metric` - For new features
- `fix/evaluation-bug` - For bug fixes
- `docs/update-readme` - For documentation updates
- `refactor/cleanup-code` - For code refactoring

### Commit Messages

Write clear, concise commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Provide additional context in the body if needed
- Reference issue numbers when applicable

Example:
```
Add token-level F1 score metric

Implements a new metric for calculating F1 score at the token level,
which provides more granular evaluation than exact match.

Fixes #123
```

## Code Style Guidelines

### Python Code

We follow PEP 8 style guidelines with some specific conventions:

- **Line length**: Maximum 100 characters
- **Imports**: Organized in three groups (standard library, third-party, local)
- **Naming conventions**:
  - Files: `snake_case.py`
  - Classes: `PascalCase`
  - Functions: `snake_case()`
  - Constants: `UPPER_CASE`
  - Private: `_leading_underscore`

### Type Hints

All function signatures must include type hints:

```python
def calculate_score(predictions: List[str], gold: List[str]) -> float:
    """Calculate the average score across predictions."""
    pass
```

### Docstrings

Use Google-style docstrings for all public modules, classes, and functions:

```python
def token_f1(pred: str, gold: str) -> float:
    """Calculate token-level F1 score between prediction and gold standard.
    
    Args:
        pred: The predicted output string
        gold: The gold standard output string
        
    Returns:
        F1 score as a float between 0.0 and 1.0
        
    Example:
        >>> token_f1("hello world", "hello there")
        0.5
    ```
    pass
```

### Code Formatting

Before committing, run the following tools:

```bash
# Format code with black
black evaluators/

# Sort imports with isort
isort evaluators/

# Check style with flake8
flake8 evaluators/

# Check types with mypy
mypy evaluators/
```

Or use trunk to run all checks:

```bash
trunk check
```

## Testing Requirements

### Unit Tests

- Write unit tests for all new functions and classes
- Place tests in the `tests/unit/` directory
- Use descriptive test names that explain what is being tested
- Aim for high code coverage (>80%)

Example:
```python
def test_token_f1_identical_strings():
    """Test that identical strings have F1 score of 1.0."""
    assert token_f1("hello world", "hello world") == 1.0
```

### Property-Based Tests

- Write property-based tests for universal properties
- Place tests in the `tests/properties/` directory
- Configure tests to run at least 100 iterations
- Tag tests with the property they validate

Example:
```python
from hypothesis import given, strategies as st

# Feature: repo-cleanup, Property 2: Python code standards compliance
@given(st.text())
def test_function_has_docstring(code: str):
    """Test that all functions have docstrings."""
    # Test implementation
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run property tests only
pytest tests/properties/

# Run with coverage
pytest --cov=evaluators
```

## Submitting Changes

### Pull Request Process

1. Ensure all tests pass locally
2. Run linting and formatting tools
3. Update documentation if needed
4. Push your changes to your fork
5. Create a pull request with a clear description
6. Wait for review and address any feedback

### Pull Request Template

When creating a pull request, include:

- **Description**: What changes does this PR make?
- **Motivation**: Why are these changes needed?
- **Testing**: How have you tested these changes?
- **Related Issues**: Link to any related issues
- **Checklist**:
  - [ ] Tests pass locally
  - [ ] Code follows style guidelines
  - [ ] Documentation updated
  - [ ] No breaking changes (or documented if necessary)

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

### Feature Requests

When requesting features, include:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if applicable)
- Potential impact on existing functionality

## Questions and Support

If you have questions or need help:

- Check the documentation in the `docs/` directory
- Search existing issues on GitHub
- Create a new issue with the "question" label
- Reach out to maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to SLM Taskpack Evaluator!
