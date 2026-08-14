"""
Unit tests for Symbolic Integration, Limits, Unicode Superscripts, and Bare Functions
"""

import math
import pytest
from engine.parser import parse_expr
from engine.differentiator import diff
from engine.integrator import integrate, definite_integrate
from engine.limits import limit
from engine.ast_nodes import Constant, Variable


def test_symbolic_polynomial_integration():
    # int(x^4 - 2*x + 1) dx = x^5/5 - x^2 + x
    anti = integrate("x^4 - 2*x + 1", "x")
    # Verify derivative matches original
    d_anti = diff(anti, "x")
    for s in [0.5, 1.0, 2.0]:
        assert math.isclose(d_anti.evaluate({"x": s}), parse_expr("x^4 - 2*x + 1").evaluate({"x": s}))


def test_symbolic_trig_and_exp_integration():
    # int(sin(x)) = -cos(x)
    assert diff(integrate("sin(x)", "x"), "x").evaluate({"x": 1.0}) == pytest.approx(math.sin(1.0))
    # int(cos(2*x)) = sin(2*x)/2
    assert diff(integrate("cos(2*x)", "x"), "x").evaluate({"x": 0.5}) == pytest.approx(math.cos(1.0))
    # int(exp(3*x)) = exp(3*x)/3
    assert diff(integrate("exp(3*x)", "x"), "x").evaluate({"x": 0.2}) == pytest.approx(math.exp(0.6))


def test_definite_integral():
    # int_0^3 x^2 dx = [x^3/3]_0^3 = 9.0
    val = definite_integrate("x^2", "x", lower=0, upper=3)
    assert math.isclose(val, 9.0, abs_tol=1e-4)


def test_limits_lhopital_and_perturbation():
    # lim_{x->0} sin(x)/x = 1.0
    lim1 = limit("sin(x)/x", "x", point=0.0)
    assert math.isclose(lim1, 1.0, abs_tol=1e-4)

    # lim_{x->0} (1 - cos(x))/x^2 = 0.5
    lim2 = limit("(1 - cos(x))/x^2", "x", point=0.0)
    assert math.isclose(lim2, 0.5, abs_tol=1e-4)


def test_unicode_superscript_parsing():
    expr = parse_expr("x² + sin(x)")
    d = diff(expr, "x")
    # d/dx[x^2 + sin(x)] = 2*x + cos(x)
    assert math.isclose(d.evaluate({"x": 1.0}), 2.0 + math.cos(1.0))


def test_bare_function_parsing():
    expr = parse_expr("cos3x")
    d = diff(expr, "x")
    # d/dx[cos(3x)] = -3*sin(3x)
    assert math.isclose(d.evaluate({"x": 1.0}), -3.0 * math.sin(3.0))
