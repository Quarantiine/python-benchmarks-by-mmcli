"""
Tests for TUI components and StepByStepEngine math reasoning output.
"""

import pytest
from calculus.tui import StepByStepEngine, SymbolicCalculusTUI


def test_step_by_step_differentiation():
    res = StepByStepEngine.explain_diff("3*x^2 + 2*x + 1", "x")
    assert res["success"] is True
    assert len(res["steps"]) >= 4
    assert "Parsed expression" in res["steps"][0]
    assert "Sum Rule" in res["steps"][1] or "Applied" in res["steps"][1]
    assert "Simplified derivative" in res["steps"][-1]
    assert "6" in res["unicode"]


def test_step_by_step_integration():
    # Indefinite
    res_indef = StepByStepEngine.explain_integrate("x^2", "x")
    assert res_indef["success"] is True
    assert "Antiderivative Search" in res_indef["steps"][1]

    # Definite
    res_def = StepByStepEngine.explain_integrate("3*x^2", "x", lower_str="0", upper_str="2")
    assert res_def["success"] is True
    assert "Definite Integral" in res_def["steps"][1]
    assert res_def["result_expr"] == 8.0


def test_step_by_step_limit():
    res = StepByStepEngine.explain_limit("sin(x) / x", "x", "0")
    assert res["success"] is True
    assert res["result_expr"] == 1.0


def test_step_by_step_simplify():
    res = StepByStepEngine.explain_simplify("x + 0 + x * 1")
    assert res["success"] is True
    assert "Simplified result" in res["steps"][-1]


def test_step_by_step_eval():
    res = StepByStepEngine.explain_eval("x^2 + y", {"x": 3, "y": 4})
    assert res["success"] is True
    assert res["result_expr"] == 13.0


def test_symbolic_calculus_tui_state():
    tui = SymbolicCalculusTUI()
    assert tui.expr_str == "x^3 + 2*x^2 + sin(x)"
    op_key, op_name, _ = tui.get_current_op()
    assert op_key == "1"
    assert op_name == "Differentiate"

    # Test compute_current
    res = tui.compute_current()
    assert res["success"] is True

    # Switch op to Integrate
    tui.selected_op_idx = 1
    res_int = tui.compute_current()
    assert res_int["success"] is True
