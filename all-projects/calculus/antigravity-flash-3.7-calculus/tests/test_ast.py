"""
Unit tests for AST Nodes and Operator Overloading
"""

import math
import pytest
from fractions import Fraction
from engine.ast_nodes import (
    Constant, Variable, NamedConstant,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Exp, Ln, Log, Sqrt, Abs,
    E, PI
)


def test_constant_eval():
    c1 = Constant(5)
    assert c1.evaluate({}) == 5.0
    c2 = Constant(Fraction(1, 3))
    assert math.isclose(c2.evaluate({}), 1/3)


def test_variable_eval():
    x = Variable("x")
    assert x.evaluate({"x": 4.5}) == 4.5
    with pytest.raises(KeyError):
        x.evaluate({"y": 2.0})


def test_named_constants():
    assert math.isclose(E.evaluate({}), math.e)
    assert math.isclose(PI.evaluate({}), math.pi)


def test_operator_overloads():
    x = Variable("x")
    expr1 = x + 3
    assert isinstance(expr1, Add)
    assert expr1.evaluate({"x": 2}) == 5.0

    expr2 = 4 * x - 2
    assert isinstance(expr2, Subtract)
    assert expr2.evaluate({"x": 3}) == 10.0

    expr3 = (x + 1) / (x - 1)
    assert isinstance(expr3, Divide)
    assert expr3.evaluate({"x": 3}) == 2.0

    expr4 = x ** 3
    assert isinstance(expr4, Power)
    assert expr4.evaluate({"x": 2}) == 8.0

    expr5 = -x
    assert isinstance(expr5, Negate)
    assert expr5.evaluate({"x": 5}) == -5.0


def test_elementary_functions():
    x = Variable("x")
    assert math.isclose(Sin(x).evaluate({"x": math.pi / 2}), 1.0)
    assert math.isclose(Cos(x).evaluate({"x": math.pi}), -1.0)
    assert math.isclose(Exp(x).evaluate({"x": 0}), 1.0)
    assert math.isclose(Ln(x).evaluate({"x": math.e}), 1.0)
    assert math.isclose(Sqrt(x).evaluate({"x": 16}), 4.0)
    assert math.isclose(Abs(x).evaluate({"x": -7}), 7.0)


def test_to_latex():
    x = Variable("x")
    expr = (Sin(x ** 2)) / (x + 1)
    latex_str = expr.to_latex()
    assert "\\frac" in latex_str
    assert "\\sin" in latex_str


def test_variables_set():
    x = Variable("x")
    y = Variable("y")
    expr = x ** 2 + 2 * x * y + y ** 2
    assert expr.variables() == {"x", "y"}
