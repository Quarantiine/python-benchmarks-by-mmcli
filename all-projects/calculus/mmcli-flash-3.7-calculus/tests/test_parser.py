"""
Comprehensive Unit Tests for Mathematical Expression Pratt Parser
"""

import math
import pytest
from fractions import Fraction

from ast_nodes import (
    Constant, Variable, Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs
)
from parser import (
    Parser, ParseError, parse, parse_expr, parse_expression,
    evaluate_expression, Lexer, TokenType, Token
)


class TestParser:
    """Test Pratt parser tokenization, operator precedence, and mathematical features."""

    def test_lexer_tokens(self):
        lexer = Lexer("3.14 + x * sin(y)")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        assert types == [
            TokenType.NUMBER,
            TokenType.PLUS,
            TokenType.IDENT,
            TokenType.STAR,
            TokenType.IDENT,
            TokenType.LPAREN,
            TokenType.IDENT,
            TokenType.RPAREN,
            TokenType.EOF
        ]

    def test_basic_arithmetic_precedence(self):
        # Multiplications and divisions take precedence over additions and subtractions
        ast1 = parse("2 + 3 * 4")
        assert ast1.evaluate() == 14

        ast2 = parse("2 * 3 + 4")
        assert ast2.evaluate() == 10

        ast3 = parse("10 - 4 - 2")
        # Left associative: (10 - 4) - 2 = 4
        assert ast3.evaluate() == 4

        ast4 = parse("24 / 4 / 2")
        # Left associative: (24 / 4) / 2 = 3
        assert ast4.evaluate() == 3

    def test_power_right_associativity(self):
        # 2 ^ 3 ^ 2 == 2 ^ (3 ^ 2) == 2 ^ 9 == 512
        ast = parse("2 ^ 3 ^ 2")
        assert ast.evaluate() == 512

        # (2 ^ 3) ^ 2 == 8 ^ 2 == 64
        ast_bracketed = parse("(2 ^ 3) ^ 2")
        assert ast_bracketed.evaluate() == 64

    def test_implicit_multiplication(self):
        env = {"x": 3.0, "y": 4.0}

        assert parse("2x").evaluate(env) == 6.0
        assert parse("2(x + 1)").evaluate(env) == 8.0
        assert parse("(x + 1)(y + 1)").evaluate(env) == 20.0
        assert parse("2x^2").evaluate(env) == 18.0  # 2 * (3^2)
        assert parse("x y").evaluate(env) == 12.0
        assert parse("2 sin(x)").evaluate({"x": 0.0}) == 0.0

    def test_unicode_superscripts(self):
        env = {"x": 4.0}
        assert parse("x²").evaluate(env) == 16.0
        assert parse("x³").evaluate(env) == 64.0
        assert parse("x⁴").evaluate(env) == 256.0
        assert parse("x⁻¹").evaluate(env) == 0.25
        assert parse("2x² + 3x + 1").evaluate(env) == 2 * 16 + 3 * 4 + 1

    def test_scientific_notation_and_floats(self):
        assert parse("1e3").evaluate() == 1000.0
        assert parse("2.5e-2").evaluate() == pytest.approx(0.025)
        assert parse("1.23E+4").evaluate() == 12300.0

    def test_trigonometric_and_standard_functions(self):
        env = {"x": math.pi / 4}
        assert parse("sin(x)").evaluate(env) == pytest.approx(math.sin(math.pi / 4))
        assert parse("cos(x)").evaluate(env) == pytest.approx(math.cos(math.pi / 4))
        assert parse("tan(x)").evaluate(env) == pytest.approx(1.0)
        assert parse("exp(0)").evaluate() == 1.0
        assert parse("ln(1)").evaluate() == 0.0
        assert parse("sqrt(16)").evaluate() == 4.0

    def test_bare_functions_and_concatenated_identifiers(self):
        # Functions without parens: e.g. sin x, cos 3x
        env = {"x": math.pi / 6}
        assert parse("sin x").evaluate(env) == pytest.approx(0.5)
        assert parse("cos 3x").evaluate(env) == pytest.approx(0.0, abs=1e-7)

    def test_pipe_absolute_values(self):
        assert parse("| -10 |").evaluate() == 10.0
        assert parse("| 3 - 8 |").evaluate() == 5.0
        assert parse("2 * | -4 | + 1").evaluate() == 9.0

    def test_constants_parsing(self):
        assert parse("pi").evaluate() == pytest.approx(math.pi)
        assert parse("e").evaluate() == pytest.approx(math.e)
        assert parse("tau").evaluate() == pytest.approx(2 * math.pi)

    def test_syntax_errors_rejection(self):
        invalid_expressions = [
            "",
            "   ",
            "sin(",
            "(2 + 3",
            "2 * * 3",
            "x = 2",
            "/ 4",
            "^ 3",
            "3 *",
            "1 + @",
        ]
        for expr_str in invalid_expressions:
            with pytest.raises(ParseError):
                parse(expr_str)

    def test_evaluate_expression_convenience(self):
        assert evaluate_expression("x^2 + y^2", {"x": 3, "y": 4}) == 25.0
        ast = parse("sin(x)")
        assert evaluate_expression(ast, {"x": 0}) == 0.0
