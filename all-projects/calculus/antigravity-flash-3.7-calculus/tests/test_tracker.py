"""
Unit tests for Derivation Step Tracker
"""

import pytest
from engine.parser import parse_expr
from engine.differentiator import diff
from engine.tracker import DerivationTracker


def test_derivation_tracking_product_rule():
    expr = parse_expr("x * sin(x)")
    tracker = DerivationTracker()
    diff(expr, var="x", tracker=tracker)

    steps = tracker.get_steps()
    assert len(steps) > 0
    # Top rule should be Product Rule
    assert any("Product Rule" in s.rule_name for s in steps)
    
    text_rep = tracker.format_text()
    assert "Product Rule" in text_rep
    assert "sin(x)" in text_rep


def test_derivation_tracking_quotient_rule():
    expr = parse_expr("(x + 1) / (x - 1)")
    tracker = DerivationTracker()
    diff(expr, var="x", tracker=tracker)

    steps = tracker.get_steps()
    assert len(steps) > 0
    assert any("Quotient Rule" in s.rule_name for s in steps)
    
    tree = tracker.build_rich_tree()
    assert tree is not None
