"""
Symbolic Calculus Engine

A pure Python symbolic computation library supporting parsing, differentiation,
integration, limits, simplification, LaTeX/ASCII pretty rendering, and an interactive TUI.
"""

from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Asin, Acos, Atan, Exp, Ln, Sqrt, Abs, E_CONST, PI_CONST
)
from calculus.parser import parse
from calculus.simplify import simplify
from calculus.diff import diff
from calculus.integrate import integrate
from calculus.limits import limit
from calculus.render import render_pretty, to_latex, render_tree
from calculus.tui import SymbolicCalculusTUI, StepByStepEngine
from calculus.cli import run_cli

__all__ = [
    "Expr", "Const", "Symbol", "Add", "Sub", "Mul", "Div", "Pow", "Neg",
    "Sin", "Cos", "Tan", "Asin", "Acos", "Atan", "Exp", "Ln", "Sqrt", "Abs", "E_CONST", "PI_CONST",
    "parse", "simplify", "diff", "integrate", "limit",
    "render_pretty", "to_latex", "render_tree",
    "SymbolicCalculusTUI", "StepByStepEngine", "run_cli"
]
