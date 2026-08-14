"""
Comprehensive Unit Tests for Derivation Step Tracker and Tree Visualizer
"""

import pytest
from parser import parse_expr
from differentiator import diff
from tracker import DerivationTracker, DerivationStep


class TestDerivationTracker:
    """Test step-by-step recording of calculus rules and formatted derivation outputs."""

    def test_tracker_initialization(self):
        tracker = DerivationTracker()
        assert len(tracker.steps) == 0
        assert tracker.get_steps() == []

    def test_product_rule_tracking(self):
        tracker = DerivationTracker()
        expr = parse_expr("x * sin(x)")
        res = diff(expr, var="x", tracker=tracker)

        steps = tracker.get_steps()
        assert len(steps) > 0
        assert any("Product Rule" in s.rule_name for s in steps)
        
        formatted = tracker.format_text()
        assert "Product Rule" in formatted
        assert "x" in formatted

    def test_quotient_rule_tracking(self):
        tracker = DerivationTracker()
        expr = parse_expr("(x + 1) / (x - 1)")
        res = diff(expr, var="x", tracker=tracker)

        steps = tracker.get_steps()
        assert len(steps) > 0
        assert any("Quotient Rule" in s.rule_name for s in steps)

    def test_chain_rule_tracking(self):
        tracker = DerivationTracker()
        expr = parse_expr("sin(x^2 + 1)")
        res = diff(expr, var="x", tracker=tracker)

        steps = tracker.get_steps()
        assert len(steps) > 0
        assert any("Chain Rule" in s.rule_name for s in steps)

    def test_rich_tree_and_latex_export(self):
        tracker = DerivationTracker()
        expr = parse_expr("exp(2*x)")
        diff(expr, var="x", tracker=tracker)

        tree = tracker.build_rich_tree()
        assert tree is not None

        latex_steps = tracker.format_latex()
        assert isinstance(latex_steps, list)
        assert len(latex_steps) > 0
