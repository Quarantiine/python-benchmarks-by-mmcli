"""
Comprehensive Unit Tests for Symbolic Differentiation and Multivariable Calculus
"""

import math
import pytest

from parser import parse_expr
from simplifier import simplify
from differentiator import (
    diff, higher_derivative, partial_derivatives,
    gradient, hessian, taylor_series,
    tangent_line, critical_points, newton_raphson
)
from tracker import DerivationTracker


class TestDifferentiation:
    """Test differentiation rules, multivariable calculus, and numerical utilities."""

    def test_polynomial_derivatives(self):
        res = diff("3*x^5 - 4*x^2 + 7*x - 12", "x")
        # 15*x^4 - 8*x + 7
        for test_val in [-2.0, 0.0, 1.5, 3.0]:
            expected = 15 * (test_val**4) - 8 * test_val + 7
            assert res.evaluate({"x": test_val}) == pytest.approx(expected, rel=1e-5)

    def test_fractional_and_negative_powers(self):
        res = diff("x^(-3) + x^(-0.5)", "x")
        for test_val in [0.5, 1.0, 2.0]:
            expected = -3 * (test_val**-4) - 0.5 * (test_val**-1.5)
            assert res.evaluate({"x": test_val}) == pytest.approx(expected, rel=1e-5)

    def test_product_rule(self):
        res = diff("sin(x) * cos(x)", "x")
        # cos(x)^2 - sin(x)^2
        val = res.evaluate({"x": 0.5})
        assert val == pytest.approx(math.cos(0.5)**2 - math.sin(0.5)**2, rel=1e-5)

    def test_quotient_rule(self):
        res = diff("(x^2 + 1) / (x^3 - 1)", "x")
        val = res.evaluate({"x": 2.0})
        # (2*2*(8-1) - (4+1)*3*4) / (8-1)^2 = (28 - 60) / 49 = -32/49
        assert val == pytest.approx(-32.0 / 49.0, rel=1e-5)

    def test_chain_rule_deep_nesting(self):
        res = diff("sin(cos(tan(x)))", "x")
        x_val = 0.2
        expected = -math.cos(math.cos(math.tan(x_val))) * math.sin(math.tan(x_val)) * (1.0 / math.cos(x_val)**2)
        assert res.evaluate({"x": x_val}) == pytest.approx(expected, rel=1e-5)

    def test_trigonometric_and_inverse_trig(self):
        assert diff("sin(x)", "x").evaluate({"x": 0.3}) == pytest.approx(math.cos(0.3))
        assert diff("cos(x)", "x").evaluate({"x": 0.3}) == pytest.approx(-math.sin(0.3))
        assert diff("tan(x)", "x").evaluate({"x": 0.3}) == pytest.approx(1.0 / (math.cos(0.3)**2))

        # asin(x) -> 1/sqrt(1-x^2), acos(x) -> -1/sqrt(1-x^2), atan(x) -> 1/(1+x^2)
        d_asin = diff("asin(x)", "x")
        assert d_asin.evaluate({"x": 0.5}) == pytest.approx(1.0 / math.sqrt(1 - 0.25))

        d_atan = diff("atan(x)", "x")
        assert d_atan.evaluate({"x": 0.5}) == pytest.approx(1.0 / (1 + 0.25))

    def test_exponential_and_logarithm(self):
        d_exp = diff("exp(3*x)", "x")
        assert d_exp.evaluate({"x": 1.0}) == pytest.approx(3 * math.exp(3.0))

        d_ln = diff("ln(x^2 + 1)", "x")
        assert d_ln.evaluate({"x": 2.0}) == pytest.approx(2 * 2.0 / (4.0 + 1))

    def test_hyperbolic_derivatives(self):
        assert diff("sinh(x)", "x").evaluate({"x": 1.0}) == pytest.approx(math.cosh(1.0))
        assert diff("cosh(x)", "x").evaluate({"x": 1.0}) == pytest.approx(math.sinh(1.0))
        assert diff("tanh(x)", "x").evaluate({"x": 1.0}) == pytest.approx(1.0 - math.tanh(1.0)**2)

    def test_derivation_tracker(self):
        tracker = DerivationTracker()
        res = diff("x^2 * exp(x)", "x", tracker=tracker)
        steps = tracker.get_steps()
        assert len(steps) > 0
        text = tracker.format_text()
        assert "Product Rule" in text
        assert "Power Rule" in text

    def test_higher_derivatives(self):
        d1 = higher_derivative("x^4", "x", order=1)
        d2 = higher_derivative("x^4", "x", order=2)
        d3 = higher_derivative("x^4", "x", order=3)
        d4 = higher_derivative("x^4", "x", order=4)
        d5 = higher_derivative("x^4", "x", order=5)

        assert d1.evaluate({"x": 2}) == 32.0   # 4*x^3
        assert d2.evaluate({"x": 2}) == 48.0   # 12*x^2
        assert d3.evaluate({"x": 2}) == 48.0   # 24*x
        assert d4.evaluate({"x": 2}) == 24.0   # 24
        assert d5.evaluate({"x": 2}) == 0.0    # 0

    def test_multivariable_gradient_and_hessian(self):
        grad = gradient("x^2 + y^2 + 2*x*y", ["x", "y"])
        # df/dx = 2*x + 2*y, df/dy = 2*y + 2*x
        env = {"x": 3.0, "y": 4.0}
        assert grad[0].evaluate(env) == 14.0
        assert grad[1].evaluate(env) == 14.0

        h = hessian("x^3 + 3*x*y^2 + y^3", ["x", "y"])
        # d^2f/dx^2 = 6x, d^2f/dxdy = 6y, d^2f/dydx = 6y, d^2f/dy^2 = 6x + 6y
        assert h[0][0].evaluate(env) == 18.0
        assert h[0][1].evaluate(env) == 24.0
        assert h[1][0].evaluate(env) == 24.0
        assert h[1][1].evaluate(env) == 42.0

    def test_taylor_series_expansion(self):
        # Taylor expansion of cos(x) around 0: 1 - x^2/2 + x^4/24
        poly = taylor_series("cos(x)", "x", x0=0.0, order=4)
        env = {"x": 0.2}
        expected = 1.0 - (0.2**2)/2.0 + (0.2**4)/24.0
        assert poly.evaluate(env) == pytest.approx(expected, rel=1e-5)

    def test_tangent_line(self):
        slope, intercept, eq_str = tangent_line("x^2", x0=3.0, var="x")
        # f'(3) = 6, f(3) = 9 => y = 6*(x - 3) + 9 = 6*x - 9
        assert slope == pytest.approx(6.0)
        assert intercept == pytest.approx(-9.0)
        assert "y = 6.0000*x - 9.0000" in eq_str

    def test_newton_raphson_and_critical_points(self):
        # Root of x^2 - 4 = 0 starting from x0 = 1.0 -> 2.0
        root = newton_raphson("x^2 - 4", "x", x0=1.0)
        assert root == pytest.approx(2.0, abs=1e-5)

        # Critical points of x^3 - 3*x on [-2, 2] -> f'(x) = 3*x^2 - 3 = 0 => x = -1, 1
        crit = critical_points("x^3 - 3*x", "x", x_min=-2.0, x_max=2.0)
        assert len(crit) == 2
        crit_x = sorted([c["x"] for c in crit])
        assert crit_x[0] == pytest.approx(-1.0, abs=1e-2)
        assert crit_x[1] == pytest.approx(1.0, abs=1e-2)
