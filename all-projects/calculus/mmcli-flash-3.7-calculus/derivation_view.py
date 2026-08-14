"""
Step-by-Step Derivation Viewer & Mathematical Breakdown Formatter
================================================================
Rich and Unicode terminal view generators for calculus derivation steps,
algebraic transformation trees, differentiation rule applications,
and intermediate/simplified formulas.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union

try:
    from tracker import DerivationStep, DerivationTracker
    from ast_nodes import Node
    from differentiator import diff
    from simplifier import simplify
    from parser import parse_expr
except ImportError:
    from .tracker import DerivationStep, DerivationTracker
    from .ast_nodes import Node
    from .differentiator import diff
    from .simplifier import simplify
    from .parser import parse_expr

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.tree import Tree as RichTree
    from rich.text import Text as RichText
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None  # type: ignore
    Panel = None  # type: ignore
    Table = None  # type: ignore
    RichTree = None  # type: ignore
    RichText = None  # type: ignore


def render_derivation_breakdown(
    original_expr: str,
    raw_derivative: str,
    simplified_derivative: str,
    steps: Optional[Union[List[DerivationStep], DerivationTracker]] = None,
    var: str = "x",
) -> str:
    """
    Format step-by-step differentiation derivation steps into a clean terminal report.
    """
    lines = []
    lines.append("═" * 74)
    lines.append("                   STEP-BY-STEP DERIVATION BREAKDOWN                      ")
    lines.append("═" * 74)
    lines.append(f" Original Function f({var}) : {original_expr}")
    lines.append(f" Raw Derivative f'({var})   : {raw_derivative}")
    lines.append(f" Simplified f'({var})       : {simplified_derivative}")
    lines.append("─" * 74)

    step_list: List[DerivationStep] = []
    if isinstance(steps, DerivationTracker):
        step_list = steps.root_steps
    elif isinstance(steps, list):
        step_list = steps

    if not step_list:
        lines.append(" No intermediate derivation steps recorded.")
    else:
        for idx, step in enumerate(step_list, 1):
            _format_step_box(step, idx, lines)

    lines.append("═" * 74)
    return "\n".join(lines)


def _format_step_box(step: DerivationStep, idx: int, lines: List[str], indent: int = 0) -> None:
    prefix = "  " * indent
    lines.append(f"{prefix}Step {idx}: {step.rule_name.upper()}")
    lines.append(f"{prefix}  • Target Expr : d/d{step.target_var}[ {step.input_expr} ]")
    if step.rule_formula:
        lines.append(f"{prefix}  • Rule Logic  : {step.rule_formula}")
    if step.notes:
        lines.append(f"{prefix}  • Notes       : {step.notes}")
    if step.raw_result:
        lines.append(f"{prefix}  • Step Result : {step.raw_result}")
    if step.simplified_result and step.simplified_result != step.raw_result:
        lines.append(f"{prefix}  • Simplified  : {step.simplified_result}")

    if step.child_steps:
        lines.append(f"{prefix}  ┌─ Sub-steps:")
        for c_idx, child in enumerate(step.child_steps, 1):
            _format_step_box(child, c_idx, lines, indent + 2)
        lines.append(f"{prefix}  └───────────")
    lines.append(f"{prefix}  " + "─" * (68 - len(prefix)))


def format_derivation_steps(tracker: DerivationTracker) -> str:
    """Format all steps in a DerivationTracker into readable text."""
    if not tracker.root_steps:
        return "No derivation steps recorded."
    return "\n".join(step.format_text() for step in tracker.root_steps)


class DerivationViewer:
    """Calculus Derivation Inspector and Visualization Generator."""

    @staticmethod
    def explain(
        expr: Union[Node, str],
        var: str = "x",
        order: int = 1,
    ) -> Dict[str, Any]:
        """
        Compute derivative with step tracking and produce comprehensive explanation dictionary.
        """
        ast = parse_expr(expr) if isinstance(expr, str) else expr
        tracker = DerivationTracker()
        
        curr_expr = ast
        for o in range(1, order + 1):
            curr_expr = diff(curr_expr, var=var, tracker=tracker, simplify_result=True)

        raw_str = tracker.root_steps[-1].raw_result if tracker.root_steps else curr_expr.to_infix()
        sim_str = curr_expr.to_infix()

        text_report = render_derivation_breakdown(
            original_expr=ast.to_infix(),
            raw_derivative=raw_str or sim_str,
            simplified_derivative=sim_str,
            steps=tracker,
            var=var,
        )

        return {
            "input_expr": ast,
            "result_expr": curr_expr,
            "order": order,
            "var": var,
            "tracker": tracker,
            "report_text": text_report,
            "steps_text": format_derivation_steps(tracker),
            "latex_result": curr_expr.to_latex(),
        }

    @staticmethod
    def render_rich_panel(tracker: DerivationTracker, title: str = "Step-by-Step Derivation") -> Any:
        """Create a Rich Panel containing a formatted derivation tree."""
        if not HAS_RICH:
            return format_derivation_steps(tracker)
        rich_tree = tracker.build_rich_tree()
        return Panel(rich_tree, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow")

    @staticmethod
    def render_rich_table(tracker: DerivationTracker) -> Any:
        """Create a Rich Table of derivation steps."""
        if not HAS_RICH:
            return format_derivation_steps(tracker)

        table = Table(title="Calculus Rules Applied", border_style="bright_blue", expand=True)
        table.add_column("Step", style="bold cyan", width=6)
        table.add_column("Rule", style="bold yellow", width=22)
        table.add_column("Expression", style="white")
        table.add_column("Result", style="bold green")

        def _add_rows(step: DerivationStep, prefix: str):
            table.add_row(
                prefix,
                step.rule_name,
                f"d/d{step.target_var}[ {step.input_expr} ]",
                step.simplified_result or step.raw_result or "—"
            )
            for idx, child in enumerate(step.child_steps, 1):
                _add_rows(child, f"{prefix}.{idx}")

        for i, root in enumerate(tracker.root_steps, 1):
            _add_rows(root, str(i))

        return table
