"""
Symbolic Calculus Engine
========================
An Abstract Syntax Tree (AST) symbolic calculus engine with recursive differentiation,
algebraic simplification, step-by-step derivation breakdown, symbolic integration,
limit calculations, and terminal plotting.
"""

from .ast_nodes import (
    Node, Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI
)
from .parser import parse_expr, Parser, Lexer, ParseError
from .simplifier import simplify
from .tracker import DerivationTracker, DerivationStep
from .differentiator import (
    diff,
    higher_derivative,
    partial_derivatives,
    gradient,
    hessian,
    taylor_series,
    tangent_line,
    normal_line,
    find_roots,
    find_critical_points,
    definite_integral_approx
)
from .integrator import (
    integrate,
    definite_integrate
)
from .limits import (
    limit
)
from .plotter import (
    PlotCanvas,
    plot_expression,
    plot_functions,
    render_braille_plot
)

__all__ = [
    # AST
    "Node", "Constant", "Variable", "NamedConstant",
    "Add", "Subtract", "Multiply", "Divide", "Power", "Negate",
    "Sin", "Cos", "Tan", "Sec", "Csc", "Cot",
    "Asin", "Acos", "Atan", "Sinh", "Cosh", "Tanh",
    "Exp", "Ln", "Log", "Sqrt", "Abs",
    "E", "PI",
    # Parsing
    "parse_expr", "Parser", "Lexer", "ParseError",
    # Simplification
    "simplify",
    # Tracking
    "DerivationTracker", "DerivationStep",
    # Differentiation & Calculus
    "diff", "higher_derivative", "partial_derivatives", "gradient", "hessian",
    "taylor_series", "tangent_line", "normal_line",
    "find_roots", "find_critical_points", "definite_integral_approx",
    # Integration & Limits
    "integrate", "definite_integrate", "limit",
    # Plotting
    "PlotCanvas", "plot_expression", "plot_functions", "render_braille_plot"
]
