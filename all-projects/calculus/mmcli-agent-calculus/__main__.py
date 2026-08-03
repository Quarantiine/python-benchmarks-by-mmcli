"""
Entry point for executing calculus package as a module or direct script.
"""

import sys
import importlib.util
from pathlib import Path

CALCULUS_DIR = Path(__file__).resolve().parent

if str(CALCULUS_DIR) in sys.path:
    sys.path.remove(str(CALCULUS_DIR))

if "calculus" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "calculus",
        CALCULUS_DIR / "__init__.py",
        submodule_search_locations=[str(CALCULUS_DIR)]
    )
    calculus_mod = importlib.util.module_from_spec(spec)
    sys.modules["calculus"] = calculus_mod
    spec.loader.exec_module(calculus_mod)

from calculus.cli import main

if __name__ == "__main__":
    main()
