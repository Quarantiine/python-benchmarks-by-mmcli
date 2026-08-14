"""
Unit tests for Mathematical Expression Parser & Lexer
"""

import math
import pytest
from engine.parser import parse_expr, ParseError
from engine.ast_nodes import (
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Exp, Ln, Variable, Constant, E, PI
)


def test_basic_arithmetic():
    expr = parse_expr("1 + 2 * 3")
    assert isinstance(expr, Add)
    assert isinstance(expr.right, Multiply)
    assert expr.evaluate({}) == 7.0

    expr2 = parse_expr("(1 + 2) * 3")
    assert isinstance(expr2, Multiply)
    assert expr2.evaluate({}) == 9.0


def test_power_precedence_and_associativity():
    # Power should be right associative: 2^3^2 = 2^(3^2) = 2^9 = 512
    expr = parse_expr("2 ^ 3 ^ 2")
    assert expr.evaluate({}) == 512.0

    expr2 = parse_expr("2 ** 3 ** 2")
    assert expr2.evaluate({}) == 512.0


def test_implicit_multiplication():
    expr1 = parse_expr("2x")
    assert isinstance(expr1, Multiply)
    assert expr1.evaluate({"x": 5}) == 10.0

    expr2 = parse_expr("3sin(x)")
    assert isinstance(expr2, Multiply)
    assert math.isclose(expr2.evaluate({"x": math.pi / 2}), 3.0)

    expr3 = parse_expr("(x + 1)(x - 1)")
    assert isinstance(expr3, Multiply)
    assert expr3.evaluate({"x": 3}) == 8.0

    expr4 = parse_expr("2(x + 3)")
    assert expr4.evaluate({"x": 2}) == 10.0


def test_unary_minus():
    expr1 = parse_expr("-x + 5")
    assert expr1.evaluate({"x": 2}) == 3.0

    expr2 = parse_expr("-x^2")
    # - (x^2)
    assert expr2.evaluate({"x": 3}) == -9.0


def test_functions_and_constants():
    expr = parse_expr("sin(pi / 2) + ln(e)")
    assert math.isclose(expr.evaluate({}), 2.0)

    expr2 = parse_expr("exp(0) + cos(0)")
    assert expr2.evaluate({}) == 2.0

    expr3 = parse_expr("sqrt(16) + abs(-5)")
    assert expr3.evaluate({}) == 9.0


def test_syntax_errors():
    with pytest.raises(ParseError):
        parse_expr("2 + * 3")

    with pytest.raises(ParseError):
        parse_expr("(x + 1")

    with pytest.raises(ParseError):
        parse_expr("")
