#!/usr/bin/env python3
"""
Setup validation CLI for checking environment configuration.

This script verifies that all required tools and dependencies are properly
installed and configured for running evaluations and benchmarks.
"""

import os
import subprocess
import sys


def check_command(cmd: str, name: str, min_version: str = None) -> bool:
    """
    Check if a command exists and optionally verify version.

    Args:
        cmd: Command to check
        name: Human-readable name for the command
        min_version: Optional minimum version requirement (not currently enforced)

    Returns:
        True if command is available, False otherwise
    """
    try:
        result = subprocess.run(
            [cmd, "--version"], capture_output=True, text=True, timeout=5
        )
        version_output = result.stdout + result.stderr
        print(f"✓ {name} is installed")
        if version_output:
            first_line = version_output.split("\n")[0]
            print(f"  Version: {first_line}")
        return True
    except FileNotFoundError:
        print(f"✗ {name} is NOT installed")
        return False
    except Exception as e:
        print(f"? {name} check failed: {e}")
        return False


def check_go() -> bool:
    """
    Check if Go is installed.

    Returns:
        True if Go is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["go", "version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Go is installed: {version}")
            return True
        else:
            print("✗ Go is NOT installed")
            return False
    except FileNotFoundError:
        print("✗ Go is NOT installed")
        return False
    except Exception as e:
        print(f"? Go check failed: {e}")
        return False


def check_bench_script() -> bool:
    """
    Check if bench.go script or pre-built binary is available.

    Returns:
        True if bench tool is found, False otherwise
    """
    locations = [
        ("./ollama-bench", "Pre-built binary"),
        ("./bench.go", "Go script (current dir)"),
        ("./bench/bench.go", "Go script (bench/ dir)"),
    ]

    for path, desc in locations:
        if os.path.exists(path):
            print(f"✓ Bench tool found: {desc} at {path}")
            return True

    print("✗ Bench script not found")
    print(
        "  Download from: https://github.com/ollama/ollama/blob/main/cmd/bench/bench.go"
    )
    return False


def check_python_packages() -> bool:
    """
    Check for required Python packages.

    Returns:
        True if all required packages are installed, False otherwise
    """
    packages = ["requests", "yaml"]
    all_ok = True

    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✓ Python package '{pkg}' is installed")
        except ImportError:
            print(f"✗ Python package '{pkg}' is NOT installed")
            all_ok = False

    return all_ok


def main() -> None:
    """
    Main entry point for the setup check CLI.

    Runs all validation checks and reports results.
    Exits with status code 1 if any checks fail.
    """
    print("=" * 60)
    print("SETUP CHECK")
    print("=" * 60)
    print()

    checks = []

    print("Checking Python...")
    checks.append(check_command(sys.executable, "Python"))
    print()

    print("Checking Ollama...")
    checks.append(check_command("ollama", "Ollama"))
    print()

    print("Checking Go...")
    checks.append(check_go())
    print()

    print("Checking Bench Script...")
    checks.append(check_bench_script())
    print()

    print("Checking Python packages...")
    checks.append(check_python_packages())
    print()

    print("=" * 60)
    if all(checks):
        print("✓ All checks passed! You're ready to benchmark.")
    else:
        print("✗ Some checks failed. Please install missing components.")
        print()
        print("Installation instructions:")
        print("- Ollama: https://ollama.ai/download")
        print("- Go: https://go.dev/doc/install")
        print(
            "- Bench script: curl -O https://raw.githubusercontent.com/ollama/ollama/main/cmd/bench/bench.go"
        )
        print("- Python packages: pip install requests pyyaml")
        sys.exit(1)


if __name__ == "__main__":
    main()
