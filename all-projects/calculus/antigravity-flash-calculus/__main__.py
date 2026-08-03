"""Main entry point for running Antigravity Calculus TUI application."""

import sys
from tui.app import CalculusTUIApp

if __name__ == "__main__":
    demo_mode = "--demo" in sys.argv or not sys.stdin.isatty()
    app = CalculusTUIApp()
    app.run(demo_mode=demo_mode)
