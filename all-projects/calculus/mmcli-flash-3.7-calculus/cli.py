"""
Calculus CLI Interface
======================
Rich & standard terminal command-line interface for symbolic differentiation,
step-by-step derivations, AST trees, terminal curve plots, limits, and integration.
"""

from __future__ import annotations
import argparse
import sys
from typing import List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None  # type: ignore

from parser import parse_expr, ParseError
from differentiator import (
    diff, higher_derivative, taylor_series,
    tangent_line, find_roots_newton, find_all_roots, critical_points
)
from simplifier import simplify
from limits import limit
from integrator import integrate, definite_integrate
from tracker import DerivationTracker
from tree_renderer import render_ast_tree, render_ascii_tree, render_pretty, to_latex
from derivation_view import render_derivation_breakdown, DerivationViewer
from plotter import plot_functions, plot_expression, render_braille_plot, render_ascii_plot


def run_cli(args_list: Optional[List[str]] = None) -> int:
    """Execute calculus CLI parser and action runner."""
    parser = argparse.ArgumentParser(
        prog="calculus",
        description="Symbolic Calculus Engine, AST Visualizer & Terminal Curve Plotter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  calculus "sin(x^2) / (x + 1)" --diff x --steps --plot
  calculus "x^3 - 3*x^2 + 2" --tree --critical --roots
  calculus "exp(2*x) * cos(x)" --order 2 --eval 1.5 --taylor 4
  calculus "sin(x)/x" --limit 0
  calculus "x^2" --integral 0 3
  calculus --tui
        """,
    )

    parser.add_argument("expression", nargs="?", help="Mathematical expression to differentiate/evaluate")
    parser.add_argument("--diff", default="x", help="Variable to differentiate with respect to (default: x)")
    parser.add_argument("--order", type=int, default=1, help="Derivative order (default: 1)")
    parser.add_argument("--steps", action="store_true", help="Display step-by-step derivation breakdown")
    parser.add_argument("--tree", action="store_true", help="Display AST equation tree")
    parser.add_argument("--ascii-tree", action="store_true", help="Display AST tree in pure ASCII")
    parser.add_argument("--plot", action="store_true", help="Render high-resolution Unicode Braille curve plot")
    parser.add_argument("--ascii-plot", action="store_true", help="Render ASCII curve plot")
    parser.add_argument("--eval", type=float, default=None, help="Evaluate f(x) and f'(x) at specified value")
    parser.add_argument("--tangent", type=float, default=None, help="Compute tangent line at given x₀")
    parser.add_argument("--taylor", type=int, default=None, help="Compute Taylor polynomial of given degree")
    parser.add_argument("--center", type=float, default=0.0, help="Center point for Taylor polynomial (default: 0.0)")
    parser.add_argument("--roots", action="store_true", help="Find real roots of f(x) = 0")
    parser.add_argument("--critical", action="store_true", help="Find and classify critical points f'(x) = 0")
    parser.add_argument("--integral", nargs=2, type=float, metavar=("A", "B"), help="Definite integral from A to B")
    parser.add_argument("--integrate", action="store_true", help="Compute symbolic indefinite antiderivative")
    parser.add_argument("--limit", type=str, default=None, help="Compute limit as variable approaches point")
    parser.add_argument("--dir", choices=["left", "right", "both"], default="both", help="Limit direction")
    parser.add_argument("--simplify", action="store_true", help="Simplify mathematical expression")
    parser.add_argument("--xmin", type=float, default=-5.0, help="Plot minimum x (default: -5.0)")
    parser.add_argument("--xmax", type=float, default=5.0, help="Plot maximum x (default: 5.0)")
    parser.add_argument("--width", type=int, default=70, help="Plot character width (default: 70)")
    parser.add_argument("--height", type=int, default=18, help="Plot character height (default: 18)")
    parser.add_argument("--latex", action="store_true", help="Output LaTeX representation")
    parser.add_argument("--tui", action="store_true", help="Launch interactive Terminal User Interface (TUI)")

    args = parser.parse_args(args_list)

    if args.tui or not args.expression:
        from tui import run_tui
        run_tui()
        return 0

    try:
        expr = parse_expr(args.expression)
    except ParseError as e:
        if HAS_RICH:
            console.print(f"[bold red]Syntax Error:[/bold red] {e.message}")
        else:
            print(f"Syntax Error: {e.message}", file=sys.stderr)
        return 1
    except Exception as e:
        if HAS_RICH:
            console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    tracker = DerivationTracker() if args.steps else None

    # Compute derivative
    d_expr = diff(expr, var=args.diff, order=args.order, tracker=tracker, simplify_result=True)

    # 1. Main Overview Display
    if HAS_RICH:
        overview_table = Table(box=None, show_header=False)
        overview_table.add_column("Property", style="bold cyan", width=22)
        overview_table.add_column("Value", style="bold white")

        overview_table.add_row("Input Expression f(x):", f"[bold bright_cyan]{render_pretty(expr, 'unicode')}[/bold bright_cyan]")
        deriv_label = f"Derivative d^{args.order}/d{args.diff}^{args.order}:" if args.order > 1 else f"Derivative d/d{args.diff}:"
        overview_table.add_row(deriv_label, f"[bold bright_yellow]{render_pretty(d_expr, 'unicode')}[/bold bright_yellow]")

        if args.latex:
            overview_table.add_row("LaTeX f(x):", f"[dim]{expr.to_latex()}[/dim]")
            overview_table.add_row("LaTeX f'(x):", f"[dim]{d_expr.to_latex()}[/dim]")

        if args.eval is not None:
            val_f = expr.evaluate({args.diff: args.eval})
            val_df = d_expr.evaluate({args.diff: args.eval})
            overview_table.add_row(f"f({args.eval}):", f"[bold green]{val_f:.6g}[/bold green]")
            overview_table.add_row(f"f'({args.eval}):", f"[bold green]{val_df:.6g}[/bold green]")

        if args.tangent is not None:
            slope, b, eq_str = tangent_line(expr, x0=args.tangent, var=args.diff)
            overview_table.add_row(f"Tangent @ x₀={args.tangent}:", f"[bold green]{eq_str}[/bold green] (slope m={slope:.4f})")

        if args.taylor is not None:
            taylor_poly = taylor_series(expr, var=args.diff, x0=args.center, order=args.taylor)
            overview_table.add_row(f"Taylor (deg {args.taylor}, x₀={args.center}):", f"[bold magenta]{render_pretty(taylor_poly, 'unicode')}[/bold magenta]")

        if args.integral is not None:
            a, b = args.integral
            approx = definite_integrate(expr, var=args.diff, lower=a, upper=b)
            overview_table.add_row(f"Definite Integral [{a}, {b}]:", f"[bold bright_blue]{approx:.6f}[/bold bright_blue]")

        if args.integrate:
            indef = integrate(expr, var=args.diff, simplify_result=True)
            overview_table.add_row(f"Antiderivative ∫ f({args.diff}) d{args.diff}:", f"[bold bright_blue]{render_pretty(indef, 'unicode')} + C[/bold bright_blue]")

        if args.limit is not None:
            pt = float(args.limit) if args.limit not in ("inf", "-inf") else (float("inf") if args.limit == "inf" else float("-inf"))
            lim_val = limit(expr, var=args.diff, point=pt, direction=args.dir)
            lim_str = f"{lim_val:.6g}" if isinstance(lim_val, float) else str(lim_val)
            overview_table.add_row(f"Limit ({args.diff} → {args.limit}):", f"[bold green]{lim_str}[/bold green]")

        console.print(Panel(overview_table, title="[bold gold1]✦ Calculus Engine Analysis ✦[/bold gold1]", border_style="bright_blue"))
    else:
        print("=" * 60)
        print("CALCULUS ENGINE ANALYSIS")
        print("=" * 60)
        print(f"Input Expression f(x): {render_pretty(expr, 'ascii')}")
        print(f"Derivative d/d{args.diff}    : {render_pretty(d_expr, 'ascii')}")
        if args.eval is not None:
            print(f"f({args.eval})              : {expr.evaluate({args.diff: args.eval}):.6g}")
            print(f"f'({args.eval})             : {d_expr.evaluate({args.diff: args.eval}):.6g}")
        if args.tangent is not None:
            slope, b, eq_str = tangent_line(expr, x0=args.tangent, var=args.diff)
            print(f"Tangent @ {args.tangent}       : {eq_str} (m={slope:.4f})")
        if args.integral is not None:
            a, b = args.integral
            print(f"Integral [{a}, {b}]     : {definite_integrate(expr, var=args.diff, lower=a, upper=b):.6f}")
        if args.integrate:
            print(f"Antiderivative ∫ f(x)dx: {integrate(expr, var=args.diff).to_infix()} + C")
        print("=" * 60)

    # 2. AST Tree View
    if args.tree or args.ascii_tree:
        use_uni = not args.ascii_tree
        if HAS_RICH and use_uni:
            console.print("\n[bold cyan]Abstract Syntax Tree (AST):[/bold cyan]")
            console.print(expr.to_rich_tree())
        else:
            print("\nAbstract Syntax Tree (AST):")
            print(render_ast_tree(expr, use_unicode=use_uni))

    # 3. Derivation Breakdown
    if args.steps and tracker:
        if HAS_RICH:
            console.print("\n[bold yellow]Step-by-Step Derivation Breakdown:[/bold yellow]")
            step_tree = tracker.build_rich_tree()
            console.print(step_tree)
        else:
            print("\nStep-by-Step Derivation Breakdown:")
            print(render_derivation_breakdown(expr.to_infix(), tracker.root_steps[-1].raw_result if tracker.root_steps else d_expr.to_infix(), d_expr.to_infix(), tracker, var=args.diff))

    # 4. Roots and Critical Points
    if args.roots:
        roots = find_all_roots(expr, domain=(args.xmin, args.xmax), var=args.diff)
        if roots:
            roots_str = ", ".join(f"{r:.4f}" for r in roots)
            if HAS_RICH:
                console.print(f"\n[bold green]Roots of f({args.diff}) = 0 in [{args.xmin}, {args.xmax}]:[/bold green] {roots_str}")
            else:
                print(f"\nRoots of f({args.diff}) = 0 in [{args.xmin}, {args.xmax}]: {roots_str}")
        else:
            msg = f"No real roots detected in range [{args.xmin}, {args.xmax}]."
            if HAS_RICH:
                console.print(f"\n[dim]{msg}[/dim]")
            else:
                print(f"\n{msg}")

    if args.critical:
        crit_pts = critical_points(expr, domain=(args.xmin, args.xmax), var=args.diff)
        if crit_pts:
            if HAS_RICH:
                crit_table = Table(title=f"Critical Points in [{args.xmin}, {args.xmax}]", border_style="yellow")
                crit_table.add_column("x", style="bold cyan")
                crit_table.add_column("y = f(x)", style="bold white")
                crit_table.add_column("f''(x)", style="dim")
                crit_table.add_column("Classification", style="bold green")
                for pt in crit_pts:
                    crit_table.add_row(f"{pt['x']:.4f}", f"{pt['y']:.4f}", f"{pt['f2']:.4f}", pt["classification"])
                console.print("\n", crit_table)
            else:
                print(f"\nCritical Points in [{args.xmin}, {args.xmax}]:")
                for pt in crit_pts:
                    print(f"  x={pt['x']:.4f}, y={pt['y']:.4f}, f''(x)={pt['f2']:.4f} -> {pt['classification']}")
        else:
            msg = f"No critical points found in range [{args.xmin}, {args.xmax}]."
            if HAS_RICH:
                console.print(f"\n[dim]{msg}[/dim]")
            else:
                print(f"\n{msg}")

    # 5. Plot
    if args.plot or args.ascii_plot:
        curves = [
            (lambda x: expr.evaluate({args.diff: x}), f"f({args.diff}) = {expr.to_infix()}", "cyan"),
            (lambda x: d_expr.evaluate({args.diff: x}), f"f'({args.diff}) = {d_expr.to_infix()}", "yellow"),
        ]
        if args.tangent is not None:
            slope, b, _ = tangent_line(expr, x0=args.tangent, var=args.diff)
            curves.append((lambda x, m=slope, c=b: m * x + c, f"Tangent @ {args.tangent}", "green"))

        plot_text = plot_functions(
            curves,
            x_min=args.xmin,
            x_max=args.xmax,
            width=args.width,
            height=args.height,
            ascii_mode=args.ascii_plot,
            use_color=HAS_RICH,
        )
        if HAS_RICH and not args.ascii_plot:
            console.print(Panel(plot_text, title="[bold cyan]Terminal Curve Plot[/bold cyan]", border_style="cyan"))
        else:
            print("\nTerminal Curve Plot:")
            print(plot_text)

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
