"""
Pretty Rendering engine for symbolic calculus expressions.

Provides LaTeX rendering, Unicode math formatting, and ASCII expression AST tree visualization.
"""

from calculus.ast import (
    Expr, Const, Symbol, Add, Sub, Mul, Div, Pow, Neg,
    Sin, Cos, Tan, Exp, Ln, Sqrt, Abs
)

# Superscript dictionary for Unicode math rendering
SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', 'n': 'ⁿ', 'x': 'ˣ'
}


def to_latex(expr: Expr) -> str:
    """Convert symbolic expression AST into a LaTeX string representation."""
    if isinstance(expr, Const):
        return str(expr.value)

    if isinstance(expr, Symbol):
        if expr.name.lower() == "pi":
            return r"\pi"
        if expr.name.lower() == "e":
            return "e"
        return expr.name

    if isinstance(expr, Neg):
        sub_latex = to_latex(expr.operand)
        if isinstance(expr.operand, (Add, Sub)):
            return f"-\\left({sub_latex}\\right)"
        return f"-{sub_latex}"

    if isinstance(expr, Add):
        left_str = to_latex(expr.left)
        right_str = to_latex(expr.right)
        if isinstance(expr.right, Neg):
            return f"{left_str} - {to_latex(expr.right.operand)}"
        return f"{left_str} + {right_str}"

    if isinstance(expr, Sub):
        left_str = to_latex(expr.left)
        right_str = to_latex(expr.right)
        if isinstance(expr.right, (Add, Sub)):
            return f"{left_str} - \\left({right_str}\\right)"
        return f"{left_str} - {right_str}"

    if isinstance(expr, Mul):
        left_latex = _latex_factor(expr.left)
        right_latex = _latex_factor(expr.right)

        # Skip multiplication dot for constant times variable/func or symbol times symbol
        if isinstance(expr.left, Const) or isinstance(expr.right, (Symbol, Sin, Cos, Tan, Exp, Ln, Sqrt, Pow)):
            return f"{left_latex} {right_latex}"
        return f"{left_latex} \\cdot {right_latex}"

    if isinstance(expr, Div):
        num_latex = to_latex(expr.left)
        den_latex = to_latex(expr.right)
        return f"\\frac{{{num_latex}}}{{{den_latex}}}"

    if isinstance(expr, Pow):
        base_latex = to_latex(expr.left)
        if isinstance(expr.left, (Add, Sub, Mul, Div, Neg)):
            base_latex = f"\\left({base_latex}\\right)"
        exp_latex = to_latex(expr.right)
        return f"{{{base_latex}}}^{{{exp_latex}}}"

    if isinstance(expr, Sin):
        return f"\\sin\\left({to_latex(expr.operand)}\\right)"

    if isinstance(expr, Cos):
        return f"\\cos\\left({to_latex(expr.operand)}\\right)"

    if isinstance(expr, Tan):
        return f"\\tan\\left({to_latex(expr.operand)}\\right)"

    if isinstance(expr, Exp):
        return f"e^{{{to_latex(expr.operand)}}}"

    if isinstance(expr, Ln):
        return f"\\ln\\left({to_latex(expr.operand)}\\right)"

    if isinstance(expr, Sqrt):
        return f"\\sqrt{{{to_latex(expr.operand)}}}"

    if isinstance(expr, Abs):
        return f"\\left|{to_latex(expr.operand)}\\right|"

    return str(expr)


def _latex_factor(expr: Expr) -> str:
    s = to_latex(expr)
    if isinstance(expr, (Add, Sub)):
        return f"\\left({s}\\right)"
    return s


def render_pretty(expr: Expr, mode: str = "unicode") -> str:
    """Render AST into formatted mathematical notation string (Unicode or ASCII)."""
    if mode == "latex":
        return to_latex(expr)

    if isinstance(expr, Const):
        return str(expr.value)

    if isinstance(expr, Symbol):
        if mode == "unicode" and expr.name.lower() == "pi":
            return "π"
        return expr.name

    if isinstance(expr, Neg):
        sub_str = render_pretty(expr.operand, mode)
        if isinstance(expr.operand, (Add, Sub)):
            return f"-({sub_str})"
        return f"-{sub_str}"

    if isinstance(expr, Add):
        left_str = render_pretty(expr.left, mode)
        right_str = render_pretty(expr.right, mode)
        return f"{left_str} + {right_str}"

    if isinstance(expr, Sub):
        left_str = render_pretty(expr.left, mode)
        right_str = render_pretty(expr.right, mode)
        if isinstance(expr.right, (Add, Sub)):
            return f"{left_str} - ({right_str})"
        return f"{left_str} - {right_str}"

    if isinstance(expr, Mul):
        left_str = render_pretty(expr.left, mode)
        right_str = render_pretty(expr.right, mode)

        if isinstance(expr.left, (Add, Sub)):
            left_str = f"({left_str})"
        if isinstance(expr.right, (Add, Sub)):
            right_str = f"({right_str})"

        # Omit '*' for constant times symbol/func or implicit multiplication
        if isinstance(expr.left, Const) or isinstance(expr.right, (Symbol, Sin, Cos, Tan, Exp, Ln, Sqrt, Pow)):
            return f"{left_str}{right_str}"
        return f"{left_str} * {right_str}"

    if isinstance(expr, Div):
        left_str = render_pretty(expr.left, mode)
        right_str = render_pretty(expr.right, mode)
        if isinstance(expr.left, (Add, Sub)):
            left_str = f"({left_str})"
        if isinstance(expr.right, (Add, Sub, Mul, Div)):
            right_str = f"({right_str})"
        return f"{left_str} / {right_str}"

    if isinstance(expr, Pow):
        base_str = render_pretty(expr.left, mode)
        if isinstance(expr.left, (Add, Sub, Mul, Div, Neg)):
            base_str = f"({base_str})"

        exp_str = render_pretty(expr.right, mode)
        if mode == "unicode" and isinstance(expr.right, Const) and str(expr.right.value) in SUPERSCRIPTS:
            return f"{base_str}{SUPERSCRIPTS[str(expr.right.value)]}"
        return f"{base_str}^{exp_str}" if not isinstance(expr.right, (Add, Sub)) else f"{base_str}^({exp_str})"

    if isinstance(expr, Sin):
        return f"sin({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Cos):
        return f"cos({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Tan):
        return f"tan({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Exp):
        if mode == "unicode":
            return f"e^({render_pretty(expr.operand, mode)})"
        return f"exp({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Ln):
        return f"ln({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Sqrt):
        symbol = "√" if mode == "unicode" else "sqrt"
        return f"{symbol}({render_pretty(expr.operand, mode)})"

    if isinstance(expr, Abs):
        return f"|{render_pretty(expr.operand, mode)}|"

    return str(expr)


def render_tree(expr: Expr, prefix: str = "", is_last: bool = True) -> str:
    """Render AST as a multi-line ASCII tree diagram."""
    lines = []
    connector = "└── " if is_last else "├── "

    if prefix == "":
        node_str = f"{expr.__class__.__name__}"
    else:
        node_str = f"{prefix}{connector}{expr.__class__.__name__}"

    if isinstance(expr, Const):
        node_str += f"({expr.value})"
    elif isinstance(expr, Symbol):
        node_str += f"('{expr.name}')"

    lines.append(node_str)

    children = []
    if hasattr(expr, 'left') and hasattr(expr, 'right'):
        children = [expr.left, expr.right]
    elif hasattr(expr, 'operand'):
        children = [expr.operand]

    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(children):
        is_child_last = (i == len(children) - 1)
        lines.append(render_tree(child, child_prefix, is_child_last))

    return "\n".join(lines)
