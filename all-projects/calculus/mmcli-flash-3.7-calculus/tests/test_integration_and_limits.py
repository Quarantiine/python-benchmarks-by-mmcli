"""
Comprehensive Unit Tests for Integration and Limit Calculations
"""

import math
import pytest

from parser import parse_expr
from differentiator import diff
from limits import limit, limit_direction
from integrator import integrate, definite_integrate


class TestLimits:
    """Test limit computation engine including direct substitution, L'Hopital's rule, and perturbations."""

    def test_direct_polynomial_substitution(self):
        assert limit("x^2 + 3*x + 2", "x", point=2) == 12.0
        assert limit("x^3 - 8", "x", point=3) == 19.0
        assert limit("exp(x)", "x", point=0) == 1.0

    def test_lhopital_0_over_0_trig(self):
        # sin(x) / x as x -> 0 => 1
        assert limit("sin(x)/x", "x", point=0) == pytest.approx(1.0, abs=1e-5)

        # (1 - cos(x)) / x^2 as x -> 0 => 0.5
        assert limit("(1 - cos(x))/x^2", "x", point=0) == pytest.approx(0.5, abs=1e-5)

        # tan(x) / x as x -> 0 => 1
        assert limit("tan(x)/x", "x", point=0) == pytest.approx(1.0, abs=1e-5)

    def test_lhopital_0_over_0_algebraic_and_exp(self):
        # (x^2 - 1) / (x - 1) as x -> 1 => 2
        assert limit("(x^2 - 1)/(x - 1)", "x", point=1) == pytest.approx(2.0, abs=1e-5)

        # (exp(x) - 1) / x as x -> 0 => 1
        assert limit("(exp(x) - 1)/x", "x", point=0) == pytest.approx(1.0, abs=1e-5)

        # ln(1 + x) / x as x -> 0 => 1
        assert limit("ln(1 + x)/x", "x", point=0) == pytest.approx(1.0, abs=1e-5)

    def test_one_sided_limits(self):
        # |x| / x as x -> 0+ is 1, as x -> 0- is -1
        assert limit_direction("abs(x)/x", "x", point=0.0, direction="+") == pytest.approx(1.0, abs=1e-4)
        assert limit_direction("abs(x)/x", "x", point=0.0, direction="-") == pytest.approx(-1.0, abs=1e-4)


class TestIntegration:
    """Test symbolic antiderivative calculation and definite numerical/analytical integration."""

    def test_polynomial_antiderivatives(self):
        anti = integrate("3*x^2 + 4*x - 5", "x")
        # Differentiating anti gives back original function
        d_anti = diff(anti, "x")
        for sample_x in [0.5, 1.0, 2.0]:
            expected = 3 * sample_x**2 + 4 * sample_x - 5
            assert d_anti.evaluate({"x": sample_x}) == pytest.approx(expected, rel=1e-5)

    def test_power_rule_negative_and_fractional(self):
        anti = integrate("x^(-2)", "x")  # -1/x
        d_anti = diff(anti, "x")
        assert d_anti.evaluate({"x": 2.0}) == pytest.approx(0.25, rel=1e-5)

        # 1/x -> ln(x)
        anti_ln = integrate("1/x", "x")
        assert diff(anti_ln, "x").evaluate({"x": 2.0}) == pytest.approx(0.5, rel=1e-5)

    def test_trigonometric_and_exponential_antiderivatives(self):
        anti_sin = integrate("sin(2*x)", "x")
        assert diff(anti_sin, "x").evaluate({"x": 0.5}) == pytest.approx(math.sin(1.0), rel=1e-5)

        anti_cos = integrate("cos(3*x)", "x")
        assert diff(anti_cos, "x").evaluate({"x": 0.5}) == pytest.approx(math.cos(1.5), rel=1e-5)

        anti_exp = integrate("exp(4*x)", "x")
        assert diff(anti_exp, "x").evaluate({"x": 0.5}) == pytest.approx(math.exp(2.0), rel=1e-5)

    def test_integration_by_parts(self):
        # ∫ x * exp(x) dx = (x - 1) * exp(x)
        anti = integrate("x * exp(x)", "x")
        d_anti = diff(anti, "x")
        for sample_x in [0.5, 1.0, 2.0]:
            assert d_anti.evaluate({"x": sample_x}) == pytest.approx(sample_x * math.exp(sample_x), rel=1e-5)

    def test_definite_integration_exact(self):
        # ∫_0^3 x^2 dx = [x^3/3]_0^3 = 9.0
        val1 = definite_integrate("x^2", "x", lower=0, upper=3)
        assert val1 == pytest.approx(9.0, rel=1e-5)

        # ∫_0^pi sin(x) dx = [-cos(x)]_0^pi = 1 - (-1) = 2.0
        val2 = definite_integrate("sin(x)", "x", lower=0, upper=math.pi)
        assert val2 == pytest.approx(2.0, rel=1e-5)

        # Equal bounds
        val3 = definite_integrate("x^5 + sin(x)", "x", lower=2, upper=2)
        assert val3 == 0.0

    def test_definite_integration_numerical_fallback(self):
        # ∫_0^1 exp(-x^2) dx ≈ 0.7468241328 (erf approximation)
        val = definite_integrate("exp(-x^2)", "x", lower=0, upper=1, method="numeric")
        assert val == pytest.approx(0.746824, abs=1e-4)
