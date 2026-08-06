"""Comprehensive unit test suite for calculus core engine and visualizers."""

import math
import unittest
from core.ast import Constant, Variable, AddNode, SubNode, MulNode, DivNode, PowNode, SinNode, CosNode
from core.parser import parse_expression

from core.simplifier import simplify
from core.differentiator import differentiate_with_steps
from tui.tree_renderer import render_ast_tree
from tui.plotter import render_ascii_plot
from tui.derivation_view import render_derivation_breakdown


class TestCalculusParser(unittest.TestCase):
    """Test expression parsing to AST nodes."""

    def test_basic_arithmetic(self):
        ast = parse_expression("3 + 5 * x")
        self.assertIsInstance(ast, AddNode)
        self.assertEqual(ast.left, Constant(3))
        self.assertIsInstance(ast.right, MulNode)

    def test_implicit_multiplication(self):
        ast = parse_expression("2x + 3sin(x)")
        self.assertIsInstance(ast, AddNode)
        self.assertIsInstance(ast.left, MulNode)
        self.assertIsInstance(ast.right, MulNode)

    def test_functions_and_powers(self):
        ast = parse_expression("x^2 + sin(x)")
        self.assertIsInstance(ast, AddNode)
        self.assertIsInstance(ast.left, PowNode)
        self.assertIsInstance(ast.right, SinNode)


class TestSymbolicDifferentiation(unittest.TestCase):
    """Test differentiation rules and derivations."""

    def test_product_rule(self):
        ast = parse_expression("x * sin(x)")
        raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
        self.assertTrue(any(s.rule_name == "Product Rule" for s in steps))
        # f'(x) = 1*sin(x) + x*cos(x) -> sin(x) + x*cos(x)
        self.assertIn("sin(x)", str(simp_d))

    def test_quotient_rule(self):
        ast = parse_expression("x / (x + 1)")
        raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
        self.assertTrue(any(s.rule_name == "Quotient Rule" for s in steps))

    def test_chain_rule(self):
        ast = parse_expression("sin(x^2)")
        raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
        self.assertIn("cos", str(simp_d))
        self.assertIn("2", str(simp_d))

    def test_power_rule(self):
        ast = parse_expression("x^3")
        raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
        self.assertEqual(str(simp_d), "3 * x ^ 2")


class TestSimplifier(unittest.TestCase):
    """Test recursive AST simplification rules."""

    def test_identity_and_zero_rules(self):
        ast1 = parse_expression("0 + x * 1")
        self.assertEqual(str(simplify(ast1)), "x")

        ast2 = parse_expression("0 * sin(x) + 5")
        self.assertEqual(str(simplify(ast2)), "5")

    def test_constant_folding(self):
        ast = parse_expression("2 + 3 * 4")
        self.assertEqual(str(simplify(ast)), "14")


class TestEvaluator(unittest.TestCase):
    """Test numerical evaluation of AST."""

    def test_numerical_eval(self):
        ast = parse_expression("x^2 + 2*x + 1")
        val = ast.evaluate({"x": 3})
        self.assertEqual(val, 16.0)


class TestTUIComponents(unittest.TestCase):
    """Test visualizers and renderers."""

    def test_tree_renderer(self):
        ast = parse_expression("x^2 + 1")
        tree_str = render_ast_tree(ast)
        self.assertIn("AddNode (+)", tree_str)
        self.assertIn("PowNode (^)", tree_str)

    def test_plotter(self):
        ast = parse_expression("x^2")
        raw_d, simp_d, _ = differentiate_with_steps(ast, "x")
        plot_str = render_ascii_plot(ast, simp_d, "x", -2.0, 2.0)
        self.assertIn("Terminal Graph Plotter", plot_str)

    def test_derivation_view(self):
        ast = parse_expression("x^2")
        raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
        report = render_derivation_breakdown("x^2", str(raw_d), str(simp_d), steps)
        self.assertIn("STEP-BY-STEP DERIVATION BREAKDOWN", report)


class TestNewFeatures(unittest.TestCase):
    """Test inverse trig, function prefix splitting, integration, and limits."""

    def test_inverse_trig_differentiation(self):
        ast = parse_expression("asin(x) + acos(x)")
        _, simp_d, _ = differentiate_with_steps(ast, "x")
        # Derivatives cancel out to 0 numerically or symbolically
        self.assertAlmostEqual(simp_d.evaluate({"x": 0.5}), 0.0, places=5)

    def test_func_prefix_splitting(self):
        ast = parse_expression("cos3x")
        _, simp_d, _ = differentiate_with_steps(ast, "x")
        self.assertAlmostEqual(simp_d.evaluate({"x": 0.0}), 0.0, places=5)
        self.assertAlmostEqual(simp_d.evaluate({"x": 1.0}), -3.0 * math.sin(3.0), places=5)

    def test_integration(self):
        from core.integrator import integrate, definite_integrate
        ast = parse_expression("x^4 - 2*x + 1")
        antideriv = integrate(ast, "x")
        self.assertIn("x", str(antideriv))
        val = definite_integrate(parse_expression("x^2"), "x", 0, 3)
        self.assertAlmostEqual(val, 9.0, places=4)

    def test_limits(self):
        from core.limits import limit
        val1 = limit(parse_expression("sin(x)/x"), "x", 0)
        self.assertAlmostEqual(val1, 1.0, places=5)
        val2 = limit(parse_expression("(1 - cos(x))/x^2"), "x", 0)
        self.assertAlmostEqual(val2, 0.5, places=5)


if __name__ == "__main__":
    import math
    unittest.main()

