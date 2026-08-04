"""
Unit tests for mathematical AST nodes, expression parser, evaluation, and string representations.
"""

import math
import pytest
from calculus import (
    parse_expression, Number, Variable, Add, Subtract, Multiply,
    Divide, Power, Negate, Sin, Cos, Log, Exp, Sqrt
)


def test_number_node():
    n = Number(42)
    assert n.evaluate({}) == 42.0
    assert str(n) == "42"
    assert n.get_variables() == set()
    assert n.clone() == Number(42)


def test_variable_node():
    v = Variable("x")
    assert v.evaluate({"x": 5.5}) == 5.5
    assert str(v) == "x"
    assert v.get_variables() == {"x"}
    assert v.clone() == Variable("x")

    with pytest.raises(ValueError):
        v.evaluate({})


def test_operator_overloads():
    x = Variable("x")
    expr = x + 2 * x ** 2 - Sin(x) / Cos(x)
    assert isinstance(expr, Subtract)
    assert expr.get_variables() == {"x"}


def test_parser_basic_arithmetic():
    expr = parse_expression("3 + 4 * 2 - (1 + 1)")
    # Evaluates without variables
    env = {}
    # 3 + 8 - 2 = 9
    assert math.isclose(expr.evaluate(env), 9.0)


def test_parser_functions_and_powers():
    expr = parse_expression("sin(x) ^ 2 + cos(x) ^ 2")
    env = {"x": 1.234}
    assert math.isclose(expr.evaluate(env), 1.0, abs_tol=1e-7)


def test_parser_log_exp_sqrt():
    expr = parse_expression("sqrt(exp(log(4)))")
    assert math.isclose(expr.evaluate({}), 2.0, abs_tol=1e-7)


def test_implicit_multiplication():
    expr = parse_expression("2x + 3sin(x)")
    env = {"x": 0.0}
    # 2*0 + 3*sin(0) = 0
    assert math.isclose(expr.evaluate(env), 0.0)

    expr2 = parse_expression("(x + 1)(x - 1)")
    env2 = {"x": 3.0}
    # (3+1)*(3-1) = 4 * 2 = 8
    assert math.isclose(expr2.evaluate(env2), 8.0)


def test_constants():
    expr = parse_expression("pi")
    assert math.isclose(expr.evaluate({}), math.pi)

    expr2 = parse_expression("e")
    assert math.isclose(expr2.evaluate({}), math.e)


def test_string_representations():
    expr = parse_expression("x^2 + 3*x + 1")
    assert str(expr) == "(((x ^ 2) + (3 * x)) + 1)"
