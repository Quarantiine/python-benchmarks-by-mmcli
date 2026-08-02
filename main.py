"""
Symbolic Calculus Engine & Interactive Terminal User Interface (TUI).

Run interactive TUI:
  python main.py

Run direct CLI commands:
  python main.py diff "x^3 + sin(x)" -v x
  python main.py int "x^2" -l 0 -u 2
  python main.py lim "sin(x)/x" -p 0
  python main.py simplify "x + x + 0"
  python main.py eval "x^2 + y" x=3 y=4
  python main.py tree "sin(2*x)"
"""

import sys
from pathlib import Path

# Dynamically append 'all-projects' directory to sys.path to resolve internal packages
ALL_PROJECTS_DIR = Path(__file__).resolve().parent / "all-projects"
if str(ALL_PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(ALL_PROJECTS_DIR))

from calculus.cli import main as cli_main


if __name__ == "__main__":
    cli_main()
