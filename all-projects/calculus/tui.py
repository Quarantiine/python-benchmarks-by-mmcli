"""
Terminal User Interface (TUI) for Symbolic Calculus Engine.

Features:
- Live expression parsing and preview
- Operation selection (Differentiation, Integration, Limits, Simplification, Evaluation, AST Tree)
- Step-by-step mathematical reasoning and breakdown
- Multi-format rendering (Unicode Math, LaTeX, ASCII AST Tree)
- Responsive Curses & Fallback Interactive Terminal Interfaces
"""

import sys
import os
import curses
import math
from typing import Dict, Any, List, Tuple, Optional

from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs
)
from calculus.parser import parse
from calculus.simplify import simplify
from calculus.diff import diff
from calculus.integrate import integrate
from calculus.limits import limit
from calculus.render import render_pretty, to_latex, render_tree


class StepByStepEngine:
    """Generates detailed step-by-step mathematical explanations for calculus operations."""

    @staticmethod
    def explain_diff(expr_str: str, var_str: str = "x") -> Dict[str, Any]:
        steps = []
        try:
            expr = parse(expr_str)
            steps.append(f"Step 1: Parsed expression f({var_str}) = {render_pretty(expr, 'unicode')}")
            
            # Analyze top-level structure
            rule_desc = StepByStepEngine._describe_diff_rule(expr, var_str)
            steps.append(f"Step 2: Applied Differentiation Rules -> {rule_desc}")

            raw_derived = diff(expr, var_str, simplify_result=False)
            steps.append(f"Step 3: Unsimplified derivative f'({var_str}) = {render_pretty(raw_derived, 'ascii')}")

            simplified = diff(expr, var_str, simplify_result=True)
            steps.append(f"Step 4: Simplified derivative f'({var_str}) = {render_pretty(simplified, 'unicode')}")

            return {
                "success": True,
                "input_expr": expr,
                "result_expr": simplified,
                "steps": steps,
                "latex": to_latex(simplified),
                "unicode": render_pretty(simplified, "unicode"),
                "tree": render_tree(simplified)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _describe_diff_rule(expr: Expr, var: str) -> str:
        if isinstance(expr, Add):
            return "Sum Rule: d/dx [u + v] = d/dx[u] + d/dx[v]"
        elif isinstance(expr, Sub):
            return "Difference Rule: d/dx [u - v] = d/dx[u] - d/dx[v]"
        elif isinstance(expr, Mul):
            return "Product Rule: d/dx [u * v] = u' * v + u * v'"
        elif isinstance(expr, Div):
            return "Quotient Rule: d/dx [u / v] = (u' * v - u * v') / (v^2)"
        elif isinstance(expr, Pow):
            return "Power / Exponential Rule: d/dx [u^v]"
        elif isinstance(expr, (Sin, Cos, Tan)):
            return f"Trigonometric Chain Rule: d/dx [{type(expr).__name__.lower()}(u)]"
        elif isinstance(expr, Exp):
            return "Exponential Rule: d/dx [e^u] = e^u * u'"
        elif isinstance(expr, Ln):
            return "Logarithmic Rule: d/dx [ln(u)] = u' / u"
        elif isinstance(expr, Symbol):
            return "Variable Rule: d/dx [x] = 1"
        elif isinstance(expr, Const):
            return "Constant Rule: d/dx [c] = 0"
        return "Composite Rule Application"

    @staticmethod
    def explain_integrate(expr_str: str, var_str: str = "x", lower_str: Optional[str] = None, upper_str: Optional[str] = None) -> Dict[str, Any]:
        steps = []
        try:
            expr = parse(expr_str)
            steps.append(f"Step 1: Parsed integrand f({var_str}) = {render_pretty(expr, 'unicode')}")

            is_definite = lower_str is not None and upper_str is not None and lower_str.strip() != "" and upper_str.strip() != ""
            
            if is_definite:
                steps.append(f"Step 2: Definite Integral from {lower_str} to {upper_str}")
                std_env = {"pi": math.pi, "e": math.e}
                lower_val = float(lower_str) if _is_number(lower_str) else parse(lower_str).eval(std_env)
                upper_val = float(upper_str) if _is_number(upper_str) else parse(upper_str).eval(std_env)
                
                indef = integrate(expr, var_str, simplify_result=True)
                steps.append(f"Step 3: Found antiderivative F({var_str}) = {render_pretty(indef, 'unicode')}")
                
                result_val = integrate(expr, var_str, lower=lower_val, upper=upper_val, simplify_result=True)
                steps.append(f"Step 4: Fundamental Theorem of Calculus F({upper_str}) - F({lower_str}) = {result_val}")

                return {
                    "success": True,
                    "input_expr": expr,
                    "result_expr": result_val,
                    "steps": steps,
                    "latex": rf"\int_{{{lower_str}}}^{{{upper_str}}} {to_latex(expr)} \, d{var_str} = {result_val}",
                    "unicode": f"∫[{lower_str} to {upper_str}] ({render_pretty(expr, 'unicode')}) d{var_str} = {result_val}",
                    "tree": render_tree(indef) if isinstance(indef, Expr) else f"Scalar Result: {result_val}"
                }
            else:
                steps.append("Step 2: Indefinite Integration (Antiderivative Search)")
                indef = integrate(expr, var_str, simplify_result=True)
                steps.append(f"Step 3: Antiderivative F({var_str}) = {render_pretty(indef, 'unicode')} + C")

                return {
                    "success": True,
                    "input_expr": expr,
                    "result_expr": indef,
                    "steps": steps,
                    "latex": rf"\int {to_latex(expr)} \, d{var_str} = {to_latex(indef)} + C",
                    "unicode": f"{render_pretty(indef, 'unicode')} + C",
                    "tree": render_tree(indef)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_limit(expr_str: str, var_str: str = "x", point_str: str = "0", direction: str = "both") -> Dict[str, Any]:
        steps = []
        try:
            expr = parse(expr_str)
            steps.append(f"Step 1: Parsed expression f({var_str}) = {render_pretty(expr, 'unicode')}")
            steps.append(f"Step 2: Target limit point {var_str} -> {point_str} (direction: {direction})")

            pt = point_str.strip().lower()
            if pt in ("inf", "+inf", "-inf"):
                point_val = pt
            elif _is_number(pt):
                point_val = float(pt)
            else:
                point_val = parse(pt)

            res = limit(expr, var_str, point_val, direction=direction)
            steps.append(f"Step 3: Evaluated limit = {res}")

            lim_symbol = f"lim({var_str}->{point_str})"
            return {
                "success": True,
                "input_expr": expr,
                "result_expr": res,
                "steps": steps,
                "latex": rf"\lim_{{{var_str} \to {point_str}}} \left({to_latex(expr)}\right) = {res}",
                "unicode": f"{lim_symbol} [{render_pretty(expr, 'unicode')}] = {res}",
                "tree": render_tree(expr)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_simplify(expr_str: str) -> Dict[str, Any]:
        steps = []
        try:
            expr = parse(expr_str)
            steps.append(f"Step 1: Input expression: {render_pretty(expr, 'unicode')}")
            
            simp = simplify(expr)
            steps.append("Step 2: Applied algebraic identity reductions, zero product elimination, constant folding")
            steps.append(f"Step 3: Simplified result: {render_pretty(simp, 'unicode')}")

            return {
                "success": True,
                "input_expr": expr,
                "result_expr": simp,
                "steps": steps,
                "latex": to_latex(simp),
                "unicode": render_pretty(simp, "unicode"),
                "tree": render_tree(simp)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def explain_eval(expr_str: str, var_bindings: Dict[str, float]) -> Dict[str, Any]:
        steps = []
        try:
            expr = parse(expr_str)
            steps.append(f"Step 1: Input expression: {render_pretty(expr, 'unicode')}")
            
            bind_str = ", ".join([f"{k} = {v}" for k, v in var_bindings.items()])
            steps.append(f"Step 2: Substituted variables: {bind_str}")

            val = expr.eval(var_bindings)
            steps.append(f"Step 3: Evaluated numerical result: {val}")

            return {
                "success": True,
                "input_expr": expr,
                "result_expr": val,
                "steps": steps,
                "latex": str(val),
                "unicode": str(val),
                "tree": render_tree(expr)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


class SymbolicCalculusTUI:
    """State manager and renderer for the Interactive Calculus TUI."""

    OPERATIONS = [
        ("1", "Differentiate", "Compute exact symbolic derivative f'(x)"),
        ("2", "Integrate", "Compute indefinite or definite integral ∫ f(x) dx"),
        ("3", "Limit", "Evaluate limit lim_{x->a} f(x)"),
        ("4", "Simplify", "Simplify algebraic & trigonometric expression"),
        ("5", "Evaluate", "Numerically evaluate expression with variable values"),
        ("6", "AST Tree", "Render full Abstract Syntax Tree structure")
    ]

    def __init__(self):
        self.expr_str = "x^3 + 2*x^2 + sin(x)"
        self.selected_op_idx = 0
        self.var_str = "x"
        self.lower_str = "0"
        self.upper_str = "pi"
        self.limit_point = "0"
        self.eval_vars = {"x": 2.0}
        self.render_mode = "unicode"  # "unicode", "latex", "ascii"
        self.history: List[str] = []

    def get_current_op(self) -> Tuple[str, str, str]:
        return self.OPERATIONS[self.selected_op_idx]

    def compute_current(self) -> Dict[str, Any]:
        op_code = self.OPERATIONS[self.selected_op_idx][0]
        if op_code == "1":
            return StepByStepEngine.explain_diff(self.expr_str, self.var_str)
        elif op_code == "2":
            return StepByStepEngine.explain_integrate(self.expr_str, self.var_str, self.lower_str, self.upper_str)
        elif op_code == "3":
            return StepByStepEngine.explain_limit(self.expr_str, self.var_str, self.limit_point)
        elif op_code == "4":
            return StepByStepEngine.explain_simplify(self.expr_str)
        elif op_code == "5":
            return StepByStepEngine.explain_eval(self.expr_str, self.eval_vars)
        elif op_code == "6":
            return StepByStepEngine.explain_simplify(self.expr_str)
        return {"success": False, "error": "Unknown operation"}


def run_interactive_cli():
    """Fallback rich interactive CLI loop for non-curses terminals."""
    tui = SymbolicCalculusTUI()
    
    print("=" * 65)
    print("           SYMBOLIC CALCULUS TERMINAL INTERFACE           ")
    print("=" * 65)

    while True:
        print("\n--- Current Configuration ---")
        print(f"Expression: {tui.expr_str}")
        print(f"Variable  : {tui.var_str}")
        op_key, op_name, op_desc = tui.get_current_op()
        print(f"Selected Operation: [{op_key}] {op_name} ({op_desc})")
        print("----------------------------")
        
        # Live Preview
        try:
            parsed = parse(tui.expr_str)
            print(f"Live Preview (Unicode): {render_pretty(parsed, 'unicode')}")
            print(f"Live Preview (LaTeX)  : {to_latex(parsed)}")
        except Exception as err:
            print(f"Syntax Alert: {err}")

        print("\nOptions:")
        for key, name, desc in tui.OPERATIONS:
            prefix = "-> " if name == op_name else "   "
            print(f"{prefix}[{key}] {name} - {desc}")
        print("   [e] Edit Expression")
        print("   [v] Set Variable Name")
        print("   [b] Set Integration Bounds")
        print("   [l] Set Limit Target Point")
        print("   [c] Compute & View Step-by-Step Breakdown")
        print("   [q] Quit")

        choice = input("\nEnter selection: ").strip().lower()
        if choice == 'q':
            print("Exiting Symbolic Calculus TUI. Goodbye!")
            break
        elif choice in ('1', '2', '3', '4', '5', '6'):
            tui.selected_op_idx = int(choice) - 1
            print(f"Operation changed to: {tui.OPERATIONS[tui.selected_op_idx][1]}")
        elif choice == 'e':
            new_expr = input(f"Enter expression (current: {tui.expr_str}): ").strip()
            if new_expr:
                tui.expr_str = new_expr
        elif choice == 'v':
            new_var = input(f"Enter variable name (current: {tui.var_str}): ").strip()
            if new_var:
                tui.var_str = new_var
        elif choice == 'b':
            tui.lower_str = input(f"Enter lower bound (current: {tui.lower_str}, blank for indefinite): ").strip()
            tui.upper_str = input(f"Enter upper bound (current: {tui.upper_str}, blank for indefinite): ").strip()
        elif choice == 'l':
            tui.limit_point = input(f"Enter limit point x -> (current: {tui.limit_point}): ").strip()
        elif choice == 'c':
            res = tui.compute_current()
            print("\n" + "=" * 50)
            print("STEP-BY-STEP MATHEMATICAL BREAKDOWN")
            print("=" * 50)
            if res["success"]:
                for step in res["steps"]:
                    print(f"  • {step}")
                print("\nOUTPUT RENDERINGS:")
                print(f"  [Unicode] : {res.get('unicode')}")
                print(f"  [LaTeX]   : {res.get('latex')}")
                print("\nAST TREE STRUCTURE:")
                print(res.get("tree", ""))
            else:
                print(f"Error executing operation: {res.get('error')}")
            print("=" * 50)
            input("\nPress Enter to return to menu...")


def run_curses_tui(stdscr):
    """Full-screen interactive Curses TUI."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    tui = SymbolicCalculusTUI()

    # Colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)

    active_field = 0  # 0: Expr, 1: Var, 2: Op Select, 3: Exec
    message = "Press UP/DOWN to navigate, ENTER to edit/execute, 'q' to quit."

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = " SYMBOLIC CALCULUS TUI - INTERACTIVE MATHEMATICS "
        stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title[:width])
        stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        # Header box: Input expression
        stdscr.addstr(2, 2, "Expression Input: ", curses.color_pair(1) | curses.A_BOLD)
        expr_attr = curses.A_REVERSE if active_field == 0 else curses.A_NORMAL
        stdscr.addstr(2, 20, f" {tui.expr_str} ", expr_attr)

        stdscr.addstr(3, 2, "Variable        : ", curses.color_pair(1) | curses.A_BOLD)
        var_attr = curses.A_REVERSE if active_field == 1 else curses.A_NORMAL
        stdscr.addstr(3, 20, f" {tui.var_str} ", var_attr)

        # Live Preview
        stdscr.addstr(5, 2, "Live Syntax & Render Preview:", curses.color_pair(3) | curses.A_BOLD)
        try:
            parsed = parse(tui.expr_str)
            unicode_preview = render_pretty(parsed, "unicode")
            latex_preview = to_latex(parsed)
            stdscr.addstr(6, 4, f"Valid Syntax  => Unicode: {unicode_preview}", curses.color_pair(2))
            stdscr.addstr(7, 4, f"                 LaTeX  : {latex_preview}", curses.color_pair(2))
        except Exception as e:
            stdscr.addstr(6, 4, f"Syntax Error  => {e}", curses.color_pair(4))

        # Operation Selection Menu
        stdscr.addstr(9, 2, "Select Calculus Operation:", curses.color_pair(3) | curses.A_BOLD)
        for i, (key, name, desc) in enumerate(tui.OPERATIONS):
            is_selected = (tui.selected_op_idx == i)
            is_focused = (active_field == 2 and is_selected)
            attr = curses.color_pair(5) if is_focused else (curses.A_BOLD if is_selected else curses.A_NORMAL)
            mark = "[x]" if is_selected else "[ ]"
            stdscr.addstr(10 + i, 4, f"{mark} {key}. {name:<14} - {desc}", attr)

        # Execute Button
        exec_attr = curses.A_REVERSE if active_field == 3 else curses.color_pair(2) | curses.A_BOLD
        stdscr.addstr(17, 4, " [ COMPUTATION & STEP-BY-STEP BREAKDOWN ] ", exec_attr)

        # Bottom status message
        stdscr.addstr(height - 2, 2, f"Status: {message[:width-10]}", curses.color_pair(1))
        stdscr.refresh()

        # Handle input
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
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
                new_e = stdscr.getstr(height - 3, 24).decode('utf-8')
                curses.noecho()
                if new_e.strip():
                    tui.expr_str = new_e.strip()
            elif active_field == 1:
                curses.echo()
                stdscr.addstr(height - 3, 2, "Enter variable name: ")
                new_v = stdscr.getstr(height - 3, 23).decode('utf-8')
                curses.noecho()
                if new_v.strip():
                    tui.var_str = new_v.strip()
            elif active_field in (2, 3):
                # Run step by step output modal
                res = tui.compute_current()
                _show_result_modal(stdscr, res)


def _show_result_modal(stdscr, res: Dict[str, Any]):
    """Modal overlay displaying step-by-step math output visualization."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    stdscr.addstr(1, 2, "=== STEP-BY-STEP MATHEMATICAL BREAKDOWN ===", curses.A_BOLD | curses.color_pair(3))
    
    row = 3
    if res["success"]:
        for step in res["steps"]:
            stdscr.addstr(row, 4, f"• {step[:width-10]}", curses.color_pair(2))
            row += 1
            if row >= height - 10:
                break

        row += 1
        stdscr.addstr(row, 2, "=== FINAL RENDERING & AST TREE ===", curses.A_BOLD | curses.color_pair(1))
        row += 1
        stdscr.addstr(row, 4, f"Unicode: {res.get('unicode')}")
        row += 1
        stdscr.addstr(row, 4, f"LaTeX  : {res.get('latex')}")
        
        row += 2
        tree_lines = res.get("tree", "").splitlines()
        stdscr.addstr(row, 4, "AST Tree Structure:")
        row += 1
        for t_line in tree_lines:
            if row < height - 3:
                stdscr.addstr(row, 6, t_line[:width-10])
                row += 1
    else:
        stdscr.addstr(row, 4, f"Error: {res.get('error')}", curses.color_pair(4))

    stdscr.addstr(height - 2, 2, "Press any key to return...", curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()


def main():
    """Main execution entry point."""
    if sys.stdin.isatty():
        try:
            curses.wrapper(run_curses_tui)
        except Exception:
            run_interactive_cli()
    else:
        run_interactive_cli()


if __name__ == "__main__":
    main()
