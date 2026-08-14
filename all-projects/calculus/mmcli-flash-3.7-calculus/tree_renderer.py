"""
AST Tree Renderer & Mathematical Notations
==========================================
Visual hierarchical AST tree rendering with Unicode box-drawing characters,
ASCII fallbacks, LaTeX mathematical output, and compact boxed diagrams.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union

try:
    from ast_nodes import (
        Node, Constant, NamedConstant, Variable,
        Add, Subtract, Multiply, Divide, Power, Negate,
        Sin, Cos, Tan, Sec, Csc, Cot,
        Asin, Acos, Atan, Sinh, Cosh, Tanh,
        Exp, Ln, Log, Sqrt, Abs,
        ArcSin, ArcCos, ArcTan,
    )
except ImportError:
    from .ast_nodes import (
        Node, Constant, NamedConstant, Variable,
        Add, Subtract, Multiply, Divide, Power, Negate,
        Sin, Cos, Tan, Sec, Csc, Cot,
        Asin, Acos, Atan, Sinh, Cosh, Tanh,
        Exp, Ln, Log, Sqrt, Abs,
        ArcSin, ArcCos, ArcTan,
    )

try:
    from rich.tree import Tree as RichTree
    from rich.text import Text as RichText
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    RichTree = None  # type: ignore
    RichText = None  # type: ignore
    Panel = None  # type: ignore


# Unicode mathematical superscripts
UNICODE_SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', 'n': 'ⁿ', 'x': 'ˣ', 'y': 'ʸ', '(': '⁽', ')': '⁾'
}


def _get_node_label(node: Node, mode: str = "unicode") -> str:
    """Generate descriptive label for an AST node."""
    cls_name = node.__class__.__name__

    if isinstance(node, Constant):
        return f"Constant({node.value})"
    elif isinstance(node, NamedConstant):
        return f"NamedConstant({node.name} ≈ {node.value:.4g})"
    elif isinstance(node, Variable):
        return f"Variable({node.name})"
    elif isinstance(node, Add):
        return "Add (+)"
    elif isinstance(node, Subtract):
        return "Subtract (-)"
    elif isinstance(node, Multiply):
        return "Multiply (*)"
    elif isinstance(node, Divide):
        return "Divide (/)"
    elif isinstance(node, Power):
        return "Power (^)"
    elif isinstance(node, Negate):
        return "Negate (-)"
    elif isinstance(node, Sin):
        return "Sin (sin)"
    elif isinstance(node, Cos):
        return "Cos (cos)"
    elif isinstance(node, Tan):
        return "Tan (tan)"
    elif isinstance(node, Sec):
        return "Sec (sec)"
    elif isinstance(node, Csc):
        return "Csc (csc)"
    elif isinstance(node, Cot):
        return "Cot (cot)"
    elif isinstance(node, (Asin, ArcSin)):
        return "ArcSin (asin)"
    elif isinstance(node, (Acos, ArcCos)):
        return "ArcCos (acos)"
    elif isinstance(node, (Atan, ArcTan)):
        return "ArcTan (atan)"
    elif isinstance(node, Sinh):
        return "Sinh (sinh)"
    elif isinstance(node, Cosh):
        return "Cosh (cosh)"
    elif isinstance(node, Tanh):
        return "Tanh (tanh)"
    elif isinstance(node, Exp):
        return "Exp (exp)"
    elif isinstance(node, Ln):
        return "Ln (ln)"
    elif isinstance(node, Log):
        return f"Log (base={node.base.value if isinstance(node.base, Constant) else node.base})"
    elif isinstance(node, Sqrt):
        return "Sqrt (√)" if mode == "unicode" else "Sqrt (sqrt)"
    elif isinstance(node, Abs):
        return "Abs (|x|)"
    else:
        return f"{cls_name} ({node.to_infix()})"


def render_ast_tree(
    node: Node,
    prefix: str = "",
    is_last: bool = True,
    use_unicode: bool = True,
    show_values: Optional[Dict[str, float]] = None,
) -> str:
    """
    Render an AST hierarchy as a multi-line tree diagram using Unicode or ASCII box characters.
    """
    lines: List[str] = []

    connector = ("└── " if is_last else "├── ") if use_unicode else ("\\-- " if is_last else "+-- ")
    label = _get_node_label(node, mode="unicode" if use_unicode else "ascii")

    if show_values is not None:
        try:
            val = node.evaluate(show_values)
            label += f" = {val:.4g}"
        except Exception:
            pass

    if prefix == "":
        lines.append(label)
    else:
        lines.append(prefix + connector + label)

    children = node.get_children()
    if use_unicode:
        child_prefix = prefix + ("    " if is_last else "│   ")
    else:
        child_prefix = prefix + ("    " if is_last else "|   ")

    for i, child in enumerate(children):
        is_child_last = (i == len(children) - 1)
        child_str = render_ast_tree(
            child,
            prefix=child_prefix,
            is_last=is_child_last,
            use_unicode=use_unicode,
            show_values=show_values,
        )
        lines.append(child_str)

    return "\n".join(lines)


def render_ascii_tree(node: Node, show_values: Optional[Dict[str, float]] = None) -> str:
    """Render AST hierarchy using pure ASCII branch connectors."""
    return render_ast_tree(node, use_unicode=False, show_values=show_values)


def render_tree(node: Node) -> str:
    """Standard alias for AST tree rendering."""
    return render_ast_tree(node, use_unicode=True)


def to_latex(expr: Node) -> str:
    """Convert AST node to LaTeX notation."""
    return expr.to_latex()


def render_pretty(expr: Node, mode: str = "unicode") -> str:
    """
    Render AST into formatted mathematical notation string.
    Modes:
      - 'unicode': uses Unicode superscripts (x²), Greek letters (π), etc.
      - 'ascii'  : standard ASCII infix format.
      - 'latex'  : LaTeX formatting.
    """
    if mode == "latex":
        return expr.to_latex()

    if mode == "ascii":
        return expr.to_infix()

    # Unicode pretty rendering
    if isinstance(expr, Constant):
        return str(expr.value)

    if isinstance(expr, NamedConstant):
        if expr.name == "pi":
            return "π"
        if expr.name == "tau":
            return "τ"
        if expr.name == "phi":
            return "ϕ"
        return expr.name

    if isinstance(expr, Variable):
        return expr.name

    if isinstance(expr, Negate):
        operand_str = render_pretty(expr.child, mode)
        if isinstance(expr.child, (Add, Subtract)):
            return f"-({operand_str})"
        return f"-{operand_str}"

    if isinstance(expr, Add):
        return f"{render_pretty(expr.left, mode)} + {render_pretty(expr.right, mode)}"

    if isinstance(expr, Subtract):
        left_s = render_pretty(expr.left, mode)
        right_s = render_pretty(expr.right, mode)
        if isinstance(expr.right, (Add, Subtract)):
            return f"{left_s} - ({right_s})"
        return f"{left_s} - {right_s}"

    if isinstance(expr, Multiply):
        l_s = render_pretty(expr.left, mode)
        r_s = render_pretty(expr.right, mode)
        if isinstance(expr.left, (Add, Subtract)):
            l_s = f"({l_s})"
        if isinstance(expr.right, (Add, Subtract)):
            r_s = f"({r_s})"
        # Implicit multiplication for constant * variable or constant * function
        if isinstance(expr.left, (Constant, NamedConstant)) and isinstance(
            expr.right, (Variable, Sin, Cos, Tan, Exp, Ln, Sqrt, Abs)
        ):
            return f"{l_s}{r_s}"
        return f"{l_s} · {r_s}"

    if isinstance(expr, Divide):
        l_s = render_pretty(expr.left, mode)
        r_s = render_pretty(expr.right, mode)
        if isinstance(expr.left, (Add, Subtract)):
            l_s = f"({l_s})"
        if isinstance(expr.right, (Add, Subtract, Multiply, Divide)):
            r_s = f"({r_s})"
        return f"{l_s} / {r_s}"

    if isinstance(expr, Power):
        base_s = render_pretty(expr.left, mode)
        if isinstance(expr.left, (Add, Subtract, Multiply, Divide, Negate)):
            base_s = f"({base_s})"
        # Check if exponent can be rendered as Unicode superscript
        exp_val_str = str(expr.right.value) if isinstance(expr.right, Constant) else None
        if exp_val_str and all(ch in UNICODE_SUPERSCRIPTS for ch in exp_val_str):
            sup = "".join(UNICODE_SUPERSCRIPTS[ch] for ch in exp_val_str)
            return f"{base_s}{sup}"
        exp_s = render_pretty(expr.right, mode)
        return f"{base_s}^{exp_s}" if not isinstance(expr.right, (Add, Subtract)) else f"{base_s}^({exp_s})"

    if isinstance(expr, Sqrt):
        return f"√({render_pretty(expr.child, mode)})"

    if isinstance(expr, Abs):
        return f"|{render_pretty(expr.child, mode)}|"

    if isinstance(expr, Exp):
        return f"e^({render_pretty(expr.child, mode)})"

    if isinstance(expr, Ln):
        return f"ln({render_pretty(expr.child, mode)})"

    if isinstance(expr, Sin):
        return f"sin({render_pretty(expr.child, mode)})"

    if isinstance(expr, Cos):
        return f"cos({render_pretty(expr.child, mode)})"

    if isinstance(expr, Tan):
        return f"tan({render_pretty(expr.child, mode)})"

    return expr.to_infix()


class ASTVisualizer:
    """Helper class for interactive AST tree inspection and visualization."""

    @staticmethod
    def render_rich(node: Node) -> Any:
        """Return Rich Tree structure if Rich is available, otherwise plain string."""
        if HAS_RICH:
            return node.to_rich_tree()
        return render_tree(node)

    @staticmethod
    def render_horizontal_boxed(node: Node) -> str:
        """Render a horizontal boxed visual expression layout."""
        lines = []
        infix = render_pretty(node, mode="unicode")
        box_width = len(infix) + 4
        lines.append("┌" + "─" * (box_width - 2) + "┐")
        lines.append(f"│ {infix} │")
        lines.append("└" + "─" * (box_width - 2) + "┘")
        return "\n".join(lines)
