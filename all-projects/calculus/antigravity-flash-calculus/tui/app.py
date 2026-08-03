"""Terminal User Interface (TUI) interactive application and runner."""

import sys
from typing import Optional

from core.differentiator import differentiate_with_steps
from core.parser import parse_expression
from core.simplifier import simplify
from tui.derivation_view import render_derivation_breakdown
from tui.plotter import render_ascii_plot
from tui.tree_renderer import render_ast_tree


class CalculusTUIApp:
    """Calculus Engine Interactive Terminal User Interface."""

    BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════╗
║               ANTIGRAVITY CALCULUS CORE & TERMINAL UI                   ║
║         Symbolic AST Differentiation, Derivation & ASCII Graphing        ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

    PRESET_EXAMPLES = [
        "x^2 + 3*x + 5",
        "sin(x) * cos(x)",
        "x * exp(x)",
        "(x^2 + 1) / (x - 1)",
        "ln(x^2 + 1)",
        "tan(2*x) + sqrt(x)",
    ]

    def __init__(self):
        self.current_expr_str = "x^3 - 4*x + sin(x)"
        self.var_name = "x"

    def run(self, demo_mode: bool = False):
        """Run the TUI application loop."""
        print(self.BANNER)

        if demo_mode or not sys.stdin.isatty():
            self.run_demo_mode()
            return

        while True:
            print(f"\n Current Expression: f({self.var_name}) = {self.current_expr_str}")
            print("─" * 74)
            print(" 1. Enter New Expression")
            print(" 2. Display AST Equation Tree")
            print(" 3. View Step-by-Step Derivation Breakdown")
            print(" 4. Render Real-Time Terminal Graph Plot (f & f')")
            print(" 5. Evaluate f(x) and f'(x) Numerically")
            print(" 6. Run Preset Demonstration Examples")
            print(" 0. Exit")
            print("─" * 74)

            try:
                choice = input("Select an option (0-6): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Antigravity Calculus TUI.")
                break

            if choice == "1":
                new_expr = input("\nEnter expression (e.g. 'x^2 + sin(3x)'): ").strip()
                if new_expr:
                    try:
                        parse_expression(new_expr)
                        self.current_expr_str = new_expr
                        print(f"Successfully set expression to: {new_expr}")
                    except Exception as e:
                        print(f"Error parsing expression: {e}")
            elif choice == "2":
                self.show_ast_tree()
            elif choice == "3":
                self.show_derivation_steps()
            elif choice == "4":
                self.show_graph_plotter()
            elif choice == "5":
                self.evaluate_expression()
            elif choice == "6":
                self.run_preset_demo()
            elif choice == "0":
                print("Thank you for using Antigravity Calculus TUI!")
                break
            else:
                print("Invalid option. Please enter a number between 0 and 6.")

    def show_ast_tree(self):
        """Display AST tree representation of function and its derivative."""
        try:
            ast = parse_expression(self.current_expr_str)
            raw_d, simp_d, _ = differentiate_with_steps(ast, self.var_name)

            print(f"\n══ AST Tree: Original Function f({self.var_name}) = {self.current_expr_str} ══")
            print(render_ast_tree(ast))

            print(f"\n══ AST Tree: Simplified Derivative f'({self.var_name}) = {simp_d} ══")
            print(render_ast_tree(simp_d))
        except Exception as e:
            print(f"Error rendering AST tree: {e}")

    def show_derivation_steps(self):
        """Display step-by-step differentiation breakdown."""
        try:
            ast = parse_expression(self.current_expr_str)
            raw_d, simp_d, steps = differentiate_with_steps(ast, self.var_name)
            report = render_derivation_breakdown(
                self.current_expr_str, str(raw_d), str(simp_d), steps
            )
            print(report)
        except Exception as e:
            print(f"Error computing derivation steps: {e}")

    def show_graph_plotter(self):
        """Render terminal ASCII graph plotter for f(x) and f'(x)."""
        try:
            ast = parse_expression(self.current_expr_str)
            raw_d, simp_d, _ = differentiate_with_steps(ast, self.var_name)

            print("\nGraph Domain Bounds:")
            try:
                xmin_in = input("Enter min X [-5.0]: ").strip()
                x_min = float(xmin_in) if xmin_in else -5.0
                xmax_in = input("Enter max X [5.0]: ").strip()
                x_max = float(xmax_in) if xmax_in else 5.0
            except ValueError:
                x_min, x_max = -5.0, 5.0

            plot = render_ascii_plot(ast, simp_d, self.var_name, x_min=x_min, x_max=x_max)
            print(plot)
        except Exception as e:
            print(f"Error rendering graph plot: {e}")

    def evaluate_expression(self):
        """Evaluate f(x) and f'(x) numerically for given x value."""
        try:
            ast = parse_expression(self.current_expr_str)
            _, simp_d, _ = differentiate_with_steps(ast, self.var_name)

            x_in = input(f"Enter value for {self.var_name} [1.0]: ").strip()
            x_val = float(x_in) if x_in else 1.0

            f_val = ast.evaluate({self.var_name: x_val})
            df_val = simp_d.evaluate({self.var_name: x_val})

            print(f"\n numerical Evaluation at {self.var_name} = {x_val}:")
            print(f"  f({x_val})  = {f_val}")
            print(f"  f'({x_val}) = {df_val}")
        except Exception as e:
            print(f"Error during numerical evaluation: {e}")

    def run_preset_demo(self):
        """Run through preset expression suite."""
        print("\n══ PRESET DEMONSTRATION SUITE ══\n")
        for expr in self.PRESET_EXAMPLES:
            print(f"────────────────────────────────────────────────────────────────────────")
            print(f" Expression : {expr}")
            try:
                ast = parse_expression(expr)
                raw_d, simp_d, steps = differentiate_with_steps(ast, "x")
                print(f" Derivative : {simp_d}")
                print(f" Total Steps: {len(steps)} rules applied")
            except Exception as e:
                print(f" Error: {e}")
        print("────────────────────────────────────────────────────────────────────────\n")

    def run_demo_mode(self):
        """Run non-interactive showcase for automated environments."""
        print("Running Non-Interactive Antigravity Calculus TUI Showcase...\n")
        demo_exprs = [
            "x^3 - 4*x + 2",
            "sin(x) * cos(x)",
            "(x^2 + 1) / (x + 1)",
        ]

        for expr_str in demo_exprs:
            print(f"\n========================================================================")
            print(f"  EXPRESSION DEMO: f(x) = {expr_str}")
            print(f"========================================================================")
            ast = parse_expression(expr_str)
            raw_d, simp_d, steps = differentiate_with_steps(ast, "x")

            print("\n1. AST TREE VISUALIZER:")
            print(render_ast_tree(ast))

            print("\n2. STEP-BY-STEP DERIVATION BREAKDOWN:")
            print(render_derivation_breakdown(expr_str, str(raw_d), str(simp_d), steps))

            print("\n3. TERMINAL ASCII GRAPH PLOT:")
            print(render_ascii_plot(ast, simp_d, "x", x_min=-4.0, x_max=4.0))


def main():
    demo_flag = "--demo" in sys.argv
    app = CalculusTUIApp()
    app.run(demo_mode=demo_flag)


if __name__ == "__main__":
    main()
