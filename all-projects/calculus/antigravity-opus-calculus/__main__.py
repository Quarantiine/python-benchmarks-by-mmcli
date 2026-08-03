#!/usr/bin/env python3
"""Entry point for the Symbolic Calculus Engine TUI."""

try:
    from .tui import run_tui
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tui import run_tui

run_tui()
