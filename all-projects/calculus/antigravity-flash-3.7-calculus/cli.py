"""
Calculus CLI Interface
======================
Rich-powered command-line interface for symbolic differentiation,
step-by-step derivations, AST trees, and terminal plots.
"""

from __future__ import annotations
import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

from engine import (
    parse_expr, diff, simplify, ParseError, DerivationTracker,
    plot_functions, taylor_series, tangent_line, find_roots,
    find_critical_points, definite_integral_approx
)

console = Console()


def run_cli(args_list: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity 3.7 Symbolic Calculus Engine & Terminal Plotter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py "sin(x^2) / (x + 1)" --diff x --steps --plot
  python app.py "x^3 - 3*x^2 + 2" --tree --critical --roots
  python app.py "exp(2*x) * cos(x)" --order 2 --eval 1.5 --taylor 4
  python app.py --tui
        """
    )
    parser.add_argument("expression", nargs="?", help="Mathematical expression to differentiate/evaluate")
    parser.add_argument("--diff", default="x", help="Variable to differentiate with respect to (default: x)")
    parser.add_argument("--order", type=int, default=1, help="Derivative order (default: 1)")
    parser.add_argument("--steps", action="store_true", help="Display step-by-step derivation breakdown")
    parser.add_argument("--tree", action="store_true", help="Display AST equation tree")
    parser.add_argument("--plot", action="store_true", help="Render high-resolution Unicode Braille plot")
    parser.add_argument("--eval", type=float, default=None, help="Evaluate f(x) and f'(x) at specified value")
    parser.add_argument("--tangent", type=float, default=None, help="Compute tangent line at given x0")
    parser.add_argument("--taylor", type=int, default=None, help="Compute Taylor polynomial of given order at center")
    parser.add_argument("--center", type=float, default=0.0, help="Center point for Taylor polynomial (default: 0.0)")
    parser.add_argument("--roots", action="store_true", help="Find roots of f(x) = 0")
    parser.add_argument("--critical", action="store_true", help="Find and classify critical points")
    parser.add_argument("--integral", nargs=2, type=float, metavar=("A", "B"), help="Approximate definite integral from A to B")
    parser.add_argument("--xmin", type=float, default=-5.0, help="Plot minimum x (default: -5.0)")
    parser.add_argument("--xmax", type=float, default=5.0, help="Plot maximum x (default: 5.0)")
    parser.add_argument("--latex", action="store_true", help="Output LaTeX representation")
    parser.add_argument("--tui", action="store_true", help="Launch interactive Terminal User Interface (TUI)")

    args = parser.parse_args(args_list)

    if args.tui or not args.expression:
        from tui.app import run_tui
        run_tui()
        return 0

    try:
        expr = parse_expr(args.expression)
    except ParseError as e:
        console.print(f"[bold red]Syntax Error:[/bold red] {e}")
        return 1

    tracker = DerivationTracker() if args.steps else None
    
    # Compute derivative
    d_expr = diff(expr, var=args.diff, order=args.order, tracker=tracker, simplify_result=True)

    # 1. Main Overview Panel
    overview_table = Table(box=None, show_header=False)
    overview_table.add_column("Property", style="bold cyan", width=18)
    overview_table.add_column("Value", style="bold white")

    overview_table.add_row("Input Expression:", f"[bold bright_cyan]{expr.to_infix()}[/bold bright_cyan]")
    deriv_label = f"Derivative d^{args.order}/d{args.diff}^{args.order}:" if args.order > 1 else f"Derivative d/d{args.diff}:"
    overview_table.add_row(deriv_label, f"[bold bright_yellow]{d_expr.to_infix()}[/bold bright_yellow]")

    if args.latex:
        overview_table.add_row("LaTeX f(x):", f"[dim]{expr.to_latex()}[/dim]")
        overview_table.add_row("LaTeX f'(x):", f"[dim]{d_expr.to_latex()}[/dim]")

    if args.eval is not None:
        val_f = expr.evaluate({args.diff: args.eval})
        val_df = d_expr.evaluate({args.diff: args.eval})
        overview_table.add_row(f"f({args.eval}):", f"[bold green]{val_f:.6g}[/bold green]")
        overview_table.add_row(f"f'({args.eval}):", f"[bold green]{val_df:.6g}[/bold green]")

    if args.tangent is not None:
        t_line, m, b = tangent_line(expr, var=args.diff, x0=args.tangent)
        overview_table.add_row(f"Tangent @ {args.tangent}:", f"[bold green]y = {t_line.to_infix()}[/bold green] (m={m:.4f})")

    if args.taylor is not None:
        taylor_poly = taylor_series(expr, var=args.diff, x0=args.center, order=args.taylor)
        overview_table.add_row(f"Taylor (deg {args.taylor}, x0={args.center}):", f"[bold magenta]{taylor_poly.to_infix()}[/bold magenta]")

    if args.integral is not None:
        a, b = args.integral
        approx = definite_integral_approx(expr, var=args.diff, a=a, b=b)
        overview_table.add_row(f"Integral [{a}, {b}]:", f"[bold bright_blue]{approx:.6f}[/bold bright_blue]")

    console.print(Panel(overview_table, title="[bold gold1]Calculus Engine Results[/bold gold1]", border_style="bright_blue"))

    # 2. AST Tree View
    if args.tree:
        console.print("\n[bold cyan]Abstract Syntax Tree (AST):[/bold cyan]")
        rich_tree = expr.to_rich_tree()
        console.print(rich_tree)

    # 3. Derivation Breakdown
    if args.steps and tracker:
        console.print("\n[bold yellow]Step-by-Step Derivation Breakdown:[/bold yellow]")
        step_tree = tracker.build_rich_tree()
        console.print(step_tree)

    # 4. Roots and Critical Points
    if args.roots:
        roots = find_roots(expr, var=args.diff, x_min=args.xmin, x_max=args.xmax)
        if roots:
            roots_str = ", ".join(f"{r:.4f}" for r in roots)
            console.print(f"\n[bold green]Roots of f({args.diff}) = 0 in [{args.xmin}, {args.xmax}]:[/bold green] {roots_str}")
        else:
            console.print(f"\n[dim]No real roots found in [{args.xmin}, {args.xmax}].[/dim]")

    if args.critical:
        crit_pts = find_critical_points(expr, var=args.diff, x_min=args.xmin, x_max=args.xmax)
        if crit_pts:
            crit_table = Table(title=f"Critical Points in [{args.xmin}, {args.xmax}]", border_style="yellow")
            crit_table.add_column("x", style="bold cyan")
            crit_table.add_column("y = f(x)", style="bold white")
            crit_table.add_column("f''(x)", style="dim")
            crit_table.add_column("Classification", style="bold green")
            for pt in crit_pts:
                crit_table.add_row(str(pt["x"]), str(pt["y"]), str(pt["f2"]), pt["classification"])
            console.print("\n", crit_table)
        else:
            console.print(f"\n[dim]No critical points found in [{args.xmin}, {args.xmax}].[/dim]")

    # 5. Plot
    if args.plot:
        curves = [
            (lambda x: expr.evaluate({args.diff: x}), f"f({args.diff}) = {expr.to_infix()}", "cyan"),
            (lambda x: d_expr.evaluate({args.diff: x}), f"f'({args.diff}) = {d_expr.to_infix()}", "yellow")
        ]
        if args.tangent is not None:
            t_line, _, _ = tangent_line(expr, var=args.diff, x0=args.tangent)
            curves.append((lambda x: t_line.evaluate({args.diff: x}), f"Tangent @ {args.tangent}", "green"))

        plot_text = plot_functions(curves, x_min=args.xmin, x_max=args.xmax, width=70, height=18)
        console.print(Panel(plot_text, title="[bold cyan]Unicode Terminal Plot[/bold cyan]", border_style="cyan"))

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
