"""
Pytest configuration file to dynamically add the 'all-projects' directory
to sys.path so 'calculus' and other packages inside all-projects can be imported directly.
"""

import sys
from pathlib import Path

# Compute path to 'all-projects' directory
ROOT_DIR = Path(__file__).resolve().parent.parent
ALL_PROJECTS_DIR = ROOT_DIR / "all-projects"

if str(ALL_PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(ALL_PROJECTS_DIR))
