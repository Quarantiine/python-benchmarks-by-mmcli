"""
Calculus package initialization file exposing core AST nodes, parser,
and evaluation utilities.
"""

from calculus.ast_nodes import (
    Node, Number, Variable, BinaryOp, UnaryOp,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan
)
from calculus.parser import parse_expression, Parser, Lexer, Token
from calculus.engine import differentiate, simplify, integrate
from calculus.tui import run_tui, render_tree, render_derivation_steps, evaluate_expression

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
    "integrate",
    "run_tui",
    "render_tree",
    "render_derivation_steps",
    "evaluate_expression",
]
