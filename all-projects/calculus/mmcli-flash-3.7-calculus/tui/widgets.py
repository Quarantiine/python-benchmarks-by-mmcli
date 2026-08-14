"""
TUI Custom Widgets for Textual
==============================
Rich components for AST trees, step-by-step derivations, live plots, and calculus analysis.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional

try:
    from textual.widgets import Static, Label
    from textual.containers import Vertical, Horizontal, VerticalScroll
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object  # type: ignore

try:
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree as RichTree
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Panel = None  # type: ignore
    Table = None  # type: ignore
    Text = None  # type: ignore
    RichTree = None  # type: ignore

from ast_nodes import Node
from parser import parse_expr, ParseError
from simplifier import simplify
from differentiator import (
    diff, higher_derivative, taylor_series,
    tangent_line, find_roots_newton, find_all_roots, critical_points
)
from integrator import definite_integrate
from tracker import DerivationTracker
from plotter import plot_functions, plot_expression
from tree_renderer import render_ast_tree, render_pretty, to_latex


class MathOverviewWidget(Static if HAS_TEXTUAL else object):
    """Displays mathematical summary cards for f(x), f'(x), f''(x), tangent, and evaluation."""

    def update_expression(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 1.0,
        order: int = 1,
    ) -> None:
        try:
            d1 = diff(expr, var=var, order=1, simplify_result=True)
            d2 = diff(expr, var=var, order=2, simplify_result=True)

            try:
                y0 = expr.evaluate({var: x0})
                dy0 = d1.evaluate({var: x0})
                d2y0 = d2.evaluate({var: x0})
            except Exception:
                y0, dy0, d2y0 = float("nan"), float("nan"), float("nan")

            slope, b, eq_str = tangent_line(expr, x0=x0, var=var)

            if HAS_RICH:
                table = Table(box=None, expand=True, show_header=False)
                table.add_column("Property", style="bold cyan", width=22)
                table.add_column("Formula / Value", style="bold white")

                table.add_row(
                    f"Input Expression f({var}):",
                    f"[bold bright_cyan]{render_pretty(expr, 'unicode')}[/bold bright_cyan]",
                )
                table.add_row(
                    f"1st Derivative f'({var}):",
                    f"[bold bright_yellow]{render_pretty(d1, 'unicode')}[/bold bright_yellow]",
                )
                table.add_row(
                    f"2nd Derivative f''({var}):",
                    f"[bold bright_magenta]{render_pretty(d2, 'unicode')}[/bold bright_magenta]",
                )
                table.add_row("Evaluation Point x₀:", f"[bold white]{x0}[/bold white]")
                table.add_row(f"Value f({x0}):", f"[bold green]{y0:.6g}[/bold green]")
                table.add_row(f"Slope f'({x0}):", f"[bold green]{dy0:.6g}[/bold green]")
                table.add_row(f"Curvature f''({x0}):", f"[bold green]{d2y0:.6g}[/bold green]")
                table.add_row(
                    f"Tangent Line @ x₀={x0}:",
                    f"[bold bright_green]{eq_str}[/bold bright_green] (slope m = {slope:.4f})",
                )
                table.add_row("LaTeX Representation:", f"[dim]{expr.to_latex()}[/dim]")

                self.update(
                    Panel(
                        table,
                        title="[bold gold1]✦ Mathematical Overview ✦[/bold gold1]",
                        border_style="bright_blue",
                    )
                )
            else:
                text = (
                    f"f({var})  = {expr.to_infix()}\n"
                    f"f'({var}) = {d1.to_infix()}\n"
                    f"f''({var})= {d2.to_infix()}\n"
                    f"f({x0})   = {y0}\n"
                    f"Tangent   = {eq_str}"
                )
                if HAS_TEXTUAL:
                    self.update(text)
        except Exception as e:
            msg = f"Error computing overview: {e}"
            if HAS_RICH and HAS_TEXTUAL:
                self.update(Panel(f"[bold red]{msg}[/bold red]", border_style="red"))
            elif HAS_TEXTUAL:
                self.update(msg)


class ASTTreeWidget(Static if HAS_TEXTUAL else object):
    """Renders visual hierarchical tree of AST nodes."""

    def update_tree(self, expr: Node) -> None:
        try:
            if HAS_RICH:
                rich_tree = expr.to_rich_tree()
                self.update(
                    Panel(
                        rich_tree,
                        title="[bold cyan]Abstract Syntax Tree Structure[/bold cyan]",
                        border_style="cyan",
                    )
                )
            else:
                tree_str = render_ast_tree(expr)
                if HAS_TEXTUAL:
                    self.update(tree_str)
        except Exception as e:
            msg = f"Error rendering AST: {e}"
            if HAS_RICH and HAS_TEXTUAL:
                self.update(Panel(f"[bold red]{msg}[/bold red]", border_style="red"))
            elif HAS_TEXTUAL:
                self.update(msg)


class DerivationStepsWidget(Static if HAS_TEXTUAL else object):
    """Renders step-by-step differentiation rules applied."""

    def update_steps(self, expr: Node, var: str = "x", order: int = 1) -> None:
        try:
            tracker = DerivationTracker()
            curr = expr
            for _ in range(order):
                curr = diff(curr, var=var, tracker=tracker, simplify_result=True)

            if HAS_RICH:
                step_tree = tracker.build_rich_tree()
                self.update(
                    Panel(
                        step_tree,
                        title=f"[bold yellow]Step-by-Step Derivation (Order {order})[/bold yellow]",
                        border_style="yellow",
                    )
                )
            else:
                if HAS_TEXTUAL:
                    self.update("\n".join(s.format_text() for s in tracker.root_steps))
        except Exception as e:
            msg = f"Error generating steps: {e}"
            if HAS_RICH and HAS_TEXTUAL:
                self.update(Panel(f"[bold red]{msg}[/bold red]", border_style="red"))
            elif HAS_TEXTUAL:
                self.update(msg)


class GraphPlotWidget(Static if HAS_TEXTUAL else object):
    """Renders Unicode Braille interactive 2D graph."""

    def update_plot(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 1.0,
        x_min: float = -5.0,
        x_max: float = 5.0,
        width: int = 68,
        height: int = 16,
    ) -> None:
        try:
            d1 = diff(expr, var=var, order=1, simplify_result=True)
            slope, b, _ = tangent_line(expr, x0=x0, var=var)

            curves = [
                (lambda x: expr.evaluate({var: x}), f"f({var}) = {expr.to_infix()}", "cyan"),
                (lambda x: d1.evaluate({var: x}), f"f'({var}) = {d1.to_infix()}", "yellow"),
                (lambda x, m=slope, c=b: m * x + c, f"Tangent @ {x0}", "green"),
            ]

            plot_text = plot_functions(
                curves,
                x_min=x_min,
                x_max=x_max,
                width=width,
                height=height,
                use_color=HAS_RICH,
            )

            if HAS_RICH:
                self.update(
                    Panel(
                        plot_text,
                        title=f"[bold bright_cyan]Unicode Braille Plot [{x_min:.1f}, {x_max:.1f}][/bold bright_cyan]",
                        border_style="bright_blue",
                    )
                )
            elif HAS_TEXTUAL:
                self.update(plot_text)
        except Exception as e:
            msg = f"Error plotting graph: {e}"
            if HAS_RICH and HAS_TEXTUAL:
                self.update(Panel(f"[bold red]{msg}[/bold red]", border_style="red"))
            elif HAS_TEXTUAL:
                self.update(msg)


class CalculusAnalysisWidget(Static if HAS_TEXTUAL else object):
    """Calculus analysis: critical points, roots, Taylor approximation, definite integral."""

    def update_analysis(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 0.0,
        x_min: float = -5.0,
        x_max: float = 5.0,
        taylor_deg: int = 4,
    ) -> None:
        try:
            crit_pts = critical_points(expr, domain=(x_min, x_max), var=var)
            roots = find_all_roots(expr, domain=(x_min, x_max), var=var)
            taylor_poly = taylor_series(expr, var=var, x0=x0, order=taylor_deg)
            integral_val = definite_integrate(expr, var=var, lower=x_min, upper=x_max)

            if HAS_RICH:
                content = Table.grid(padding=1)
                content.add_column(ratio=1)

                crit_table = Table(
                    title="Critical Points & Local Extrema (f'(x) = 0)",
                    border_style="gold1",
                    expand=True,
                )
                crit_table.add_column("x", style="bold cyan", justify="right")
                crit_table.add_column("y = f(x)", style="bold white", justify="right")
                crit_table.add_column("f''(x)", style="dim", justify="right")
                crit_table.add_column("Classification", style="bold green")

                if crit_pts:
                    for pt in crit_pts:
                        crit_table.add_row(
                            f"{pt['x']:.4f}",
                            f"{pt['y']:.4f}",
                            f"{pt['f2']:.4f}",
                            pt["classification"],
                        )
                else:
                    crit_table.add_row("—", "—", "—", "[dim]No critical points found in range[/dim]")

                summary_table = Table(
                    title="Calculus Properties & Series", border_style="magenta", expand=True
                )
                summary_table.add_column("Analysis Feature", style="bold yellow", width=24)
                summary_table.add_column("Result", style="bold white")

                roots_str = (
                    ", ".join(f"{r:.4f}" for r in roots)
                    if roots
                    else "No real roots detected"
                )
                summary_table.add_row("Roots f(x) = 0:", f"[bold green]{roots_str}[/bold green]")
                summary_table.add_row(
                    f"Taylor Polynomial (deg {taylor_deg}, x₀={x0}):",
                    f"[bold bright_magenta]{render_pretty(taylor_poly, 'unicode')}[/bold bright_magenta]",
                )
                summary_table.add_row(
                    f"Definite Integral [{x_min}, {x_max}]:",
                    f"[bold bright_blue]∫ f({var}) d{var} ≈ {integral_val:.6f}[/bold bright_blue]",
                )

                content.add_row(crit_table)
                content.add_row(summary_table)

                self.update(
                    Panel(
                        content,
                        title="[bold green]✦ Deep Calculus Analysis ✦[/bold green]",
                        border_style="green",
                    )
                )
            else:
                text = (
                    f"Roots: {roots}\n"
                    f"Critical Points: {crit_pts}\n"
                    f"Taylor (deg {taylor_deg}): {taylor_poly.to_infix()}\n"
                    f"Integral [{x_min}, {x_max}]: {integral_val:.6f}"
                )
                if HAS_TEXTUAL:
                    self.update(text)
        except Exception as e:
            msg = f"Error in calculus analysis: {e}"
            if HAS_RICH and HAS_TEXTUAL:
                self.update(Panel(f"[bold red]{msg}[/bold red]", border_style="red"))
            elif HAS_TEXTUAL:
                self.update(msg)
