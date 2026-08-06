"""Lexer and Parser for converting mathematical string expressions into AST nodes."""

import math
import re
from typing import List, Union

from .ast import (
    AcosNode,
    AddNode,
    AsinNode,
    AtanNode,
    Constant,
    CosNode,
    DivNode,
    ExpNode,
    LnNode,
    MulNode,
    NegNode,
    Node,
    PowNode,
    SinNode,
    SqrtNode,
    SubNode,
    TanNode,
    Variable,
)


class Token:

    def __init__(self, type_: str, value: Union[str, float]):
        self.type = type_  # 'NUMBER', 'VAR', 'OP', 'FUNC', 'LPAREN', 'RPAREN'
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


KNOWN_FUNCS = [
    "arcsin", "arccos", "arctan",
    "asin", "acos", "atan",
    "sin", "cos", "tan",
    "exp", "sqrt", "ln", "log",
]


def tokenize(expr: str) -> List[Token]:
    """Convert expression string into list of tokens with implicit multiplication handling."""
    # Normalize operators and spaces
    expr = expr.replace("**", "^").strip()

    token_specification = [
        ("NUMBER", r"\d+(\.\d+)?|\.\d+"),
        ("FUNC", r"(sin|cos|tan|asin|acos|atan|arcsin|arccos|arctan|exp|ln|log|sqrt)\b"),
        ("VAR", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP", r"[\+\-\*\/\^]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"\s+"),
        ("MISMATCH", r"."),
    ]

    tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification)
    raw_tokens = []

    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            val = float(value) if "." in value else int(value)
            raw_tokens.append(Token("NUMBER", val))
        elif kind == "FUNC":
            raw_tokens.append(Token("FUNC", value))
        elif kind == "VAR":
            v_lower = value.lower()
            if v_lower == "pi":
                raw_tokens.append(Token("NUMBER", math.pi))
            elif v_lower == "e":
                raw_tokens.append(Token("NUMBER", math.e))
            else:
                matched_func = None
                for f in KNOWN_FUNCS:
                    if v_lower.startswith(f) and len(v_lower) > len(f):
                        matched_func = f
                        break
                if matched_func:
                    rem = value[len(matched_func):]
                    raw_tokens.append(Token("FUNC", matched_func))
                    raw_tokens.append(Token("LPAREN", "("))
                    raw_tokens.extend(tokenize(rem))
                    raw_tokens.append(Token("RPAREN", ")"))
                else:
                    raw_tokens.append(Token("VAR", value))
        elif kind == "OP":
            raw_tokens.append(Token("OP", value))
        elif kind == "LPAREN":
            raw_tokens.append(Token("LPAREN", value))
        elif kind == "RPAREN":
            raw_tokens.append(Token("RPAREN", value))
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise ValueError(f"Unexpected character in expression: {value}")

    # Process implicit multiplication:
    # e.g., 2x -> 2 * x, 3(x) -> 3 * (x), x sin(x) -> x * sin(x), (a)(b) -> (a) * (b)
    tokens: List[Token] = []
    for i, tok in enumerate(raw_tokens):
        if i > 0:
            prev = raw_tokens[i - 1]
            # Cases where * should be inserted:
            # prev: NUMBER, VAR, RPAREN
            # curr: VAR, FUNC, LPAREN
            prev_can_end = prev.type in ("NUMBER", "VAR", "RPAREN")
            curr_can_start = tok.type in ("VAR", "FUNC", "LPAREN")
            if prev_can_end and curr_can_start:
                tokens.append(Token("OP", "*"))

        tokens.append(tok)

    return tokens


def parse_expression(expr: str) -> Node:
    """Parse infix math expression string into AST node."""
    tokens = tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression string.")

    # Convert to AST using recursive descent / operator-precedence parsing
    pos = 0

    def parse_expr(min_prec: int = 0) -> Node:
        nonlocal pos
        left = parse_primary()

        precedences = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        right_assoc = {"^": True}

        while pos < len(tokens):
            tok = tokens[pos]
            if tok.type != "OP" or tok.value not in precedences:
                break
            op = str(tok.value)
            prec = precedences[op]

            if prec < min_prec:
                break

            pos += 1
            next_min_prec = prec + 1 if not right_assoc.get(op, False) else prec
            right = parse_expr(next_min_prec)

            if op == "+":
                left = AddNode(left, right)
            elif op == "-":
                left = SubNode(left, right)
            elif op == "*":
                left = MulNode(left, right)
            elif op == "/":
                left = DivNode(left, right)
            elif op == "^":
                left = PowNode(left, right)

        return left

    def parse_primary() -> Node:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression.")

        tok = tokens[pos]

        # Prefix unary minus / plus
        if tok.type == "OP" and tok.value == "-":
            pos += 1
            child = parse_expr(3)  # High precedence for unary minus
            return NegNode(child)
        elif tok.type == "OP" and tok.value == "+":
            pos += 1
            return parse_expr(3)

        if tok.type == "NUMBER":
            pos += 1
            return Constant(tok.value)

        if tok.type == "VAR":
            pos += 1
            return Variable(str(tok.value))

        if tok.type == "FUNC":
            func_name = str(tok.value).lower()
            pos += 1
            if pos < len(tokens) and tokens[pos].type == "LPAREN":
                pos += 1
                arg = parse_expr(0)
                if pos >= len(tokens) or tokens[pos].type != "RPAREN":
                    raise ValueError(f"Missing closing parenthesis for function '{func_name}'")
                pos += 1
            else:
                arg = parse_primary()

            if func_name == "sin":
                return SinNode(arg)
            elif func_name == "cos":
                return CosNode(arg)
            elif func_name == "tan":
                return TanNode(arg)
            elif func_name in ("asin", "arcsin"):
                return AsinNode(arg)
            elif func_name in ("acos", "arccos"):
                return AcosNode(arg)
            elif func_name in ("atan", "arctan"):
                return AtanNode(arg)
            elif func_name == "exp":
                return ExpNode(arg)
            elif func_name in ("ln", "log"):
                return LnNode(arg)
            elif func_name == "sqrt":
                return SqrtNode(arg)
            else:
                raise ValueError(f"Unknown function '{func_name}'")

        if tok.type == "LPAREN":
            pos += 1
            node = parse_expr(0)
            if pos >= len(tokens) or tokens[pos].type != "RPAREN":
                raise ValueError("Missing closing parenthesis ')'")
            pos += 1
            return node

        raise ValueError(f"Unexpected token: {tok}")

    ast = parse_expr(0)
    if pos < len(tokens):
        raise ValueError(f"Extra trailing tokens starting at '{tokens[pos]}'")
    return ast

