"""
Comprehensive Unit Tests for Algebraic Simplification and Rule Reduction
"""

import math
import pytest
from fractions import Fraction

from ast_nodes import Constant, Variable, Add, Subtract, Multiply, Divide, Power, Sin, Cos
from parser import parse_expr
from simplifier import simplify, deep_simplify


class TestSimplifier:
    """Test algebraic simplification rules, constant folding, and identity elimination."""

    def test_constant_folding(self):
        assert simplify("5 + 7").to_infix() == "12"
        assert simplify("15 - 8").to_infix() == "7"
        assert simplify("4 * 6").to_infix() == "24"
        assert simplify("20 / 4").to_infix() == "5"
        assert simplify("2 ^ 3").to_infix() == "8"
        assert simplify("1/2 + 1/3").to_infix() == "5/6"

    def test_additive_identities(self):
        assert simplify("x + 0").to_infix() == "x"
        assert simplify("0 + x").to_infix() == "x"
        assert simplify("x - 0").to_infix() == "x"
        assert simplify("0 - x").to_infix() == "-x"
        assert simplify("x - x").to_infix() == "0"
        assert simplify("x + (-x)").to_infix() == "0"
        assert simplify("(-x) + x").to_infix() == "0"

    def test_multiplicative_identities(self):
        assert simplify("x * 1").to_infix() == "x"
        assert simplify("1 * x").to_infix() == "x"
        assert simplify("x * 0").to_infix() == "0"
        assert simplify("0 * x").to_infix() == "0"
        assert simplify("x / 1").to_infix() == "x"
        assert simplify("0 / x").to_infix() == "0"
        assert simplify("x / x").to_infix() == "1"

    def test_power_rules(self):
        assert simplify("x ^ 1").to_infix() == "x"
        assert simplify("x ^ 0").to_infix() == "1"
        assert simplify("1 ^ x").to_infix() == "1"
        assert simplify("0 ^ x").to_infix() == "0"
        assert simplify("x ^ 2 * x ^ 3").to_infix() == "x ^ 5"
        assert simplify("x ^ 5 / x ^ 2").to_infix() == "x ^ 3"
        assert simplify("(x ^ 2) ^ 3").to_infix() == "x ^ 6"

    def test_like_terms_collection(self):
        assert simplify("3*x + 4*x").to_infix() == "7 * x"
        assert simplify("5*x - 2*x").to_infix() == "3 * x"
        assert simplify("x + x").to_infix() == "2 * x"
        assert simplify("2*x - 2*x").to_infix() == "0"

    def test_double_negation(self):
        assert simplify("-(-x)").to_infix() == "x"
        assert simplify("-(-5)").to_infix() == "5"

    def test_transcendental_simplifications(self):
        assert simplify("sin(0)").to_infix() == "0"
        assert simplify("cos(0)").to_infix() == "1"
        assert simplify("tan(0)").to_infix() == "0"
        assert simplify("exp(0)").to_infix() == "1"
        assert simplify("ln(1)").to_infix() == "0"
        assert simplify("ln(exp(x))").to_infix() == "x"
        assert simplify("exp(ln(x))").to_infix() == "x"
        assert simplify("sqrt(0)").to_infix() == "0"
        assert simplify("sqrt(1)").to_infix() == "1"

    def test_nested_complex_simplifications(self):
        expr = parse_expr("((x + 0) * 1 + 0) / 1")
        assert simplify(expr).to_infix() == "x"

        expr2 = parse_expr("0 * sin(x^2 + 1) + 1 * cos(0)")
        assert simplify(expr2).to_infix() == "1"

    def test_deep_simplify_convergence(self):
        expr = parse_expr("(x * 1 + 0) * (y / 1 - 0) + (x - x)")
        res = deep_simplify(expr)
        assert res.to_infix() == "x * y"
