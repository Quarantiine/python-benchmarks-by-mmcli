"""
Derivation Step Tracker
=======================
Records, structures, and formats hierarchical step-by-step calculus derivations.
Supports rule names, formulas, expressions, intermediate/simplified values,
and tree-based visual formatting.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from rich.tree import Tree as RichTree
    from rich.text import Text as RichText
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    RichTree = None  # type: ignore
    RichText = None  # type: ignore


@dataclass
class DerivationStep:
    """Represents a single step in a symbolic differentiation derivation."""
    rule_name: str
    rule_formula: str
    input_expr: str
    target_var: str
    raw_result: Optional[str] = None
    simplified_result: Optional[str] = None
    notes: Optional[str] = None
    child_steps: List[DerivationStep] = field(default_factory=list)
    depth: int = 0

    def add_child(self, child: DerivationStep) -> None:
        """Add a sub-derivation step."""
        child.depth = self.depth + 1
        self.child_steps.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize derivation step to dictionary format."""
        return {
            "rule_name": self.rule_name,
            "rule_formula": self.rule_formula,
            "input_expr": self.input_expr,
            "target_var": self.target_var,
            "raw_result": self.raw_result,
            "simplified_result": self.simplified_result,
            "notes": self.notes,
            "depth": self.depth,
            "child_steps": [c.to_dict() for c in self.child_steps]
        }

    def format_text(self, indent: int = 0) -> str:
        """Format derivation step and its children as indented plain text."""
        prefix = "  " * indent
        lines = [f"{prefix}• [{self.rule_name}] d/d{self.target_var}[ {self.input_expr} ]"]
        if self.rule_formula:
            lines.append(f"{prefix}  Formula: {self.rule_formula}")
        if self.notes:
            lines.append(f"{prefix}  Note: {self.notes}")
        for child in self.child_steps:
            lines.append(child.format_text(indent + 1))
        if self.raw_result and self.raw_result != self.input_expr:
            lines.append(f"{prefix}  ↳ Result: {self.raw_result}")
        if self.simplified_result and self.simplified_result != self.raw_result:
            lines.append(f"{prefix}  ↳ Simplified: {self.simplified_result}")
        return "\n".join(lines)


class DerivationTracker:
    """Manages the hierarchical stack of differentiation steps."""

    def __init__(self) -> None:
        self.root_steps: List[DerivationStep] = []
        self._stack: List[DerivationStep] = []

    @property
    def steps(self) -> List[DerivationStep]:
        return self.root_steps

    def format_latex(self) -> List[str]:
        """Return LaTeX representation of derivation steps."""
        lines = []
        for step in self.root_steps:
            lines.append(f"\\frac{{d}}{{d{step.target_var}}}\\left[{step.input_expr}\\right] = {step.simplified_result or step.raw_result or step.input_expr}")
        return lines

    def start_step(
        self,
        rule_name: str,
        rule_formula: str,
        input_expr: str,
        target_var: str,
        notes: Optional[str] = None
    ) -> DerivationStep:
        """Start tracking a new derivation step."""
        depth = len(self._stack)
        step = DerivationStep(
            rule_name=rule_name,
            rule_formula=rule_formula,
            input_expr=input_expr,
            target_var=target_var,
            notes=notes,
            depth=depth
        )
        if self._stack:
            self._stack[-1].add_child(step)
        else:
            self.root_steps.append(step)
        self._stack.append(step)
        return step

    def end_step(
        self,
        raw_result: Optional[str] = None,
        simplified_result: Optional[str] = None
    ) -> Optional[DerivationStep]:
        """Complete the current derivation step and record its results."""
        if not self._stack:
            return None
        step = self._stack.pop()
        if raw_result is not None:
            step.raw_result = raw_result
        if simplified_result is not None:
            step.simplified_result = simplified_result
        return step

    def get_steps(self) -> List[DerivationStep]:
        """Return top-level derivation steps."""
        return self.root_steps

    def clear(self) -> None:
        """Clear recorded steps."""
        self.root_steps.clear()
        self._stack.clear()

    def format_text(self) -> str:
        """Return plain text formatted derivation breakdown."""
        if not self.root_steps:
            return "No derivation steps recorded."
        return "\n\n".join(step.format_text() for step in self.root_steps)

    def to_tree_string(self) -> str:
        """Return tree visualization string."""
        return self.format_text()

    def build_rich_tree(self) -> Any:
        """Generate a Rich Tree visual breakdown."""
        if not HAS_RICH:
            return self.format_text()

        root_label = RichText("Step-by-Step Derivation Breakdown", style="bold cyan")
        tree = RichTree(root_label)

        def _add_to_tree(parent: Any, step: DerivationStep) -> None:
            header = RichText()
            header.append("• ", style="bold green")
            header.append(f"[{step.rule_name}] ", style="bold yellow")
            header.append(f"d/d{step.target_var}[ ", style="white")
            header.append(step.input_expr, style="bold bright_white")
            header.append(" ]", style="white")

            node = parent.add(header)
            if step.rule_formula:
                formula_txt = RichText("  Formula: ", style="dim")
                formula_txt.append(step.rule_formula, style="italic cyan")
                node.add(formula_txt)
            if step.notes:
                notes_txt = RichText("  Note: ", style="dim")
                notes_txt.append(step.notes, style="italic")
                node.add(notes_txt)

            for child in step.child_steps:
                _add_to_tree(node, child)

            if step.raw_result:
                res_txt = RichText("  ↳ Result: ", style="bold green")
                res_txt.append(step.raw_result, style="bright_white")
                node.add(res_txt)
            if step.simplified_result and step.simplified_result != step.raw_result:
                sim_txt = RichText("  ↳ Simplified: ", style="bold gold1")
                sim_txt.append(step.simplified_result, style="bold bright_yellow")
                node.add(sim_txt)

        for step in self.root_steps:
            _add_to_tree(tree, step)

        return tree
