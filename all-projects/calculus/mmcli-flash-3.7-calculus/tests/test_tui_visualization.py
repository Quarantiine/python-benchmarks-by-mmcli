"""
Unit and Integration Tests for Visualization, Plotter, Tree Renderer, Derivation Viewer, TUI, and CLI
"""

import math
import sys
import unittest
from parser import parse_expr
from ast_nodes import Node, Constant, Variable, Add, Sin, Cos
from plotter import (
    PlotCanvas, AsciiCanvas, plot_functions, plot_expression,
    render_braille_plot, render_ascii_plot, plot_curve
)
from tree_renderer import (
    render_ast_tree, render_ascii_tree, render_tree,
    render_pretty, to_latex, ASTVisualizer
)
from derivation_view import (
    render_derivation_breakdown, format_derivation_steps,
    DerivationViewer
)
from tui_core import StepByStepEngine, SymbolicCalculusTUI
from cli import run_cli


class TestPlotter(unittest.TestCase):
    def test_plot_canvas_basics(self):
        canvas = PlotCanvas(width=40, height=10, x_min=-2.0, x_max=2.0, y_min=-1.0, y_max=1.0)
        canvas.set_pixel(0, 0)
        canvas.set_pixel(10, 10)
        lines = canvas.render_lines(use_color=False)
        self.assertGreater(len(lines), 10)
        self.assertTrue(any("│" in l for l in lines))

    def test_plot_canvas_curve(self):
        canvas = PlotCanvas(width=50, height=12, x_min=-3.14, x_max=3.14, y_min=-1.5, y_max=1.5)
        canvas.add_curve(math.sin)
        lines = canvas.render_lines(use_color=False)
        self.assertGreater(len(lines), 12)

    def test_ascii_canvas(self):
        canvas = AsciiCanvas(width=40, height=10, x_min=-2.0, x_max=2.0, y_min=-1.0, y_max=1.0)
        canvas.add_curve(math.sin, symbol="*")
        lines = canvas.render_lines()
        self.assertGreater(len(lines), 10)
        self.assertTrue(any("*" in l for l in lines))

    def test_plot_expression(self):
        expr = parse_expr("cos(x)")
        braille_out = plot_expression(expr, var="x", include_derivative=True, x_min=-3.14, x_max=3.14)
        self.assertIn("cos(x)", braille_out)
        self.assertIn("-sin(x)", braille_out)

        ascii_out = plot_expression(expr, var="x", include_derivative=True, ascii_mode=True)
        self.assertIn("cos(x)", ascii_out)

    def test_render_braille_and_ascii_helpers(self):
        expr = parse_expr("x^2")
        d1 = parse_expr("2*x")
        d2 = parse_expr("2")
        b_plot = render_braille_plot(expr, "x", d_expr=d1, d2_expr=d2)
        self.assertIn("x ^ 2", b_plot)
        self.assertIn("2 * x", b_plot)

        a_plot = render_ascii_plot(expr, "x", d_expr=d1)
        self.assertIn("x ^ 2", a_plot)

    def test_plot_curve_callable(self):
        out = plot_curve(lambda x: x**3, label="cube", x_min=-2, x_max=2)
        self.assertIn("cube", out)


class TestTreeRenderer(unittest.TestCase):
    def test_unicode_ast_tree(self):
        expr = parse_expr("sin(x^2) / (x + 1)")
        tree_str = render_ast_tree(expr)
        self.assertIn("Divide (/)", tree_str)
        self.assertIn("Sin (sin)", tree_str)
        self.assertIn("Power (^)", tree_str)
        self.assertIn("└──", tree_str)
        self.assertIn("├──", tree_str)

    def test_ascii_ast_tree(self):
        expr = parse_expr("sin(x^2) / (x + 1)")
        tree_str = render_ascii_tree(expr)
        self.assertIn("Divide (/)", tree_str)
        self.assertIn("+--", tree_str)
        self.assertIn("\\--", tree_str)

    def test_render_pretty_modes(self):
        expr = parse_expr("x^2 + 2*x + 1")
        uni = render_pretty(expr, "unicode")
        self.assertIn("x²", uni)

        ascii_s = render_pretty(expr, "ascii")
        self.assertIn("x ^ 2", ascii_s)

        latex_s = render_pretty(expr, "latex")
        self.assertIn("{x}^{2}", latex_s)

    def test_ast_visualizer(self):
        expr = parse_expr("exp(x)")
        boxed = ASTVisualizer.render_horizontal_boxed(expr)
        self.assertIn("┌", boxed)
        self.assertIn("e^(x)", boxed)


class TestDerivationView(unittest.TestCase):
    def test_derivation_viewer_explain(self):
        res = DerivationViewer.explain("sin(x^2)", var="x", order=1)
        self.assertTrue(res["report_text"])
        self.assertIn("STEP-BY-STEP DERIVATION BREAKDOWN", res["report_text"])
        self.assertIn("CHAIN RULE", res["report_text"].upper())
        self.assertIn("cos", res["result_expr"].to_infix())

    def test_render_derivation_breakdown_empty(self):
        out = render_derivation_breakdown("x", "1", "1", steps=[])
        self.assertIn("No intermediate derivation steps recorded", out)


class TestTUIAndCLI(unittest.TestCase):
    def test_step_by_step_engine(self):
        # Diff
        d_res = StepByStepEngine.explain_diff("exp(2*x)", "x", order=1)
        self.assertTrue(d_res["success"])
        self.assertIn("e^(2x)", d_res["unicode"])

        # Integrate
        i_res = StepByStepEngine.explain_integrate("x^2", "x", "0", "3")
        self.assertTrue(i_res["success"])
        self.assertAlmostEqual(i_res["result_expr"], 9.0, places=2)

        # Limit
        l_res = StepByStepEngine.explain_limit("sin(x)/x", "x", "0")
        self.assertTrue(l_res["success"])
        self.assertAlmostEqual(float(l_res["result_expr"]), 1.0, places=3)

        # Simplify
        s_res = StepByStepEngine.explain_simplify("0 + x * 1")
        self.assertTrue(s_res["success"])
        self.assertEqual(s_res["result_expr"].to_infix(), "x")

        # Eval
        e_res = StepByStepEngine.explain_eval("x^2 + 5", {"x": 3.0})
        self.assertTrue(e_res["success"])
        self.assertEqual(e_res["result_expr"], 14.0)

    def test_tui_state_manager(self):
        tui = SymbolicCalculusTUI()
        tui.expr_str = "x^3"
        for i in range(len(tui.OPERATIONS)):
            tui.selected_op_idx = i
            res = tui.compute_current()
            self.assertTrue(res.get("success"), f"Failed for index {i}")

    def test_cli_execution_flags(self):
        # CLI with --steps and --tree
        code = run_cli(["x^2 + 3*x", "--diff", "x", "--steps", "--tree"])
        self.assertEqual(code, 0)

        # CLI with --plot and --eval
        code = run_cli(["cos(x)", "--eval", "0", "--tangent", "0", "--plot"])
        self.assertEqual(code, 0)

        # CLI with --integral
        code = run_cli(["x", "--integral", "0", "2"])
        self.assertEqual(code, 0)

        # CLI with --taylor and --roots and --critical
        code = run_cli(["x^3 - 3*x", "--taylor", "3", "--roots", "--critical"])
        self.assertEqual(code, 0)

        # CLI with --limit
        code = run_cli(["sin(x)/x", "--limit", "0"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
