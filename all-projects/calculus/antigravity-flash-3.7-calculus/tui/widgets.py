"""
TUI Custom Widgets
==================
Rich components for AST trees, step-by-step derivations, live plots, and calculus analysis.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from textual.widgets import Static, Tree, Label
from textual.containers import Vertical, Horizontal, VerticalScroll
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax

from engine import (
    Node, parse_expr, diff, simplify, DerivationTracker,
    plot_functions, taylor_series, tangent_line, find_roots,
    find_critical_points, definite_integral_approx
)


class MathOverviewWidget(Static):
    """Displays mathematical summary cards for f(x), f'(x), f''(x), tangent, and evaluation."""

    def update_expression(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 1.0,
        order: int = 1
    ) -> None:
        try:
            d1 = simplify(expr.differentiate(var))
            d2 = simplify(d1.differentiate(var))

            # Evaluations
            try:
                y0 = expr.evaluate({var: x0})
                dy0 = d1.evaluate({var: x0})
                d2y0 = d2.evaluate({var: x0})
            except Exception:
                y0, dy0, d2y0 = float('nan'), float('nan'), float('nan')

            t_line, m, b = tangent_line(expr, var=var, x0=x0)

            table = Table(box=None, expand=True, show_header=False)
            table.add_column("Property", style="bold cyan", width=22)
            table.add_column("Formula / Value", style="bold white")

            table.add_row("Input Expression f(x):", f"[bold bright_cyan]{expr.to_infix()}[/bold bright_cyan]")
            table.add_row(f"1st Derivative f'({var}):", f"[bold bright_yellow]{d1.to_infix()}[/bold bright_yellow]")
            table.add_row(f"2nd Derivative f''({var}):", f"[bold bright_magenta]{d2.to_infix()}[/bold bright_magenta]")
            table.add_row(f"Evaluation Point x₀:", f"[bold white]{x0}[/bold white]")
            table.add_row(f"Value f({x0}):", f"[bold green]{y0:.6g}[/bold green]")
            table.add_row(f"Slope f'({x0}):", f"[bold green]{dy0:.6g}[/bold green]")
            table.add_row(f"Curvature f''({x0}):", f"[bold green]{d2y0:.6g}[/bold green]")
            table.add_row(f"Tangent Line @ x₀={x0}:", f"[bold bright_green]y = {t_line.to_infix()}[/bold bright_green] (slope m = {m:.4f})")
            table.add_row(f"LaTeX Representation:", f"[dim]{expr.to_latex()}[/dim]")

            self.update(Panel(table, title="[bold gold1]✦ Mathematical Overview ✦[/bold gold1]", border_style="bright_blue"))
        except Exception as e:
            self.update(Panel(f"[bold red]Error computing overview:[/bold red] {e}", title="Error", border_style="red"))


class ASTTreeWidget(Static):
    """Renders visual hierarchical tree of AST nodes."""

    def update_tree(self, expr: Node) -> None:
        try:
            rich_tree = expr.to_rich_tree()
            self.update(Panel(rich_tree, title="[bold cyan]Abstract Syntax Tree Structure[/bold cyan]", border_style="cyan"))
        except Exception as e:
            self.update(Panel(f"[bold red]Error rendering AST:[/bold red] {e}", border_style="red"))


class DerivationStepsWidget(Static):
    """Renders step-by-step differentiation rules applied."""

    def update_steps(self, expr: Node, var: str = "x", order: int = 1) -> None:
        try:
            tracker = DerivationTracker()
            diff(expr, var=var, order=order, tracker=tracker, simplify_result=True)
            step_tree = tracker.build_rich_tree()
            self.update(Panel(step_tree, title=f"[bold yellow]Step-by-Step Derivation (Order {order})[/bold yellow]", border_style="yellow"))
        except Exception as e:
            self.update(Panel(f"[bold red]Error generating steps:[/bold red] {e}", border_style="red"))


class GraphPlotWidget(Static):
    """Renders Unicode Braille interactive 2D graph."""

    def update_plot(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 1.0,
        x_min: float = -5.0,
        x_max: float = 5.0,
        width: int = 68,
        height: int = 16
    ) -> None:
        try:
            d1 = simplify(expr.differentiate(var))
            t_line, _, _ = tangent_line(expr, var=var, x0=x0)

            curves = [
                (lambda x: expr.evaluate({var: x}), f"f({var}) = {expr.to_infix()}", "cyan"),
                (lambda x: d1.evaluate({var: x}), f"f'({var}) = {d1.to_infix()}", "yellow"),
                (lambda x: t_line.evaluate({var: x}), f"Tangent @ {x0}", "green")
            ]

            plot_text = plot_functions(
                curves,
                x_min=x_min,
                x_max=x_max,
                width=width,
                height=height
            )
            self.update(Panel(plot_text, title=f"[bold bright_cyan]Unicode Braille Plot [{x_min:.1f}, {x_max:.1f}][/bold bright_cyan]", border_style="bright_blue"))
        except Exception as e:
            self.update(Panel(f"[bold red]Error plotting graph:[/bold red] {e}", border_style="red"))


class CalculusAnalysisWidget(Static):
    """Calculus analysis: critical points, roots, Taylor approximation, definite integral."""

    def update_analysis(
        self,
        expr: Node,
        var: str = "x",
        x0: float = 0.0,
        x_min: float = -5.0,
        x_max: float = 5.0,
        taylor_deg: int = 4
    ) -> None:
        try:
            # 1. Critical Points
            crit_pts = find_critical_points(expr, var=var, x_min=x_min, x_max=x_max)
            # 2. Roots
            roots = find_roots(expr, var=var, x_min=x_min, x_max=x_max)
            # 3. Taylor Polynomial
            taylor_poly = taylor_series(expr, var=var, x0=x0, order=taylor_deg)
            # 4. Definite Integral
            integral_val = definite_integral_approx(expr, var=var, a=x_min, b=x_max)

            content = Table.grid(padding=1)
            content.add_column(ratio=1)

            # Table for Critical Points
            crit_table = Table(title="Critical Points & Local Extrema (f'(x) = 0)", border_style="gold1", expand=True)
            crit_table.add_column("x", style="bold cyan", justify="right")
            crit_table.add_column("y = f(x)", style="bold white", justify="right")
            crit_table.add_column("f''(x)", style="dim", justify="right")
            crit_table.add_column("Classification", style="bold green")

            if crit_pts:
                for pt in crit_pts:
                    crit_table.add_row(str(pt["x"]), str(pt["y"]), str(pt["f2"]), pt["classification"])
            else:
                crit_table.add_row("—", "—", "—", "[dim]No critical points found in range[/dim]")

            # Summary Table for Roots, Taylor, Integral
            summary_table = Table(title="Calculus Properties & Series", border_style="magenta", expand=True)
            summary_table.add_column("Analysis Feature", style="bold yellow", width=24)
            summary_table.add_column("Result", style="bold white")

            roots_str = ", ".join(f"{r:.4f}" for r in roots) if roots else "No real roots detected"
            summary_table.add_row("Roots f(x) = 0:", f"[bold green]{roots_str}[/bold green]")
            summary_table.add_row(f"Taylor Polynomial (deg {taylor_deg}, x₀={x0}):", f"[bold bright_magenta]{taylor_poly.to_infix()}[/bold bright_magenta]")
            summary_table.add_row(f"Definite Integral [{x_min}, {x_max}]:", f"[bold bright_blue]∫ f({var}) d{var} ≈ {integral_val:.6f}[/bold bright_blue]")

            content.add_row(crit_table)
            content.add_row(summary_table)

            self.update(Panel(content, title="[bold green]✦ Deep Calculus Analysis ✦[/bold green]", border_style="green"))
        except Exception as e:
            self.update(Panel(f"[bold red]Error in calculus analysis:[/bold red] {e}", border_style="red"))
