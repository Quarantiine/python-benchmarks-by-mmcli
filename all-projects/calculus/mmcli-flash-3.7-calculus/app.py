"""
Main Application Entry Point
============================
Launches CLI commands or full-screen interactive TUI.
"""

import sys
from cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
