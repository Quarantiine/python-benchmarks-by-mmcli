"""
CLI entry point for Symbolic Calculus Engine.
Supports interactive TUI mode and direct command-line argument evaluation.
"""

import sys
import argparse
from typing import List, Optional, Dict, Any

from calculus import (
    parse, diff, integrate, limit, simplify, render_pretty, to_latex, render_tree
)
from calculus.tui import main as tui_main, StepByStepEngine


def create_parser() -> argparse.ArgumentParser:
    """Build and return argument parser for symbolic calculus CLI."""
    parser = argparse.ArgumentParser(
        prog="symbolic-calculus",
        description="Symbolic Calculus Engine & Interactive Terminal User Interface (TUI)",
        epilog="If no command is specified, interactive TUI mode will launch."
    )

    parser.add_argument(
        "--tui", "-i", action="store_true",
        help="Launch interactive TUI mode."
    )

    subparsers = parser.add_subparsers(dest="command", help="Calculus Operation Subcommands")

    # Interactive subcommands
    subparsers.add_parser("tui", help="Launch interactive TUI mode.")
    subparsers.add_parser("interactive", help="Launch interactive TUI mode.")

    # Differentiate
    diff_parser = subparsers.add_parser(
        "diff",
        aliases=["differentiate", "derivative"],
        help="Compute derivative of an expression"
    )
    diff_parser.add_argument("expression", nargs="+", help="Mathematical expression (e.g. 'x^3 + sin(x)')")
    diff_parser.add_argument("-v", "--var", default="x", help="Variable to differentiate with respect to (default: x)")
    diff_parser.add_argument("--steps", action="store_true", default=True, help="Show step-by-step breakdown (default: True)")
    diff_parser.add_argument("--no-steps", action="store_false", dest="steps", help="Disable step-by-step breakdown")
    diff_parser.add_argument("-f", "--format", choices=["unicode", "latex", "ascii", "tree", "all"], default="all", help="Output format style")

    # Integrate
    int_parser = subparsers.add_parser(
        "int",
        aliases=["integrate", "integral"],
        help="Compute indefinite or definite integral"
    )
    int_parser.add_argument("expression", nargs="+", help="Mathematical integrand expression")
    int_parser.add_argument("-v", "--var", default="x", help="Variable of integration (default: x)")
    int_parser.add_argument("-l", "--lower", default=None, help="Lower limit for definite integral")
    int_parser.add_argument("-u", "--upper", default=None, help="Upper limit for definite integral")
    int_parser.add_argument("--steps", action="store_true", default=True, help="Show step-by-step breakdown")
    int_parser.add_argument("--no-steps", action="store_false", dest="steps", help="Disable step-by-step breakdown")
    int_parser.add_argument("-f", "--format", choices=["unicode", "latex", "ascii", "tree", "all"], default="all", help="Output format style")

    # Limit
    lim_parser = subparsers.add_parser(
        "lim",
        aliases=["limit"],
        help="Compute limit of an expression"
    )
    lim_parser.add_argument("expression", nargs="+", help="Mathematical expression")
    lim_parser.add_argument("-v", "--var", default="x", help="Variable name (default: x)")
    lim_parser.add_argument("-p", "--at", "--point", dest="point", default="0", help="Limit point target value (default: 0)")
    lim_parser.add_argument("-d", "--dir", "--direction", dest="direction", choices=["both", "left", "right"], default="both", help="Limit direction (default: both)")
    lim_parser.add_argument("--steps", action="store_true", default=True, help="Show step-by-step breakdown")
    lim_parser.add_argument("--no-steps", action="store_false", dest="steps", help="Disable step-by-step breakdown")
    lim_parser.add_argument("-f", "--format", choices=["unicode", "latex", "ascii", "tree", "all"], default="all", help="Output format style")

    # Simplify
    simp_parser = subparsers.add_parser(
        "simplify",
        aliases=["simp"],
        help="Simplify algebraic expression"
    )
    simp_parser.add_argument("expression", nargs="+", help="Mathematical expression to simplify")
    simp_parser.add_argument("--steps", action="store_true", default=True, help="Show step-by-step breakdown")
    simp_parser.add_argument("--no-steps", action="store_false", dest="steps", help="Disable step-by-step breakdown")
    simp_parser.add_argument("-f", "--format", choices=["unicode", "latex", "ascii", "tree", "all"], default="all", help="Output format style")

    # Evaluate
    eval_parser = subparsers.add_parser(
        "eval",
        aliases=["evaluate"],
        help="Evaluate expression with variable values"
    )
    eval_parser.add_argument("expression", nargs="+", help="Mathematical expression followed optionally by key=val assignments")
    eval_parser.add_argument("-v", "--var", action="append", help="Variable assignment key=val (e.g. -v x=3)")

    # Tree / AST
    tree_parser = subparsers.add_parser(
        "tree",
        aliases=["ast"],
        help="Print AST tree representation of expression"
    )
    tree_parser.add_argument("expression", nargs="+", help="Mathematical expression")

    return parser


def parse_eval_args(tokens: List[str], var_flags: Optional[List[str]] = None) -> tuple[str, Dict[str, float]]:
    """Parse expression and key=val bindings from eval positional args and flags."""
    var_bindings: Dict[str, float] = {}
    expr_parts: List[str] = []

    for tok in tokens:
        if "=" in tok:
            k, v = tok.split("=", 1)
            try:
                var_bindings[k.strip()] = float(v.strip())
            except ValueError:
                expr_parts.append(tok)
        else:
            expr_parts.append(tok)

    if var_flags:
        for vf in var_flags:
            if "=" in vf:
                k, v = vf.split("=", 1)
                try:
                    var_bindings[k.strip()] = float(v.strip())
                except ValueError:
                    pass

    expr_str = " ".join(expr_parts)
    return expr_str, var_bindings


def format_result_output(res: Dict[str, Any], show_steps: bool = True, fmt: str = "all") -> str:
    """Format the evaluation dictionary result into display string."""
    if not res.get("success", False):
        return f"Error: {res.get('error', 'Unknown calculation error')}"

    lines = []
    if show_steps and res.get("steps"):
        lines.append("Step-by-Step Breakdown:")
        for step in res["steps"]:
            lines.append(f"  • {step}")
        lines.append("")

    unicode_val = res.get("unicode", "")
    latex_val = res.get("latex", "")
    tree_val = res.get("tree", "")

    if fmt == "unicode":
        lines.append(f"Unicode: {unicode_val}")
    elif fmt == "latex":
        lines.append(f"LaTeX: {latex_val}")
    elif fmt == "ascii":
        if "input_expr" in res and hasattr(res["result_expr"], "eval"):
            ascii_val = render_pretty(res["result_expr"], "ascii")
        else:
            ascii_val = unicode_val
        lines.append(f"ASCII: {ascii_val}")
    elif fmt == "tree":
        lines.append("AST Tree:")
        lines.append(tree_val)
    else:  # "all"
        lines.append(f"Unicode: {unicode_val}")
        lines.append(f"LaTeX  : {latex_val}")
        if tree_val:
            lines.append("AST Tree:")
            lines.append(tree_val)

    return "\n".join(lines)


def run_cli(args_list: Optional[List[str]] = None) -> int:
    """Run CLI argument processor. Returns exit code (0 for success, 1 for failure)."""
    parser = create_parser()
    
    # If no args passed to CLI or empty sys.argv, launch interactive mode
    if args_list is None:
        args_list = sys.argv[1:]

    if not args_list or args_list == ["--tui"] or args_list == ["-i"]:
        tui_main()
        return 0

    try:
        args = parser.parse_args(args_list)
    except SystemExit as err:
        return err.code if isinstance(err.code, int) else 0

    if args.tui or args.command in ("tui", "interactive"):
        tui_main()
        return 0

    cmd = args.command
    if not cmd:
        tui_main()
        return 0

    if cmd in ("diff", "differentiate", "derivative"):
        expr_str = " ".join(args.expression)
        res = StepByStepEngine.explain_diff(expr_str, var_str=args.var)
        print(format_result_output(res, show_steps=args.steps, fmt=args.format))
        return 0 if res["success"] else 1

    elif cmd in ("int", "integrate", "integral"):
        expr_str = " ".join(args.expression)
        res = StepByStepEngine.explain_integrate(
            expr_str, var_str=args.var, lower_str=args.lower, upper_str=args.upper
        )
        print(format_result_output(res, show_steps=args.steps, fmt=args.format))
        return 0 if res["success"] else 1

    elif cmd in ("lim", "limit"):
        expr_str = " ".join(args.expression)
        res = StepByStepEngine.explain_limit(
            expr_str, var_str=args.var, point_str=args.point, direction=args.direction
        )
        print(format_result_output(res, show_steps=args.steps, fmt=args.format))
        return 0 if res["success"] else 1

    elif cmd in ("simplify", "simp"):
        expr_str = " ".join(args.expression)
        res = StepByStepEngine.explain_simplify(expr_str)
        print(format_result_output(res, show_steps=args.steps, fmt=args.format))
        return 0 if res["success"] else 1

    elif cmd in ("eval", "evaluate"):
        expr_str, var_map = parse_eval_args(args.expression, getattr(args, "var", None))
        res = StepByStepEngine.explain_eval(expr_str, var_map)
        print(format_result_output(res, show_steps=True, fmt="unicode"))
        return 0 if res["success"] else 1

    elif cmd in ("tree", "ast"):
        expr_str = " ".join(args.expression)
        try:
            parsed = parse(expr_str)
            print(f"AST Tree for '{expr_str}':\n")
            print(render_tree(parsed))
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    else:
        parser.print_help()
        return 1


def main():
    """Main execution entry point."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
