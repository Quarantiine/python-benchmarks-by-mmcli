"""
Comprehensive Unit Tests for AST Node Representations and Hierarchy
"""

import math
import pytest
from fractions import Fraction

from ast_nodes import (
    Node, Constant, NamedConstant, Variable,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Sec, Csc, Cot,
    Asin, Acos, Atan, Sinh, Cosh, Tanh,
    Exp, Ln, Log, Sqrt, Abs,
    E, PI, TAU, PHI, to_node
)


class TestASTNodes:
    """Test AST Node hierarchy, algebraic properties, evaluation, and representation."""

    def test_constant_initialization_and_evaluation(self):
        c_int = Constant(42)
        c_float = Constant(3.14)
        c_frac = Constant(Fraction(3, 4))

        assert c_int.value == 42
        assert c_int.evaluate() == 42.0
        assert c_float.evaluate() == pytest.approx(3.14)
        assert c_frac.evaluate() == pytest.approx(0.75)
        assert str(c_frac) == "3/4"

    def test_constant_identity_checks(self):
        assert Constant(0).is_zero() is True
        assert Constant(0.0).is_zero() is True
        assert Constant(Fraction(0, 5)).is_zero() is True
        assert Constant(1).is_zero() is False

        assert Constant(1).is_one() is True
        assert Constant(1.0).is_one() is True
        assert Constant(-1).is_negative_one() is True
        assert Constant(-1.0).is_negative_one() is True
        assert Constant(2).is_negative_one() is False

    def test_named_constants(self):
        assert PI.evaluate() == pytest.approx(math.pi)
        assert E.evaluate() == pytest.approx(math.e)
        assert TAU.evaluate() == pytest.approx(2 * math.pi)
        assert PHI.evaluate() == pytest.approx((1 + math.sqrt(5)) / 2)

        assert PI.to_infix() == "pi"
        assert PI.to_latex() == "\\pi"
        assert E.to_latex() == "\\e"
        assert PI.differentiate("x") == Constant(0)

    def test_variable_node(self):
        v_x = Variable("x")
        v_y = Variable("y")

        assert v_x.evaluate({"x": 10.5}) == 10.5
        assert v_y.evaluate({"y": -4.2}) == -4.2

        with pytest.raises(KeyError):
            v_x.evaluate({"z": 1.0})

        assert v_x.variables() == {"x"}
        assert v_x.differentiate("x") == Constant(1)
        assert v_x.differentiate("y") == Constant(0)
        assert v_x.to_infix() == "x"
        assert v_x.to_latex() == "x"

    def test_operator_overloading(self):
        x = Variable("x")
        y = Variable("y")

        add = x + y
        sub = x - y
        mul = x * y
        div = x / y
        pow_node = x ** 2
        neg = -x

        assert isinstance(add, Add)
        assert isinstance(sub, Subtract)
        assert isinstance(mul, Multiply)
        assert isinstance(div, Divide)
        assert isinstance(pow_node, Power)
        assert isinstance(neg, Negate)

        # Reverse operations with numbers
        r_add = 5 + x
        r_sub = 5 - x
        r_mul = 5 * x
        r_div = 5 / x
        r_pow = 2 ** x

        assert isinstance(r_add, Add)
        assert isinstance(r_sub, Subtract)
        assert isinstance(r_mul, Multiply)
        assert isinstance(r_div, Divide)
        assert isinstance(r_pow, Power)

    def test_complex_expression_evaluation(self):
        x = Variable("x")
        expr = (x**2 + 3*x - 4) / (x + 2)
        env = {"x": 2.0}
        # (4 + 6 - 4) / 4 = 6/4 = 1.5
        assert expr.evaluate(env) == pytest.approx(1.5)

    def test_trigonometric_and_hyperbolic_evaluation(self):
        x = Variable("x")
        val = 0.5
        env = {"x": val}

        assert Sin(x).evaluate(env) == pytest.approx(math.sin(val))
        assert Cos(x).evaluate(env) == pytest.approx(math.cos(val))
        assert Tan(x).evaluate(env) == pytest.approx(math.tan(val))
        assert Sec(x).evaluate(env) == pytest.approx(1.0 / math.cos(val))
        assert Csc(x).evaluate(env) == pytest.approx(1.0 / math.sin(val))
        assert Cot(x).evaluate(env) == pytest.approx(1.0 / math.tan(val))

        assert Asin(x).evaluate(env) == pytest.approx(math.asin(val))
        assert Acos(x).evaluate(env) == pytest.approx(math.acos(val))
        assert Atan(x).evaluate(env) == pytest.approx(math.atan(val))

        assert Sinh(x).evaluate(env) == pytest.approx(math.sinh(val))
        assert Cosh(x).evaluate(env) == pytest.approx(math.cosh(val))
        assert Tanh(x).evaluate(env) == pytest.approx(math.tanh(val))

    def test_transcendental_functions(self):
        x = Variable("x")
        env = {"x": 2.0}

        assert Exp(x).evaluate(env) == pytest.approx(math.exp(2.0))
        assert Ln(x).evaluate(env) == pytest.approx(math.log(2.0))
        assert Log(x, Constant(10)).evaluate(env) == pytest.approx(math.log10(2.0))
        assert Sqrt(x).evaluate(env) == pytest.approx(math.sqrt(2.0))
        assert Abs(Constant(-5.5)).evaluate() == 5.5

    def test_to_latex_representation(self):
        x = Variable("x")
        expr = Sin(x**2) / (Cos(x) + 1)
        latex_str = expr.to_latex()
        assert "\\sin" in latex_str
        assert "\\cos" in latex_str
        assert "\\frac" in latex_str

    def test_to_tree_string(self):
        x = Variable("x")
        expr = (x + 1) * (x - 1)
        tree = expr.to_tree_string()
        assert "Multiply (*)" in tree
        assert "Add (+)" in tree
        assert "Subtract (-)" in tree

    def test_node_equality_and_hash(self):
        x1 = Variable("x")
        x2 = Variable("x")
        y = Variable("y")

        assert x1 == x2
        assert x1 != y
        assert hash(x1) == hash(x2)

        c1 = Constant(5)
        c2 = Constant(5.0)
        assert c1 == c2

        add1 = Add(x1, c1)
        add2 = Add(x2, c2)
        assert add1 == add2
        assert hash(add1) == hash(add2)

    def test_to_node_helper(self):
        assert isinstance(to_node(5), Constant)
        assert isinstance(to_node(2.5), Constant)
        assert isinstance(to_node(Fraction(1, 3)), Constant)
        v = Variable("x")
        assert to_node(v) is v
        with pytest.raises(TypeError):
            to_node([1, 2, 3])
