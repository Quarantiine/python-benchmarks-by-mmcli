"""
Pytest configuration file to dynamically register the 'calculus' package
from 'all-projects/calculus/mmcli-flash-calculus' cleanly without shadowing
the standard library 'ast' module.
"""

import sys
import importlib.util
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CALCULUS_DIR = ROOT_DIR / "all-projects" / "calculus" / "mmcli-flash-lite-calculus"

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
