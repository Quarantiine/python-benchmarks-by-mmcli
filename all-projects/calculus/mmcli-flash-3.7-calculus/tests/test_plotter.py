"""
Comprehensive Unit Tests for Terminal Unicode/Braille and ASCII Plotters
"""

import math
import pytest

from parser import parse_expr
from plotter import (
    PlotCanvas, AsciiCanvas, plot_functions, plot_expression,
    render_braille_plot, render_ascii_plot, plot_curve
)


class TestPlotter:
    """Test Braille and ASCII terminal curve renderers."""

    def test_plot_canvas_pixel_setting(self):
        canvas = PlotCanvas(width=30, height=10, x_min=-2.0, x_max=2.0, y_min=-2.0, y_max=2.0)
        canvas.set_pixel(10, 10, color="cyan")
        assert canvas.grid[2][5] != 0

    def test_plot_canvas_render_lines(self):
        canvas = PlotCanvas(width=40, height=12, x_min=-3.0, x_max=3.0, y_min=-3.0, y_max=3.0)
        canvas.add_curve(lambda x: x**2, color="cyan", label="f(x)=x^2")
        lines = canvas.render_lines(use_color=False)
        assert len(lines) >= 12
        assert any("│" in l for l in lines)
        assert any("└" in l for l in lines)

    def test_ascii_canvas(self):
        canvas = AsciiCanvas(width=40, height=10, x_min=-2.0, x_max=2.0, y_min=-1.0, y_max=1.0)
        canvas.add_curve(math.sin, symbol="*", label="sin(x)")
        lines = canvas.render_lines()
        assert len(lines) >= 10
        assert any("*" in l for l in lines)
        assert any("+" in l or "|" in l for l in lines)

    def test_plot_expression_braille_and_ascii(self):
        expr = parse_expr("sin(x)")
        braille_plot = plot_expression(expr, var="x", include_derivative=True, width=50, height=12)
        assert "sin(x)" in braille_plot
        assert "cos(x)" in braille_plot

        ascii_plot = plot_expression(expr, var="x", include_derivative=True, ascii_mode=True, width=50, height=12)
        assert "sin(x)" in ascii_plot

    def test_render_braille_with_tangent_line(self):
        expr = parse_expr("x^2")
        d_expr = parse_expr("2*x")
        tangent_fn = lambda x: 4.0 * x - 4.0
        plot_str = render_braille_plot(expr, "x", d_expr=d_expr, tangent_fn=tangent_fn)
        assert "x ^ 2" in plot_str
        assert "2 * x" in plot_str

    def test_plot_curve_helper(self):
        result = plot_curve(lambda x: math.cos(x), label="cos(x)", x_min=-3.14, x_max=3.14)
        assert "cos(x)" in result
