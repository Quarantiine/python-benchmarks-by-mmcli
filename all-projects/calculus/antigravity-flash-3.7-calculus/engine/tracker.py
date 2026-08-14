"""
Derivation Step Tracker
=======================
Records, structures, and formats step-by-step calculus derivations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional
from rich.tree import Tree
from rich.text import Text


@dataclass
class DerivationStep:
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
        child.depth = self.depth + 1
        self.child_steps.append(child)

    def to_dict(self) -> dict[str, Any]:
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
        prefix = "  " * indent
        lines = []
        lines.append(f"{prefix}• [{self.rule_name}] d/d{self.target_var}[ {self.input_expr} ]")
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

    def start_step(
        self,
        rule_name: str,
        rule_formula: str,
        input_expr: str,
        target_var: str,
        notes: Optional[str] = None
    ) -> DerivationStep:
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
        if not self._stack:
            return None
        step = self._stack.pop()
        if raw_result is not None:
            step.raw_result = raw_result
        if simplified_result is not None:
            step.simplified_result = simplified_result
        return step

    def get_steps(self) -> List[DerivationStep]:
        return self.root_steps

    def clear(self) -> None:
        self.root_steps.clear()
        self._stack.clear()

    def format_text(self) -> str:
        if not self.root_steps:
            return "No derivation steps recorded."
        return "\n\n".join(step.format_text() for step in self.root_steps)

    def build_rich_tree(self) -> Tree:
        root_label = Text("Step-by-Step Derivation Breakdown", style="bold cyan")
        tree = Tree(root_label)
        for step in self.root_steps:
            self._populate_rich_tree(tree, step)
        return tree

    def _populate_rich_tree(self, parent_tree: Tree, step: DerivationStep) -> None:
        step_text = Text()
        step_text.append(f"[{step.rule_name}] ", style="bold yellow")
        step_text.append(f"d/d{step.target_var}", style="bold green")
        step_text.append(f"[ {step.input_expr} ]", style="bold white")
        
        if step.rule_formula:
            step_text.append(f"\n  Rule: {step.rule_formula}", style="dim italic cyan")
        if step.notes:
            step_text.append(f"\n  Note: {step.notes}", style="italic magenta")
        if step.raw_result:
            step_text.append(f"\n  ↳ Raw: {step.raw_result}", style="dim white")
        if step.simplified_result:
            step_text.append(f"\n  ↳ Simplified: {step.simplified_result}", style="bold bright_green")

        node = parent_tree.add(step_text)
        for child in step.child_steps:
            self._populate_rich_tree(node, child)
