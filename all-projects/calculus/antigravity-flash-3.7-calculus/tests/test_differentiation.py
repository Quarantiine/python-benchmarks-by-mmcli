"""
Unit tests for Symbolic Differentiation Rules & Calculus Utilities
"""

import math
import pytest
from engine.parser import parse_expr
from engine.differentiator import (
    diff, higher_derivative, partial_derivatives,
    gradient, hessian, taylor_series, tangent_line, find_roots, find_critical_points
)
from engine.ast_nodes import Constant, Variable


def test_basic_derivatives():
    # d/dx[5] = 0
    assert diff("5", "x") == Constant(0)
    # d/dx[x] = 1
    assert diff("x", "x") == Constant(1)
    # d/dx[y] = 0 (w.r.t x)
    assert diff("y", "x") == Constant(0)


def test_power_rule():
    # d/dx[x^3] = 3*x^2
    d = diff("x^3", "x")
    assert d.evaluate({"x": 2}) == 12.0

    # d/dx[x^2] = 2*x
    d2 = diff("x^2", "x")
    assert d2.evaluate({"x": 5}) == 10.0


def test_product_rule():
    # d/dx[x * sin(x)] = sin(x) + x * cos(x)
    d = diff("x * sin(x)", "x")
    # at x = pi: sin(pi) + pi*cos(pi) = 0 + pi*(-1) = -pi
    assert math.isclose(d.evaluate({"x": math.pi}), -math.pi, abs_tol=1e-5)


def test_quotient_rule():
    # d/dx[(x + 1) / (x - 1)] = ((1)*(x - 1) - (x + 1)*(1)) / (x - 1)^2 = -2 / (x - 1)^2
    d = diff("(x + 1) / (x - 1)", "x")
    # at x = 3: -2 / (3 - 1)^2 = -2 / 4 = -0.5
    assert math.isclose(d.evaluate({"x": 3.0}), -0.5)


def test_chain_rule_trig_and_exp():
    # d/dx[sin(x^2)] = 2*x*cos(x^2)
    d1 = diff("sin(x^2)", "x")
    # at x = 1: 2 * cos(1) ≈ 1.0806046
    assert math.isclose(d1.evaluate({"x": 1.0}), 2.0 * math.cos(1.0))

    # d/dx[exp(3*x)] = 3*exp(3*x)
    d2 = diff("exp(3*x)", "x")
    assert math.isclose(d2.evaluate({"x": 0.0}), 3.0)

    # d/dx[ln(x^2 + 1)] = 2*x / (x^2 + 1)
    d3 = diff("ln(x^2 + 1)", "x")
    assert math.isclose(d3.evaluate({"x": 1.0}), 1.0)


def test_general_power_rule():
    # d/dx[x^x] = x^x * (ln(x) + 1)
    d = diff("x^x", "x")
    # at x = 2: 2^2 * (ln(2) + 1) = 4 * (0.693147 + 1) ≈ 6.7725887
    assert math.isclose(d.evaluate({"x": 2.0}), 4.0 * (math.log(2.0) + 1.0))


def test_higher_derivatives():
    # f(x) = x^4 - 2*x^3 + x
    # f'(x) = 4*x^3 - 6*x^2 + 1
    # f''(x) = 12*x^2 - 12*x
    # f'''(x) = 24*x - 12
    # f''''(x) = 24
    expr = parse_expr("x^4 - 2*x^3 + x")
    d2 = higher_derivative(expr, "x", 2)
    assert d2.evaluate({"x": 2.0}) == 12.0 * 4.0 - 12.0 * 2.0  # 24.0

    d4 = higher_derivative(expr, "x", 4)
    assert d4.evaluate({"x": 10.0}) == 24.0


def test_multivariable_gradient_and_hessian():
    # f(x, y) = x^2 + 3*x*y + y^2
    expr = parse_expr("x^2 + 3*x*y + y^2")
    grad = gradient(expr, ["x", "y"])
    # grad[0] = 2x + 3y, grad[1] = 3x + 2y
    assert grad[0].evaluate({"x": 1.0, "y": 2.0}) == 2.0 + 6.0  # 8.0
    assert grad[1].evaluate({"x": 1.0, "y": 2.0}) == 3.0 + 4.0  # 7.0

    hess = hessian(expr, ["x", "y"])
    # H = [[2, 3], [3, 2]]
    assert hess[0][0].evaluate({}) == 2.0
    assert hess[0][1].evaluate({}) == 3.0
    assert hess[1][0].evaluate({}) == 3.0
    assert hess[1][1].evaluate({}) == 2.0


def test_taylor_series():
    # Taylor series of exp(x) around 0: 1 + x + x^2/2 + x^3/6 + ...
    expr = parse_expr("exp(x)")
    taylor = taylor_series(expr, "x", x0=0.0, order=3)
    # at x = 0.5: 1 + 0.5 + 0.125 + 0.5^3/6 = 1 + 0.5 + 0.125 + 0.0208333 = 1.645833
    assert math.isclose(taylor.evaluate({"x": 0.5}), 1.0 + 0.5 + 0.125 + (0.5**3)/6.0, abs_tol=1e-5)


def test_tangent_line():
    # f(x) = x^2 at x0 = 2: y = 4*(x - 2) + 4 = 4x - 4
    expr = parse_expr("x^2")
    t_line, m, b = tangent_line(expr, "x", x0=2.0)
    assert math.isclose(m, 4.0)
    assert math.isclose(b, -4.0)
    assert math.isclose(t_line.evaluate({"x": 3.0}), 8.0)


def test_critical_points():
    # f(x) = x^3 - 3*x (extrema at x = -1 (max), x = 1 (min))
    expr = parse_expr("x^3 - 3*x")
    crit_pts = find_critical_points(expr, "x", x_min=-3.0, x_max=3.0)
    assert len(crit_pts) == 2
    xs = [pt["x"] for pt in crit_pts]
    assert any(math.isclose(x, -1.0, abs_tol=1e-3) for x in xs)
    assert any(math.isclose(x, 1.0, abs_tol=1e-3) for x in xs)
