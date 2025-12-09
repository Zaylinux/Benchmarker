#!/usr/bin/env python3
"""
Legacy wrapper for check_setup.py - redirects to evaluators.cli.check_setup

This file is maintained for backward compatibility.
New code should use: python3 -m evaluators.cli.check_setup
"""

import os
import sys
import warnings

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Show deprecation warning
warnings.warn(
    "evaluators/check_setup.py is deprecated. Use 'python3 -m evaluators.cli.check_setup' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import and run the new CLI
from evaluators.cli.check_setup import main  # noqa: E402

if __name__ == "__main__":
    main()
