"""
Unit tests for Algebraic Simplification Engine
"""

import pytest
from engine.parser import parse_expr
from engine.simplifier import simplify
from engine.ast_nodes import Constant, Variable


def test_additive_identities():
    assert simplify(parse_expr("x + 0")) == Variable("x")
    assert simplify(parse_expr("0 + x")) == Variable("x")
    assert simplify(parse_expr("x - 0")) == Variable("x")
    assert simplify(parse_expr("0 - x")).to_infix() == "-x"
    assert simplify(parse_expr("x - x")) == Constant(0)


def test_multiplicative_identities():
    assert simplify(parse_expr("x * 1")) == Variable("x")
    assert simplify(parse_expr("1 * x")) == Variable("x")
    assert simplify(parse_expr("x * 0")) == Constant(0)
    assert simplify(parse_expr("0 * x")) == Constant(0)
    assert simplify(parse_expr("x / 1")) == Variable("x")
    assert simplify(parse_expr("0 / x")) == Constant(0)
    assert simplify(parse_expr("x / x")) == Constant(1)


def test_power_identities():
    assert simplify(parse_expr("x ^ 1")) == Variable("x")
    assert simplify(parse_expr("x ^ 0")) == Constant(1)
    assert simplify(parse_expr("1 ^ x")) == Constant(1)
    assert simplify(parse_expr("0 ^ x")) == Constant(0)


def test_constant_folding():
    assert simplify(parse_expr("2 + 3")) == Constant(5)
    assert simplify(parse_expr("10 - 4")) == Constant(6)
    assert simplify(parse_expr("3 * 7")) == Constant(21)
    assert simplify(parse_expr("2 ^ 3")) == Constant(8)
    assert simplify(parse_expr("sin(0)")) == Constant(0)
    assert simplify(parse_expr("cos(0)")) == Constant(1)
    assert simplify(parse_expr("exp(0)")) == Constant(1)
    assert simplify(parse_expr("ln(1)")) == Constant(0)


def test_like_terms_combining():
    assert simplify(parse_expr("x + x")).to_infix() in ("2 * x", "x * 2")
    assert simplify(parse_expr("3*x + 2*x")).to_infix() in ("5 * x", "x * 5")
    assert simplify(parse_expr("5*x - 3*x")).to_infix() in ("2 * x", "x * 2")
    assert simplify(parse_expr("2*x - 2*x")) == Constant(0)


def test_double_negation():
    assert simplify(parse_expr("-(-x)")) == Variable("x")
