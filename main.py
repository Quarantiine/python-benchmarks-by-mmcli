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

# Dynamically resolve 'calculus' package without inserting CALCULUS_DIR into sys.path (which would shadow stdlib 'ast')
CALCULUS_DIR = Path(__file__).resolve().parent / "all-projects" / "calculus" / "mmcli-flash-calculus" / "mmcli-flash-lite-calculus"

if str(CALCULUS_DIR) in sys.path:
    sys.path.remove(str(CALCULUS_DIR))

if "calculus" not in sys.modules:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "calculus",
        CALCULUS_DIR / "__init__.py",
        submodule_search_locations=[str(CALCULUS_DIR)]
    )
    calculus_mod = importlib.util.module_from_spec(spec)
    sys.modules["calculus"] = calculus_mod
    spec.loader.exec_module(calculus_mod)

from calculus.cli import main as cli_main


if __name__ == "__main__":
    cli_main()
