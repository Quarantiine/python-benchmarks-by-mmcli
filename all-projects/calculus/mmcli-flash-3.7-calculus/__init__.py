"""
Calculus Engine Core
====================
Mathematical AST, Pratt Parser, Symbolic Calculus, Simplification, Limits, Integration,
Terminal Plotting, AST Tree Visualization, Derivation Breakdown, and TUI.
"""

from ast_nodes import (
    Node, Constant, NamedConstant, Variable,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    ArcSin, ArcCos, ArcTan,
    E, PI, TAU, PHI,
    to_node
)

from parser import (
    Token, TokenType, Lexer, Parser, ParseError,
    parse, parse_expr, parse_expression,
    evaluate_expression
)

from simplifier import (
    simplify, simplify_pass
)

from tracker import (
    DerivationStep, DerivationTracker
)

from differentiator import (
    diff, higher_derivative, partial_derivatives,
    gradient, hessian, taylor_series, tangent_line,
    find_roots_newton, critical_points
)

from limits import (
    limit
)

from integrator import (
    integrate, definite_integrate
)

from plotter import (
    PlotCanvas, AsciiCanvas, plot_functions, plot_expression,
    render_braille_plot, render_ascii_plot, plot_curve
)

from tree_renderer import (
    render_ast_tree, render_ascii_tree, render_tree,
    render_pretty, to_latex, ASTVisualizer
)

from derivation_view import (
    render_derivation_breakdown, format_derivation_steps,
    DerivationViewer
)

from tui_core import (
    StepByStepEngine, SymbolicCalculusTUI, run_tui,
    run_curses_tui, run_interactive_cli
)

from cli import (
    run_cli
)

__all__ = [
    # AST Nodes
    "Node", "Constant", "NamedConstant", "Variable",
    "Add", "Subtract", "Multiply", "Divide", "Power", "Negate",
    "Sin", "Cos", "Tan", "Sec", "Csc", "Cot",
    "Asin", "Acos", "Atan", "Sinh", "Cosh", "Tanh",
    "Exp", "Ln", "Log", "Sqrt", "Abs",
    "ArcSin", "ArcCos", "ArcTan",
    "E", "PI", "TAU", "PHI",
    "to_node",
    # Parser
    "Token", "TokenType", "Lexer", "Parser", "ParseError",
    "parse", "parse_expr", "parse_expression",
    "evaluate_expression",
    # Simplifier
    "simplify", "simplify_pass",
    # Tracker
    "DerivationStep", "DerivationTracker",
    # Calculus - Differentiation
    "diff", "higher_derivative", "partial_derivatives",
    "gradient", "hessian", "taylor_series", "tangent_line",
    "find_roots_newton", "critical_points",
    # Calculus - Limits
    "limit",
    # Calculus - Integration
    "integrate", "definite_integrate",
    # Plotter
    "PlotCanvas", "AsciiCanvas", "plot_functions", "plot_expression",
    "render_braille_plot", "render_ascii_plot", "plot_curve",
    # Tree Renderer
    "render_ast_tree", "render_ascii_tree", "render_tree",
    "render_pretty", "to_latex", "ASTVisualizer",
    # Derivation View
    "render_derivation_breakdown", "format_derivation_steps",
    "DerivationViewer",
    # TUI
    "StepByStepEngine", "SymbolicCalculusTUI", "run_tui",
    "run_curses_tui", "run_interactive_cli",
    # CLI
    "run_cli",
]
