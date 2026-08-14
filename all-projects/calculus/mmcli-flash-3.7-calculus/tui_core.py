"""
Terminal User Interface (TUI) Core for Symbolic Calculus Engine
===============================================================
Interactive full-screen Curses TUI, Rich/Textual support, and responsive
interactive CLI shell for symbolic differentiation, step-by-step breakdown,
AST tree inspection, and Unicode curve plotting.
"""

from __future__ import annotations
import curses
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from ast_nodes import Node
from parser import parse_expr, ParseError
from simplifier import simplify
from differentiator import (
    diff, higher_derivative, taylor_series, tangent_line,
    find_roots_newton, critical_points
)
from limits import limit
from integrator import integrate, definite_integrate
from tracker import DerivationTracker
from tree_renderer import render_ast_tree, render_pretty, to_latex
from derivation_view import render_derivation_breakdown, DerivationViewer
from plotter import plot_functions, plot_expression, render_braille_plot, render_ascii_plot


class StepByStepEngine:
    """Generates detailed step-by-step mathematical explanations for calculus operations."""

    @staticmethod
    def explain_diff(expr_str: str, var_str: str = "x", order: int = 1) -> Dict[str, Any]:
        """Generate step-by-step derivative explanation."""
        try:
            expr = parse_expr(expr_str)
            tracker = DerivationTracker()
            curr = expr
            for _ in range(order):
                curr = diff(curr, var=var_str, tracker=tracker, simplify_result=True)

            steps_text = [
                f"Input Expression: {render_pretty(expr, 'unicode')}",
                f"Derivative Order: {order} w.r.t '{var_str}'",
            ]
            for root in tracker.root_steps:
                steps_text.append(f"• Applied {root.rule_name}: {root.rule_formula or root.input_expr}")
                if root.simplified_result:
                    steps_text.append(f"  ↳ Sub-result: {root.simplified_result}")

            steps_text.append(f"Final Simplified Result: {render_pretty(curr, 'unicode')}")

            return {
                "success": True,
                "input_expr": expr,
                "result_expr": curr,
                "steps": steps_text,
                "report": render_derivation_breakdown(
                    expr.to_infix(),
                    tracker.root_steps[-1].raw_result if tracker.root_steps else curr.to_infix(),
                    curr.to_infix(),
                    tracker,
                    var=var_str,
                ),
                "unicode": render_pretty(curr, "unicode"),
                "latex": curr.to_latex(),
                "tree": render_ast_tree(curr),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_integrate(
        expr_str: str,
        var_str: str = "x",
        lower_str: Optional[str] = None,
        upper_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate step-by-step integration explanation."""
        try:
            expr = parse_expr(expr_str)
            is_definite = (
                lower_str is not None
                and upper_str is not None
                and lower_str.strip() != ""
                and upper_str.strip() != ""
            )

            if is_definite:
                a = float(lower_str.strip())
                b = float(upper_str.strip())
                val = definite_integrate(expr, var=var_str, lower=a, upper=b)
                indef = integrate(expr, var=var_str, simplify_result=True)
                steps = [
                    f"Step 1: Parsed integrand f({var_str}) = {render_pretty(expr, 'unicode')}",
                    f"Step 2: Antiderivative F({var_str}) = {render_pretty(indef, 'unicode')}",
                    f"Step 3: Fundamental Theorem of Calculus F({b}) - F({a})",
                    f"Step 4: Computed Definite Integral = {val:.6f}",
                ]
                return {
                    "success": True,
                    "input_expr": expr,
                    "result_expr": val,
                    "steps": steps,
                    "unicode": f"∫[{a}, {b}] {render_pretty(expr, 'unicode')} d{var_str} = {val:.6f}",
                    "latex": rf"\int_{{{a}}}^{{{b}}} {expr.to_latex()} \, d{var_str} \approx {val:.6f}",
                    "tree": render_ast_tree(indef),
                }
            else:
                indef = integrate(expr, var=var_str, simplify_result=True)
                steps = [
                    f"Step 1: Parsed integrand f({var_str}) = {render_pretty(expr, 'unicode')}",
                    "Step 2: Applied Symbolic Antiderivative Integration Rules",
                    f"Step 3: Antiderivative F({var_str}) = {render_pretty(indef, 'unicode')} + C",
                ]
                return {
                    "success": True,
                    "input_expr": expr,
                    "result_expr": indef,
                    "steps": steps,
                    "unicode": f"{render_pretty(indef, 'unicode')} + C",
                    "latex": rf"\int {expr.to_latex()} \, d{var_str} = {indef.to_latex()} + C",
                    "tree": render_ast_tree(indef),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_limit(
        expr_str: str,
        var_str: str = "x",
        point_str: str = "0",
        direction: str = "both",
    ) -> Dict[str, Any]:
        """Generate limit evaluation explanation."""
        try:
            expr = parse_expr(expr_str)
            p_str = point_str.strip().lower()
            if p_str in ("inf", "+inf", "infinity"):
                pt: Any = float("inf")
            elif p_str in ("-inf", "-infinity"):
                pt = float("-inf")
            else:
                pt = float(p_str)

            res = limit(expr, var=var_str, point=pt, direction=direction)
            res_str = f"{res:.6g}" if isinstance(res, float) else str(res)
            steps = [
                f"Step 1: Parsed expression f({var_str}) = {render_pretty(expr, 'unicode')}",
                f"Step 2: Target limit point {var_str} → {point_str} (direction: {direction})",
                "Step 3: Evaluated limit via Direct Substitution / L'Hôpital / Numerical Perturbation",
                f"Step 4: Limit Value = {res_str}",
            ]
            return {
                "success": True,
                "input_expr": expr,
                "result_expr": res,
                "steps": steps,
                "unicode": f"lim({var_str} → {point_str}) [{render_pretty(expr, 'unicode')}] = {res_str}",
                "latex": rf"\lim_{{{var_str} \to {point_str}}} \left({expr.to_latex()}\right) = {res_str}",
                "tree": render_ast_tree(expr),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_simplify(expr_str: str) -> Dict[str, Any]:
        """Generate algebraic simplification explanation."""
        try:
            expr = parse_expr(expr_str)
            simp = simplify(expr)
            steps = [
                f"Step 1: Input expression: {render_pretty(expr, 'unicode')}",
                "Step 2: Applied canonical normalization, zero/one eliminations, constant folding",
                f"Step 3: Simplified expression: {render_pretty(simp, 'unicode')}",
            ]
            return {
                "success": True,
                "input_expr": expr,
                "result_expr": simp,
                "steps": steps,
                "unicode": render_pretty(simp, "unicode"),
                "latex": simp.to_latex(),
                "tree": render_ast_tree(simp),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_eval(expr_str: str, var_bindings: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate numeric value given variable bindings."""
        try:
            expr = parse_expr(expr_str)
            val = expr.evaluate(var_bindings)
            bind_str = ", ".join(f"{k} = {v}" for k, v in var_bindings.items())
            steps = [
                f"Step 1: Input expression: {render_pretty(expr, 'unicode')}",
                f"Step 2: Variable bindings: {bind_str}",
                f"Step 3: Evaluated numerical value: {val:.6g}",
            ]
            return {
                "success": True,
                "input_expr": expr,
                "result_expr": val,
                "steps": steps,
                "unicode": f"{val:.6g}",
                "latex": str(val),
                "tree": render_ast_tree(expr),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class SymbolicCalculusTUI:
    """State manager and coordinator for interactive calculus sessions."""

    OPERATIONS = [
        ("1", "Differentiate", "Compute derivative f'(x) with step-by-step rule breakdown"),
        ("2", "Integrate", "Compute definite or indefinite integral ∫ f(x) dx"),
        ("3", "Limit", "Evaluate symbolic or numerical limit lim_{x->a} f(x)"),
        ("4", "Simplify", "Algebraically reduce and simplify expression"),
        ("5", "Evaluate", "Numerically evaluate expression with variable values"),
        ("6", "AST Tree", "Display full Abstract Syntax Tree structure"),
        ("7", "Terminal Plot", "Render 2D Unicode Braille curve graph"),
    ]

    def __init__(self) -> None:
        self.expr_str = "sin(x^2) / (x + 1)"
        self.selected_op_idx = 0
        self.var_str = "x"
        self.order = 1
        self.lower_str = "0"
        self.upper_str = "3.14159"
        self.limit_point = "0"
        self.eval_vars = {"x": 1.0}
        self.xmin = -5.0
        self.xmax = 5.0

    def get_current_op(self) -> Tuple[str, str, str]:
        return self.OPERATIONS[self.selected_op_idx]

    def compute_current(self) -> Dict[str, Any]:
        op_code = self.OPERATIONS[self.selected_op_idx][0]
        if op_code == "1":
            return StepByStepEngine.explain_diff(self.expr_str, self.var_str, self.order)
        elif op_code == "2":
            return StepByStepEngine.explain_integrate(self.expr_str, self.var_str, self.lower_str, self.upper_str)
        elif op_code == "3":
            return StepByStepEngine.explain_limit(self.expr_str, self.var_str, self.limit_point)
        elif op_code == "4":
            return StepByStepEngine.explain_simplify(self.expr_str)
        elif op_code == "5":
            return StepByStepEngine.explain_eval(self.expr_str, self.eval_vars)
        elif op_code == "6":
            try:
                expr = parse_expr(self.expr_str)
                return {
                    "success": True,
                    "input_expr": expr,
                    "tree": render_ast_tree(expr),
                    "unicode": render_pretty(expr, "unicode"),
                    "latex": expr.to_latex(),
                    "steps": ["Parsed AST successfully."],
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        elif op_code == "7":
            try:
                expr = parse_expr(self.expr_str)
                plot_str = plot_expression(expr, var=self.var_str, x_min=self.xmin, x_max=self.xmax, width=64, height=14)
                return {
                    "success": True,
                    "input_expr": expr,
                    "plot": plot_str,
                    "unicode": render_pretty(expr, "unicode"),
                    "steps": [f"Rendered curve plot in range [{self.xmin}, {self.xmax}]"],
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Unknown operation"}


def run_curses_tui(stdscr: Any) -> None:
    """Full-screen interactive Curses TUI."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    tui = SymbolicCalculusTUI()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)

    active_field = 0  # 0: Expr, 1: Var, 2: Op Select, 3: Exec
    status_msg = "Use UP/DOWN to navigate fields, ENTER to edit/compute, 'q' to quit."

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " ✦ SYMBOLIC CALCULUS ENGINE - INTERACTIVE TUI ✦ "
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title[:width])
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        # Header inputs
        stdscr.addstr(2, 2, "Expression Input: ", curses.color_pair(1) | curses.A_BOLD)
        expr_attr = curses.A_REVERSE if active_field == 0 else curses.A_NORMAL
        stdscr.addstr(2, 20, f" {tui.expr_str} ", expr_attr)

        stdscr.addstr(3, 2, "Variable        : ", curses.color_pair(1) | curses.A_BOLD)
        var_attr = curses.A_REVERSE if active_field == 1 else curses.A_NORMAL
        stdscr.addstr(3, 20, f" {tui.var_str} ", var_attr)

        # Live Syntax Preview
        stdscr.addstr(5, 2, "Live Syntax & Render Preview:", curses.color_pair(3) | curses.A_BOLD)
        try:
            parsed = parse_expr(tui.expr_str)
            unicode_preview = render_pretty(parsed, "unicode")
            latex_preview = to_latex(parsed)
            stdscr.addstr(6, 4, f"✓ Valid Syntax  => Unicode: {unicode_preview[:width-32]}", curses.color_pair(2))
            stdscr.addstr(7, 4, f"                   LaTeX  : {latex_preview[:width-32]}", curses.color_pair(2))
        except Exception as e:
            stdscr.addstr(6, 4, f"✗ Syntax Error  => {str(e)[:width-24]}", curses.color_pair(4))

        # Operation Selector
        stdscr.addstr(9, 2, "Select Calculus Operation:", curses.color_pair(3) | curses.A_BOLD)
        for i, (key, name, desc) in enumerate(tui.OPERATIONS):
            is_selected = (tui.selected_op_idx == i)
            is_focused = (active_field == 2 and is_selected)
            attr = curses.color_pair(5) if is_focused else (curses.A_BOLD if is_selected else curses.A_NORMAL)
            mark = "[x]" if is_selected else "[ ]"
            stdscr.addstr(10 + i, 4, f"{mark} {key}. {name:<15} - {desc[:width-30]}", attr)

        # Execute Button
        exec_attr = curses.A_REVERSE if active_field == 3 else curses.color_pair(2) | curses.A_BOLD
        stdscr.addstr(18, 4, " [ ⚡ EXECUTE COMPUTATION & VIEW BREAKDOWN ⚡ ] ", exec_attr)

        stdscr.addstr(height - 2, 2, f"Status: {status_msg[:width-10]}", curses.color_pair(1))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key == curses.KEY_UP:
            if active_field == 2 and tui.selected_op_idx > 0:
                tui.selected_op_idx -= 1
            else:
                active_field = max(0, active_field - 1)
        elif key == curses.KEY_DOWN:
            if active_field == 2 and tui.selected_op_idx < len(tui.OPERATIONS) - 1:
                tui.selected_op_idx += 1
            else:
                active_field = min(3, active_field + 1)
        elif key in (10, 13):  # ENTER
            if active_field == 0:
                curses.echo()
                stdscr.addstr(height - 3, 2, "Enter new expression: ")
                new_e = stdscr.getstr(height - 3, 24).decode("utf-8")
                curses.noecho()
                if new_e.strip():
                    tui.expr_str = new_e.strip()
            elif active_field == 1:
                curses.echo()
                stdscr.addstr(height - 3, 2, "Enter variable name: ")
                new_v = stdscr.getstr(height - 3, 23).decode("utf-8")
                curses.noecho()
                if new_v.strip():
                    tui.var_str = new_v.strip()
            elif active_field in (2, 3):
                res = tui.compute_current()
                _show_curses_modal(stdscr, res, tui)


def _show_curses_modal(stdscr: Any, res: Dict[str, Any], tui: SymbolicCalculusTUI) -> None:
    """Modal overlay for results in curses."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    stdscr.addstr(1, 2, "=== MATHEMATICAL RESULT & BREAKDOWN ===", curses.A_BOLD | curses.color_pair(3))
    row = 3

    if res.get("success"):
        if "plot" in res:
            plot_lines = res["plot"].splitlines()
            for pl in plot_lines:
                if row < height - 3:
                    clean = pl.replace("[cyan]", "").replace("[/cyan]", "").replace("[yellow]", "").replace("[/yellow]", "")
                    stdscr.addstr(row, 2, clean[:width-4])
                    row += 1
        elif "report" in res:
            report_lines = res["report"].splitlines()
            for rl in report_lines:
                if row < height - 3:
                    stdscr.addstr(row, 2, rl[:width-4])
                    row += 1
        else:
            for step in res.get("steps", []):
                if row < height - 8:
                    stdscr.addstr(row, 4, f"• {step[:width-10]}", curses.color_pair(2))
                    row += 1

            if "unicode" in res:
                row += 1
                stdscr.addstr(row, 2, f"Unicode : {res.get('unicode')[:width-12]}", curses.color_pair(1) | curses.A_BOLD)
                row += 1
            if "latex" in res:
                stdscr.addstr(row, 2, f"LaTeX   : {res.get('latex')[:width-12]}", curses.color_pair(1))
                row += 1

            if "tree" in res:
                row += 1
                stdscr.addstr(row, 2, "AST Tree Structure:", curses.A_BOLD)
                row += 1
                for tl in res["tree"].splitlines():
                    if row < height - 3:
                        stdscr.addstr(row, 4, tl[:width-10])
                        row += 1
    else:
        stdscr.addstr(row, 4, f"Error: {res.get('error')}", curses.color_pair(4) | curses.A_BOLD)

    stdscr.addstr(height - 2, 2, "Press any key to return...", curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()


def run_interactive_cli() -> None:
    """Fallback interactive CLI loop."""
    tui = SymbolicCalculusTUI()

    print("=" * 68)
    print("           SYMBOLIC CALCULUS ENGINE INTERACTIVE SHELL            ")
    print("=" * 68)

    while True:
        print("\n--- Current Workspace ---")
        print(f"Expression : {tui.expr_str}")
        print(f"Variable   : {tui.var_str}")
        op_key, op_name, op_desc = tui.get_current_op()
        print(f"Operation  : [{op_key}] {op_name} ({op_desc})")
        print("-------------------------")

        try:
            parsed = parse_expr(tui.expr_str)
            print(f"Live Preview (Unicode) : {render_pretty(parsed, 'unicode')}")
            print(f"Live Preview (LaTeX)   : {to_latex(parsed)}")
        except Exception as err:
            print(f"Syntax Note : {err}")

        print("\nCommands:")
        for key, name, desc in tui.OPERATIONS:
            prefix = "-> " if name == op_name else "   "
            print(f"{prefix}[{key}] {name} - {desc}")
        print("   [e] Edit Expression")
        print("   [v] Set Variable")
        print("   [c] Compute & View Breakdown")
        print("   [p] Render Plot")
        print("   [q] Quit")

        try:
            choice = input("\nEnter selection: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if choice == "q":
            print("Goodbye!")
            break
        elif choice in ("1", "2", "3", "4", "5", "6", "7"):
            tui.selected_op_idx = int(choice) - 1
            print(f"Selected: {tui.OPERATIONS[tui.selected_op_idx][1]}")
        elif choice == "e":
            new_e = input(f"Enter expression (current: {tui.expr_str}): ").strip()
            if new_e:
                tui.expr_str = new_e
        elif choice == "v":
            new_v = input(f"Enter variable (current: {tui.var_str}): ").strip()
            if new_v:
                tui.var_str = new_v
        elif choice == "p":
            try:
                expr = parse_expr(tui.expr_str)
                print(plot_expression(expr, var=tui.var_str, x_min=tui.xmin, x_max=tui.xmax, width=64, height=14))
            except Exception as e:
                print(f"Plot Error: {e}")
        elif choice == "c":
            res = tui.compute_current()
            print("\n" + "=" * 60)
            print("STEP-BY-STEP MATHEMATICAL OUTPUT")
            print("=" * 60)
            if res.get("success"):
                if "report" in res:
                    print(res["report"])
                else:
                    for s in res.get("steps", []):
                        print(f"  • {s}")
                    if "unicode" in res:
                        print(f"\nResult (Unicode): {res['unicode']}")
                    if "latex" in res:
                        print(f"Result (LaTeX)  : {res['latex']}")
                    if "tree" in res:
                        print(f"\nAST Tree:\n{res['tree']}")
                    if "plot" in res:
                        print(f"\nPlot:\n{res['plot']}")
            else:
                print(f"Error: {res.get('error')}")
            print("=" * 60)


def run_tui() -> None:
    """Entry point to launch the best interactive terminal interface available."""
    if sys.stdin.isatty():
        try:
            from tui.app import run_textual_tui
            if run_textual_tui():
                return
        except Exception:
            pass

        try:
            curses.wrapper(run_curses_tui)
            return
        except Exception:
            pass

    run_interactive_cli()
