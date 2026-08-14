#!/usr/bin/env python3
"""
Symbolic Calculus Engine & Interactive TUI
==========================================
Main executable entry point.

Usage:
  # Launch interactive TUI:
  python app.py
  python app.py --tui

  # Command Line Interface (CLI):
  python app.py "sin(x^2) / (x + 1)" --diff x --steps --plot
  python app.py "x^3 - 3*x^2 + 2" --tree --critical --roots
  python app.py "exp(2*x) * cos(x)" --order 2 --eval 1.5 --taylor 4
"""

import sys
from cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())
