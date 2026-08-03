"""Formatter for rendering step-by-step differentiation derivation breakdowns."""

from typing import List

from core.differentiator import DerivationStep


def render_derivation_breakdown(
    original_expr: str,
    raw_derivative: str,
    simplified_derivative: str,
    steps: List[DerivationStep],
) -> str:
    """Format step-by-step derivation steps into a clean terminal report."""
    lines = []
    lines.append("════════════════════════════════════════════════════════════════════════")
    lines.append("                 STEP-BY-STEP DERIVATION BREAKDOWN                      ")
    lines.append("════════════════════════════════════════════════════════════════════════")
    lines.append(f" Original Function f(x) : {original_expr}")
    lines.append(f" Raw Derivative f'(x)   : {raw_derivative}")
    lines.append(f" Simplified f'(x)       : {simplified_derivative}")
    lines.append("────────────────────────────────────────────────────────────────────────")

    if not steps:
        lines.append(" No intermediate derivation steps recorded.")
    else:
        for idx, step in enumerate(steps, 1):
            lines.append(f" Step {idx}: {step.rule_name.upper()}")
            lines.append(f"   Target Expr : {step.expression}")
            lines.append(f"   Rule Logic  : {step.explanation}")
            lines.append(f"   Step Result : {step.result}")
            lines.append(f"   Simplified  : {step.simplified_result}")
            lines.append("   " + "─" * 64)

    lines.append("════════════════════════════════════════════════════════════════════════")
    return "\n".join(lines)
