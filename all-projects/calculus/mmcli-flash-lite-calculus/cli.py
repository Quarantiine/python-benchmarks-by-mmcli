"""
CLI command dispatcher for the Symbolic Calculus Engine.
Supports diff, int, lim, simplify, eval, tree, and interactive TUI mode.
"""

import argparse
import sys
from calculus.parser import parse_expression
from calculus.engine import differentiate, simplify, integrate
from calculus.tui import run_tui, render_tree, render_derivation_steps, evaluate_expression


def main():
    parser = argparse.ArgumentParser(
        description="Minovative Mind CLI Flash Lite Calculus Engine & TUI",
        prog="calculus"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Compute derivative of an expression")
    diff_parser.add_argument("expression", type=str, help="Mathematical expression")
    diff_parser.add_argument("-v", "--var", type=str, default="x", help="Variable to differentiate with respect to")
    diff_parser.add_argument("-s", "--steps", action="store_true", help="Show step-by-step derivation breakdown")

    # int command
    int_parser = subparsers.add_parser("int", help="Compute definite or indefinite integral (numerical/symbolic approximation)")
    int_parser.add_argument("expression", type=str, help="Mathematical expression")
    int_parser.add_argument("-v", "--var", type=str, default="x", help="Variable of integration")
    int_parser.add_argument("-l", "--lower", type=float, default=None, help="Lower limit of integration")
    int_parser.add_argument("-u", "--upper", type=float, default=None, help="Upper limit of integration")

    # lim command
    lim_parser = subparsers.add_parser("lim", help="Evaluate limit of an expression as variable approaches point")
    lim_parser.add_argument("expression", type=str, help="Mathematical expression")
    lim_parser.add_argument("-v", "--var", type=str, default="x", help="Variable")
    lim_parser.add_argument("-p", "--point", type=float, default=0.0, help="Point to approach")

    # simplify command
    simplify_parser = subparsers.add_parser("simplify", help="Simplify a mathematical expression")
    simplify_parser.add_argument("expression", type=str, help="Mathematical expression")

    # eval command
    eval_parser = subparsers.add_parser("eval", help="Evaluate expression at given variable values")
    eval_parser.add_argument("expression", type=str, help="Mathematical expression")
    eval_parser.add_argument("assignments", nargs="*", help="Variable assignments in format var=val (e.g. x=3 y=4)")

    # tree command
    tree_parser = subparsers.add_parser("tree", help="Render ASCII/Unicode AST equation tree")
    tree_parser.add_argument("expression", type=str, help="Mathematical expression")

    args = parser.parse_args()

    if not args.command:
        # Run interactive TUI mode if no subcommand is given
        try:
            run_tui()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting TUI. Goodbye!")
        return

    try:
        if args.command == "diff":
            expr = parse_expression(args.expression)
            if args.steps:
                print(f"=== Step-by-Step Derivation Breakdown for d/d{args.var}({args.expression}) ===")
                steps = render_derivation_steps(expr, args.var)
                for step_num, desc, tree_str in steps:
                    print(f"\n[Step {step_num}] {desc}")
                    print(tree_str)
                final_deriv = differentiate(expr, args.var)
                final_simplified = simplify(final_deriv)
                print(f"\nFinal Derivative (Simplified): {final_simplified}")
            else:
                deriv = differentiate(expr, args.var)
                simplified = simplify(deriv)
                print(f"d/d{args.var}({args.expression}) = {simplified}")

        elif args.command == "int":
            expr = parse_expression(args.expression)
            if args.lower is not None and args.upper is not None:
                # Numerical integration using Simpson's / Trapezoidal rule
                n = 1000
                a = args.lower
                b = args.upper
                h = (b - a) / n
                total = evaluate_expression(expr, {args.var: a}) + evaluate_expression(expr, {args.var: b})
                for i in range(1, n):
                    x_val = a + i * h
                    coeff = 4 if i % 2 != 0 else 2
                    total += coeff * evaluate_expression(expr, {args.var: x_val})
                integral_val = total * (h / 3)
                print(f"Definite Integral of {args.expression} d{args.var} from {a} to {b} ≈ {integral_val:.6f}")
            else:
                antideriv = integrate(expr, args.var)
                simplified = simplify(antideriv)
                print(f"∫ ({args.expression}) d{args.var} = {simplified} + C")

        elif args.command == "lim":
            expr = parse_expression(args.expression)
            p = args.point
            v = args.var
            # Approximate limit by evaluating very close points
            eps = 1e-6
            val_left = evaluate_expression(expr, {v: p - eps})
            val_right = evaluate_expression(expr, {v: p + eps})
            val_center = evaluate_expression(expr, {v: p})
            
            print(f"Limit of {args.expression} as {v} → {p}:")
            print(f"  f({p} - ε) ≈ {val_left:.6f}")
            print(f"  f({p} + ε) ≈ {val_right:.6f}")
            if abs(val_left - val_right) < 1e-3:
                print(f"Estimated Limit: {val_right:.6f}")
            else:
                print(f"Limit may not exist or function diverges (Left: {val_left:.4f}, Right: {val_right:.4f})")

        elif args.command == "simplify":
            expr = parse_expression(args.expression)
            simplified = simplify(expr)
            print(f"Original:   {expr}")
            print(f"Simplified: {simplified}")

        elif args.command == "eval":
            expr = parse_expression(args.expression)
            var_map = {}
            for assignment in args.assignments:
                if "=" in assignment:
                    k, v = assignment.split("=", 1)
                    var_map[k.strip()] = float(v.strip())
            result = evaluate_expression(expr, var_map)
            print(f"Expression: {args.expression}")
            print(f"Assignments: {var_map}")
            print(f"Result: {result}")

        elif args.command == "tree":
            expr = parse_expression(args.expression)
            tree_str = render_tree(expr)
            print(f"Equation Tree for: {args.expression}\n")
            print(tree_str)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
