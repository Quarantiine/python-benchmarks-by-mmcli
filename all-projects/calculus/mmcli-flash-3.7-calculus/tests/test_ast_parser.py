"""
Unit Tests for AST Node Hierarchy and Mathematical Parser
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
from parser import (
    Parser, ParseError, parse, parse_expr, parse_expression,
    evaluate_expression, Lexer, TokenType
)


class TestASTNodes:
    def test_constant_node(self):
        c1 = Constant(5)
        c2 = Constant(5.0)
        c3 = Constant(Fraction(1, 2))
        assert c1.evaluate() == 5.0
        assert c2.evaluate() == 5.0
        assert c3.evaluate() == 0.5
        assert c1.is_zero() is False
        assert Constant(0).is_zero() is True
        assert Constant(1).is_one() is True
        assert Constant(-1).is_negative_one() is True
        assert c1.to_infix() == "5"
        assert c3.to_infix() == "1/2"
        assert c1.differentiate("x") == Constant(0)
        assert c1.variables() == set()

    def test_named_constant(self):
        assert PI.evaluate() == pytest.approx(math.pi)
        assert E.evaluate() == pytest.approx(math.e)
        assert TAU.evaluate() == pytest.approx(2 * math.pi)
        assert PI.to_infix() == "pi"
        assert PI.to_latex() == "\\pi"
        assert PI.differentiate("x") == Constant(0)

    def test_variable_node(self):
        v = Variable("x")
        assert v.evaluate({"x": 3.5}) == 3.5
        with pytest.raises(KeyError):
            v.evaluate({"y": 2.0})
        assert v.to_infix() == "x"
        assert v.to_latex() == "x"
        assert v.variables() == {"x"}
        assert v.differentiate("x") == Constant(1)
        assert v.differentiate("y") == Constant(0)

    def test_arithmetic_overloads(self):
        x = Variable("x")
        expr = (x + 2) * (x - 3) / 4 ** x
        assert isinstance(expr, Divide)
        assert isinstance(expr.left, Multiply)
        assert isinstance(expr.right, Power)
        assert expr.variables() == {"x"}

    def test_unary_operations(self):
        x = Variable("x")
        neg = -x
        assert isinstance(neg, Negate)
        assert neg.evaluate({"x": 7}) == -7
        assert neg.to_infix() == "-x"
        assert neg.differentiate("x").evaluate({"x": 10}) == -1

    def test_binary_evaluation(self):
        x = Variable("x")
        env = {"x": 3}
        assert (x + 4).evaluate(env) == 7
        assert (x - 5).evaluate(env) == -2
        assert (x * 6).evaluate(env) == 18
        assert (x / 2).evaluate(env) == 1.5
        assert (x ** 2).evaluate(env) == 9

    def test_elementary_functions_eval(self):
        x = Variable("x")
        env = {"x": 0.5}
        assert Sin(x).evaluate(env) == pytest.approx(math.sin(0.5))
        assert Cos(x).evaluate(env) == pytest.approx(math.cos(0.5))
        assert Tan(x).evaluate(env) == pytest.approx(math.tan(0.5))
        assert Exp(x).evaluate(env) == pytest.approx(math.exp(0.5))
        assert Ln(x).evaluate(env) == pytest.approx(math.log(0.5))
        assert Sqrt(x).evaluate(env) == pytest.approx(math.sqrt(0.5))
        assert Abs(x - 2).evaluate(env) == 1.5

    def test_tree_rendering(self):
        x = Variable("x")
        expr = (x ** 2) + 3 * x
        tree_str = expr.to_tree_string()
        assert "Add (+)" in tree_str
        assert "Power (^)" in tree_str
        assert "Variable(x)" in tree_str


class TestParser:
    def test_basic_arithmetic(self):
        ast = parse("3 + 4 * 2")
        assert ast.evaluate() == 11
        ast2 = parse("(3 + 4) * 2")
        assert ast2.evaluate() == 14

    def test_operator_precedence(self):
        # 2 + 3 * 4 ^ 2 -> 2 + 3 * 16 -> 2 + 48 = 50
        ast = parse("2 + 3 * 4 ^ 2")
        assert ast.evaluate() == 50

    def test_power_right_associativity(self):
        # 2 ^ 3 ^ 2 == 2 ^ (3 ^ 2) == 2 ^ 9 == 512
        ast = parse("2 ^ 3 ^ 2")
        assert ast.evaluate() == 512

    def test_implicit_multiplication(self):
        env = {"x": 4}
        assert parse("3x").evaluate(env) == 12
        assert parse("3(x + 1)").evaluate(env) == 15
        assert parse("(x + 1)(x - 1)").evaluate(env) == 15
        assert parse("2x^2").evaluate(env) == 32  # 2 * (4^2)

    def test_unicode_superscripts(self):
        env = {"x": 3}
        ast = parse("x² + 2x + 1")
        assert ast.evaluate(env) == 16
        ast2 = parse("x⁻¹")
        assert ast2.evaluate(env) == pytest.approx(1/3)

    def test_bare_functions_and_compound_ident(self):
        env = {"x": math.pi / 6}
        # cos 3x -> cos(3 * pi/6) = cos(pi/2) = 0
        ast = parse("cos3x")
        assert ast.evaluate(env) == pytest.approx(0.0, abs=1e-7)
        ast2 = parse("sin x")
        assert ast2.evaluate(env) == pytest.approx(0.5)

    def test_benchmark_expressions(self):
        cases = [
            ("3*x^5 - 4*x^2 + 7*x - 12", {"x": 2}, 3*32 - 4*4 + 14 - 12),
            ("(2*x + 5)^4", {"x": 1}, 7**4),
            ("(x^2 + 1) * (3*x^3 - 2)", {"x": 1}, 2 * 1),
            ("sin(x) * cos(x)", {"x": 0.5}, math.sin(0.5) * math.cos(0.5)),
            ("tan(x^2 + 1)", {"x": 0.5}, math.tan(0.25 + 1)),
            ("asin(x) + acos(x)", {"x": 0.5}, math.pi / 2),
            ("tan(x)^2 + 1", {"x": 0.5}, math.tan(0.5)**2 + 1),
            ("exp(3*x) * (x^2 - 2*x + 2)", {"x": 0.5}, math.exp(1.5) * (0.25 - 1.0 + 2)),
            ("ln(x^2 + 1) / x", {"x": 2.0}, math.log(5.0) / 2.0),
            ("sqrt(1 + sin(x)^2)", {"x": 0.5}, math.sqrt(1 + math.sin(0.5)**2)),
            ("1 / sqrt(4 - x^2)", {"x": 1.0}, 1 / math.sqrt(3.0)),
        ]
        for expr_str, env, expected in cases:
            ast = parse(expr_str)
            assert ast.evaluate(env) == pytest.approx(expected, rel=1e-4)

    def test_pipe_absolute_value(self):
        assert parse("|x - 5|").evaluate({"x": 2}) == 3
        assert parse("|-7|").evaluate() == 7

    def test_scientific_notation(self):
        assert parse("1.5e2").evaluate() == 150.0
        assert parse("2E-2").evaluate() == 0.02

    def test_syntax_errors(self):
        invalid_expressions = [
            "sin(x",
            "x = 2",
            "(3 + 4",
            "3 + +",
            "3 * * 2",
            "",
            "   ",
            "/ 5",
            "^ 2",
        ]
        for inv in invalid_expressions:
            with pytest.raises(ParseError):
                parse(inv)

    def test_evaluate_expression_helper(self):
        assert evaluate_expression("x^2 + 3", {"x": 4}) == 19
        ast = parse("2*x + 1")
        assert evaluate_expression(ast, {"x": 5}) == 11
