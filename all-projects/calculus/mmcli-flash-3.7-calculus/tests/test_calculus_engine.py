"""
Calculus Engine & Simplification Test Suite
===========================================
Comprehensive unit tests for algebraic simplification, differentiation with step-by-step
tracking, multivariate calculus, limits, and integration.
"""

import math
from fractions import Fraction
import pytest

from ast_nodes import Constant, Variable, Add, Subtract, Multiply, Divide, Power, Sin, Cos, Exp, Ln
from parser import parse_expr
from simplifier import simplify
from tracker import DerivationTracker
from differentiator import (
    diff, higher_derivative, partial_derivatives,
    gradient, hessian, taylor_series, tangent_line, critical_points
)
from limits import limit
from integrator import integrate, definite_integrate


class TestSimplification:
    """Test algebraic simplification rules and constant folding."""

    def test_constant_folding(self):
        assert simplify("2 + 3").evaluate() == 5
        assert simplify("10 - 4").evaluate() == 6
        assert simplify("3 * 7").evaluate() == 21
        assert simplify("12 / 4").evaluate() == 3

    def test_additive_identities(self):
        assert simplify("x + 0").to_infix() == "x"
        assert simplify("0 + x").to_infix() == "x"
        assert simplify("x - 0").to_infix() == "x"
        assert simplify("x - x").to_infix() == "0"
        assert simplify("x + (-x)").to_infix() == "0"

    def test_multiplicative_identities(self):
        assert simplify("x * 1").to_infix() == "x"
        assert simplify("1 * x").to_infix() == "x"
        assert simplify("x * 0").to_infix() == "0"
        assert simplify("0 * x").to_infix() == "0"
        assert simplify("x / 1").to_infix() == "x"
        assert simplify("x / x").to_infix() == "1"

    def test_like_terms_collection(self):
        assert simplify("3*x + 4*x").to_infix() == "7 * x"
        assert simplify("5*x - 2*x").to_infix() == "3 * x"
        assert simplify("2*x - 2*x").to_infix() == "0"

    def test_power_rules(self):
        assert simplify("x^1").to_infix() == "x"
        assert simplify("x^0").to_infix() == "1"
        assert simplify("x^2 * x^3").to_infix() == "x ^ 5"
        assert simplify("x^5 / x^2").to_infix() == "x ^ 3"
        assert simplify("(x^2)^3").to_infix() == "x ^ 6"

    def test_elementary_functions(self):
        assert simplify("sin(0)").to_infix() == "0"
        assert simplify("cos(0)").to_infix() == "1"
        assert simplify("tan(0)").to_infix() == "0"
        assert simplify("ln(1)").to_infix() == "0"
        assert simplify("exp(0)").to_infix() == "1"
        assert simplify("ln(exp(x))").to_infix() == "x"
        assert simplify("exp(ln(x))").to_infix() == "x"


class TestDifferentiation:
    """Test differentiation rules, step tracking, and calculus utilities."""

    def test_power_and_polynomial_derivatives(self):
        res = diff("3*x^5 - 4*x^2 + 7*x - 12", "x")
        # 15*x^4 - 8*x + 7
        assert math.isclose(res.evaluate({"x": 2}), 15 * (2**4) - 8 * 2 + 7)

    def test_product_rule(self):
        res = diff("sin(x) * cos(x)", "x")
        # cos(x)*cos(x) - sin(x)*sin(x) = cos(2x)
        val = res.evaluate({"x": 0.5})
        expected = math.cos(0.5)**2 - math.sin(0.5)**2
        assert math.isclose(val, expected, abs_tol=1e-6)

    def test_quotient_rule(self):
        res = diff("(x^2 + 1) / (x^3 - 1)", "x")
        val = res.evaluate({"x": 2.0})
        # (2x*(x^3-1) - (x^2+1)*3x^2) / (x^3-1)^2
        # (4*7 - 5*12) / 49 = (28 - 60) / 49 = -32 / 49
        assert math.isclose(val, -32.0 / 49.0, abs_tol=1e-6)

    def test_chain_rule(self):
        res = diff("sin(cos(tan(x)))", "x")
        # Check numerical evaluation at x = 0.2
        val = res.evaluate({"x": 0.2})
        t = math.tan(0.2)
        c = math.cos(t)
        expected = math.cos(c) * (-math.sin(t)) * (1 / math.cos(0.2)**2)
        assert math.isclose(val, expected, abs_tol=1e-6)

    def test_derivation_tracker(self):
        tracker = DerivationTracker()
        res = diff("x^2 * sin(x)", "x", tracker=tracker)
        steps = tracker.get_steps()
        assert len(steps) > 0
        text = tracker.format_text()
        assert "Product Rule" in text
        assert "Power Rule" in text
        assert "Chain Rule" in text

    def test_higher_derivatives(self):
        d1 = diff("sin(x)", "x", order=1)
        d2 = diff("sin(x)", "x", order=2)
        d3 = diff("sin(x)", "x", order=3)
        d4 = diff("sin(x)", "x", order=4)
        assert d1.to_infix() == "cos(x)"
        assert d2.to_infix() == "-sin(x)"
        assert d3.to_infix() == "-cos(x)"
        assert d4.to_infix() == "sin(x)"

    def test_multivariable_calculus(self):
        grad = gradient("x^2 + 3*y^2", ["x", "y"])
        assert grad[0].to_infix() == "2 * x"
        assert grad[1].to_infix() == "6 * y"

        h = hessian("x^2 + 3*y^2", ["x", "y"])
        assert h[0][0].evaluate() == 2
        assert h[0][1].evaluate() == 0
        assert h[1][0].evaluate() == 0
        assert h[1][1].evaluate() == 6

    def test_taylor_series(self):
        taylor = taylor_series("exp(x)", "x", x0=0.0, order=3)
        val = taylor.evaluate({"x": 0.1})
        expected = 1 + 0.1 + (0.1**2)/2 + (0.1**3)/6
        assert math.isclose(val, expected, abs_tol=1e-5)

    def test_tangent_line(self):
        slope, b, eq = tangent_line("x^2", x0=2.0, var="x")
        assert math.isclose(slope, 4.0)
        assert math.isclose(b, -4.0)
        assert "y = 4.0000*x - 4.0000" in eq


class TestLimits:
    """Test limit computation engine."""

    def test_direct_substitution(self):
        assert limit("x^2 + 3*x + 2", "x", point=2) == 12

    def test_lhopital_0_over_0(self):
        assert math.isclose(limit("sin(x)/x", "x", point=0), 1.0)
        assert math.isclose(limit("(1 - cos(x))/x^2", "x", point=0), 0.5)
        assert math.isclose(limit("(x^2 - 1)/(x - 1)", "x", point=1), 2.0)
        assert math.isclose(limit("(exp(x) - 1)/x", "x", point=0), 1.0)


class TestIntegration:
    """Test indefinite and definite symbolic integration."""

    def test_polynomial_integration(self):
        anti = integrate("x^4 - 2*x + 1", "x")
        # d/dx of anti should evaluate to integrand
        d_anti = diff(anti, "x")
        for test_x in [0.5, 1.0, 2.0]:
            assert math.isclose(d_anti.evaluate({"x": test_x}), (test_x**4 - 2*test_x + 1), abs_tol=1e-6)

    def test_trigonometric_and_exponential_integration(self):
        anti_sin = integrate("sin(3*x)", "x")
        anti_exp = integrate("exp(2*x)", "x")
        assert math.isclose(diff(anti_sin, "x").evaluate({"x": 0.3}), math.sin(3 * 0.3), abs_tol=1e-6)
        assert math.isclose(diff(anti_exp, "x").evaluate({"x": 0.3}), math.exp(2 * 0.3), abs_tol=1e-6)

    def test_integration_by_parts(self):
        anti_parts = integrate("x * exp(x)", "x")
        # (x - 1) * exp(x)
        assert math.isclose(diff(anti_parts, "x").evaluate({"x": 1.5}), 1.5 * math.exp(1.5), abs_tol=1e-6)

    def test_definite_integration(self):
        res1 = definite_integrate("x^2", "x", 0, 3)
        assert math.isclose(res1, 9.0, abs_tol=1e-5)

        res2 = definite_integrate("sin(x)", "x", 0, math.pi)
        assert math.isclose(res2, 2.0, abs_tol=1e-5)
