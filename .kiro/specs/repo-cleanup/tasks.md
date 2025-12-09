# Implementation Plan

- [x] 1. Set up project infrastructure and configuration files
  - Create requirements.txt with pinned dependencies (requests, pyyaml, pytest, hypothesis, flake8, mypy, black)
  - Create requirements-dev.txt for development dependencies
  - Create .python-version file specifying Python 3.7+
  - Create LICENSE file (choose appropriate open source license)
  - Create CONTRIBUTING.md with contribution guidelines
  - _Requirements: 4.1, 4.2, 4.5, 10.1, 10.2, 10.4_

- [x] 2. Improve .gitignore configuration
  - Add patterns for output files (outputs/, *.json in root, *.bench)
  - Add patterns for virtual environments (.venv/, venv/, env/)
  - Add patterns for Python cache (__pycache__/, *.pyc, *.pyo, *.pyd, .Python)
  - Add patterns for compiled binaries (ollama-bench, bench, *.exe)
  - Add patterns for IDE files (.vscode/, .idea/, *.swp, .DS_Store)
  - Add patterns for temporary files (*.tmp, *.log, .pytest_cache/)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 3. Fix markdown documentation formatting issues
  - Add language specifiers to all code blocks in README.md
  - Add language specifiers to all code blocks in GETTING_STARTED.md
  - Add language specifiers to all code blocks in SETUP.md
  - Add language specifiers to all code blocks in BENCHMARKING.md
  - Add language specifiers to all code blocks in ARCHITECTURE.md
  - Fix table column alignment in all documentation files
  - _Requirements: 2.3, 2.4_

- [ ]* 3.1 Write property test for markdown formatting
  - **Property 1: Markdown formatting compliance**
  - **Validates: Requirements 2.3, 2.4**

- [x] 4. Reorganize directory structure
  - Create docs/ directory and move all .md files except README.md
  - Create scripts/ directory and move all .sh files
  - Create evaluators/core/ directory for core evaluation logic
  - Create evaluators/benchmarking/ directory for benchmarking code
  - Create evaluators/querying/ directory for model querying code
  - Create evaluators/reporting/ directory for report generation
  - Create evaluators/cli/ directory for CLI scripts
  - Create tests/ directory with tests/unit/ and tests/properties/ subdirectories
  - Update all relative paths in moved files
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 5. Refactor core evaluation logic into modules
  - Create evaluators/core/__init__.py
  - Create evaluators/core/metrics.py with token_f1, exact_match, is_json_valid functions
  - Add type hints to all functions in metrics.py
  - Add docstrings to all functions in metrics.py
  - Create evaluators/core/evaluator.py with Evaluator class and evaluate function
  - Create evaluators/core/loader.py with load_tasks, load_meta, load_outputs functions
  - Extract scoring logic from evaluate.py into core modules
  - _Requirements: 3.1, 3.2, 3.3, 8.1_

- [ ]* 5.1 Write property test for Python code standards
  - **Property 2: Python code standards compliance**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 6. Refactor benchmarking code into modules
  - Create evaluators/benchmarking/__init__.py
  - Create evaluators/benchmarking/bench_runner.py with BenchRunner class
  - Move find_bench_script and run_ollama_bench to bench_runner.py
  - Add type hints and docstrings to all functions
  - Create evaluators/benchmarking/aggregator.py with aggregate_metrics function
  - Move aggregation logic from bench_ollama.py to aggregator.py
  - _Requirements: 3.1, 3.2, 3.3, 8.1_

- [x] 7. Refactor querying code into modules
  - Create evaluators/querying/__init__.py
  - Create evaluators/querying/ollama_client.py with OllamaClient class
  - Extract Ollama querying logic from query_ollama.py
  - Create evaluators/querying/openai_client.py with OpenAIClient class
  - Extract OpenAI querying logic from query_model.py
  - Add type hints and docstrings to all classes and methods
  - _Requirements: 3.1, 3.2, 3.3, 8.1_

- [x] 8. Refactor reporting code into modules
  - Create evaluators/reporting/__init__.py
  - Create evaluators/reporting/json_reporter.py with JSONReporter class
  - Create evaluators/reporting/markdown_reporter.py with MarkdownReporter class
  - Extract report generation logic from compare_models.py
  - Add type hints and docstrings to all classes and methods
  - _Requirements: 3.1, 3.2, 3.3, 8.1_

- [x] 9. Create new CLI entry points
  - Create evaluators/cli/__init__.py
  - Create evaluators/cli/evaluate.py (refactored from evaluate.py)
  - Create evaluators/cli/benchmark.py (refactored from bench_ollama.py)
  - Create evaluators/cli/compare.py (refactored from compare_models.py)
  - Move evaluators/check_setup.py to evaluators/cli/check_setup.py
  - Update all CLI scripts to use new module structure
  - Ensure all CLI scripts have proper argument parsing and help text
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 10. Update shell scripts with better structure
  - Add function definitions to setup_bench.sh for reusable logic
  - Add dependency checks to setup_bench.sh (check for curl, go)
  - Add function definitions to setup_benchstat.sh
  - Add dependency checks to setup_benchstat.sh
  - Add function definitions to example_workflow.sh
  - Add dependency checks to example_workflow.sh
  - Add informative comments to all shell scripts
  - Ensure all scripts exit with appropriate error codes
  - _Requirements: 7.4, 7.5_

- [ ]* 10.1 Write property test for shell script structure
  - **Property 5: Shell script structure**
  - **Validates: Requirements 7.4, 7.5**

- [ ] 11. Standardize file naming conventions
  - Verify all Python files in evaluators/ use snake_case
  - Rename any files that don't follow snake_case convention
  - Verify all shell scripts use kebab-case
  - Rename any scripts that don't follow kebab-case convention
  - Update all imports and references to renamed files
  - _Requirements: 6.1_

- [ ]* 11.1 Write property test for naming conventions
  - **Property 4: Consistent naming conventions**
  - **Validates: Requirements 6.1, 6.4**

- [ ] 12. Add comprehensive error handling
  - Create evaluators/core/exceptions.py with custom exception classes
  - Add EvaluatorError, SetupError, ModelError, DataError classes
  - Update all modules to use custom exceptions
  - Improve error messages with actionable guidance
  - Add try-except blocks with informative error messages in CLI scripts
  - _Requirements: 3.4_

- [ ] 13. Update README.md
  - Simplify overview section with clear project purpose
  - Add quick start section with 3-5 commands
  - Add links to all documentation in docs/ directory
  - Add license badge and information
  - Add contribution guidelines link
  - Add contact/support information
  - Remove redundant content that's now in docs/
  - _Requirements: 2.5, 10.4, 10.5_

- [ ] 14. Create backward compatibility layer
  - Create symlinks from old script locations to new locations in scripts/
  - Add deprecation warnings to old script locations
  - Create migration guide in docs/MIGRATION.md
  - Document all breaking changes and how to update
  - _Requirements: Migration strategy from design_

- [ ] 15. Set up testing infrastructure
  - Create tests/__init__.py
  - Create tests/unit/__init__.py for unit tests
  - Create tests/properties/__init__.py for property-based tests
  - Create pytest.ini configuration file
  - Configure pytest to run with minimum 100 iterations for property tests
  - _Requirements: Testing strategy from design_

- [ ]* 15.1 Write unit tests for directory structure
  - Test that expected directories exist (docs/, scripts/, evaluators/core/, etc.)
  - Test that scripts/ contains all .sh files
  - Test that docs/ contains all documentation files
  - _Requirements: 1.1, 1.3_

- [ ]* 15.2 Write unit tests for required files
  - Test that LICENSE file exists
  - Test that CONTRIBUTING.md exists
  - Test that requirements.txt exists and is valid
  - Test that .gitignore exists
  - Test that README.md exists
  - _Requirements: 4.1, 10.1, 10.2_

- [ ]* 15.3 Write unit tests for configuration files
  - Test that requirements.txt contains expected packages
  - Test that .python-version specifies Python 3.7+
  - Test that .gitignore contains outputs/ pattern
  - _Requirements: 4.1, 4.2, 5.1_

- [ ]* 15.4 Write property test for gitignore coverage
  - **Property 3: Gitignore coverage**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 16. Run linting and fix issues
  - Run flake8 on all Python files and fix PEP 8 violations
  - Run mypy on all Python files and fix type hint issues
  - Run black on all Python files to format code
  - Run markdownlint on all documentation and fix issues
  - Run shellcheck on all shell scripts and fix issues
  - Run trunk check --all and fix remaining issues
  - _Requirements: 3.2, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 17. Final verification and documentation
  - Run full test suite and ensure all tests pass
  - Verify all linting checks pass
  - Test setup process from scratch in clean environment
  - Review all documentation for accuracy and completeness
  - Update ARCHITECTURE.md to reflect new structure
  - Create release notes documenting all changes
  - _Requirements: All requirements_

- [ ] 18. Checkpoint - Ensure all tests pass, ask the user if questions arise
