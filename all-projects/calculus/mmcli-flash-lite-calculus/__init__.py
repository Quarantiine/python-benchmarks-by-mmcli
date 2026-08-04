"""
Calculus package initialization file exposing core AST nodes, parser,
and evaluation utilities.
"""

from .ast_nodes import (
    Node, Number, Variable, BinaryOp, UnaryOp,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan
)
from .parser import parse_expression, Parser, Lexer, Token
from .engine import differentiate, simplify
from .tui import run_tui, render_tree, render_derivation_steps, evaluate_expression

__all__ = [
    "Node",
    "Number",
    "Variable",
    "BinaryOp",
    "UnaryOp",
    "Add",
    "Subtract",
    "Multiply",
    "Divide",
    "Power",
    "Negate",
    "Sin",
    "Cos",
    "Tan",
    "Log",
    "Exp",
    "Sqrt",
    "Asin",
    "Acos",
    "Atan",
    "parse_expression",
    "Parser",
    "Lexer",
    "Token",
    "differentiate",
    "simplify",
    "run_tui",
    "render_tree",
    "render_derivation_steps",
    "evaluate_expression",
]
