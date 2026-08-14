"""
Unit tests for Unicode Braille Graph Plotter
"""

import pytest
from engine.plotter import PlotCanvas, plot_functions, plot_expression
from engine.parser import parse_expr


def test_plot_canvas_set_pixel():
    canvas = PlotCanvas(width=30, height=10, x_min=-2.0, x_max=2.0, y_min=-2.0, y_max=2.0)
    canvas.set_pixel(10, 10, color="cyan")
    assert canvas.grid[2][5] != 0


def test_plot_canvas_render():
    canvas = PlotCanvas(width=40, height=12, x_min=-3.0, x_max=3.0, y_min=-3.0, y_max=3.0)
    canvas.add_curve(lambda x: x ** 2, color="cyan")
    lines = canvas.render_lines()
    assert len(lines) >= 12
    assert any("│" in l for l in lines)
    assert any("└" in l for l in lines)


def test_plot_expression():
    expr = parse_expr("sin(x)")
    plot_str = plot_expression(expr, var="x", include_derivative=True, width=50, height=12)
    assert "f(x) = sin(x)" in plot_str
    assert "f'(x)" in plot_str
