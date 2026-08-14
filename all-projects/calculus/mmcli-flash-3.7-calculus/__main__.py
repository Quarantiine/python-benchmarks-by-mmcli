"""
Module execution entry point (python -m calculus or python .).
"""

import sys
from cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
