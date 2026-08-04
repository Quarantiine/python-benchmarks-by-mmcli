"""
Unit tests for the calculus core engine (AST, parsing, recursive differentiation rules,
product rule, quotient rule, chain rule, power rule, trig rules, and algebraic simplification).
"""

import pytest
import math
from calculus import parse_expression, differentiate, simplify, Number, Variable, Add, Multiply, Sin, Cos


def test_basic_parsing_and_evaluation():
    expr = parse_expression("x^2 + 3*x + 2")
    assert expr.evaluate({'x': 2.0}) == 12.0
    assert expr.evaluate({'x': 0.0}) == 2.0


def test_differentiate_power_rule():
    # d/dx(x^3) = 3 * x^2
    expr = parse_expression("x^3")
    deriv = differentiate(expr, 'x')
    simp = simplify(deriv)
    assert str(simp) == "(3 * (x ^ 2))"


def test_differentiate_sum_rule():
    # d/dx(x^2 + x) = 2*x + 1
    expr = parse_expression("x^2 + x")
    deriv = differentiate(expr, 'x')
    simp = simplify(deriv)
    assert "((2 * x) + 1)" in str(simp) or "((2 * (x ^ 1)) + 1)" in str(simp)


def test_differentiate_product_rule():
    # d/dx(x * sin(x)) = 1 * sin(x) + x * cos(x)
    expr = parse_expression("x * sin(x)")
    deriv = differentiate(expr, 'x')
    simp = simplify(deriv)
    # Check evaluation or representation
    val = simp.evaluate({'x': math.pi / 2})
    expected = math.sin(math.pi / 2) + (math.pi / 2) * math.cos(math.pi / 2)
    assert math.isclose(val, expected, rel_tol=1e-7)


def test_differentiate_quotient_rule():
    # d/dx(x / (x + 1))
    expr = parse_expression("x / (x + 1)")
    deriv = differentiate(expr, 'x')
    simp = simplify(deriv)
    val = simp.evaluate({'x': 1.0})
    # f = x, g = x+1. f'g - fg' / g^2 = 1*(x+1) - x*(1) / (x+1)^2 = 1 / (x+1)^2
    # at x=1, 1 / 4 = 0.25
    assert math.isclose(val, 0.25, rel_tol=1e-7)


def test_differentiate_chain_rule_trig():
    # d/dx(sin(x^2)) = cos(x^2) * 2*x
    expr = parse_expression("sin(x^2)")
    deriv = differentiate(expr, 'x')
    simp = simplify(deriv)
    val = simp.evaluate({'x': 1.0})
    expected = math.cos(1.0) * 2.0 * 1.0
    assert math.isclose(val, expected, rel_tol=1e-7)


def test_algebraic_simplification():
    # x + 0 => x
    expr1 = parse_expression("x + 0")
    assert str(simplify(expr1)) == "x"

    # x * 1 => x
    expr2 = parse_expression("x * 1")
    assert str(simplify(expr2)) == "x"

    # 0 * x => 0
    expr3 = parse_expression("0 * x")
    assert str(simplify(expr3)) == "0"

    # x - x => 0
    expr4 = parse_expression("x - x")
    assert str(simplify(expr4)) == "0"

    # -(-x) => x
    expr5 = parse_expression("-(-x)")
    assert str(simplify(expr5)) == "x"
