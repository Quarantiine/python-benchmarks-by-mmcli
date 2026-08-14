"""
TUI Package
===========
Terminal user interface components, widgets, and full-screen apps.
"""

from .widgets import (
    MathOverviewWidget,
    ASTTreeWidget,
    DerivationStepsWidget,
    GraphPlotWidget,
    CalculusAnalysisWidget,
)
from .app import run_textual_tui

try:
    from tui_core import (
        StepByStepEngine,
        SymbolicCalculusTUI,
        run_curses_tui,
        run_interactive_cli,
        run_tui,
    )
except ImportError:
    from ..tui_core import (
        StepByStepEngine,
        SymbolicCalculusTUI,
        run_curses_tui,
        run_interactive_cli,
        run_tui,
    )

__all__ = [
    "MathOverviewWidget",
    "ASTTreeWidget",
    "DerivationStepsWidget",
    "GraphPlotWidget",
    "CalculusAnalysisWidget",
    "run_textual_tui",
    "StepByStepEngine",
    "SymbolicCalculusTUI",
    "run_curses_tui",
    "run_interactive_cli",
    "run_tui",
]
