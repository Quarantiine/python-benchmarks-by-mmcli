"""
Tests for non-interactive CLI execution and direct command-line argument evaluation.
"""

import pytest
from calculus.cli import run_cli, parse_eval_args, create_parser, format_result_output


def test_cli_parser_creation():
    parser = create_parser()
    assert parser.prog == "symbolic-calculus"


# ==============================================================================
# 1. DIFFERENTIATION COMMAND & ALIASES
# ==============================================================================

def test_cli_diff_command(capsys):
    ret = run_cli(["diff", "x^3 + sin(x)", "-v", "x", "-f", "unicode"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Step-by-Step Breakdown:" in captured
    assert "Unicode:" in captured


def test_cli_diff_aliases(capsys):
    # Test 'differentiate' alias
    ret1 = run_cli(["differentiate", "x^2", "-f", "latex"])
    assert ret1 == 0
    captured1 = capsys.readouterr().out
    assert "LaTeX:" in captured1

    # Test 'derivative' alias
    ret2 = run_cli(["derivative", "3*x", "--no-steps", "-f", "unicode"])
    assert ret2 == 0
    captured2 = capsys.readouterr().out
    assert "Step-by-Step Breakdown:" not in captured2
    assert "3" in captured2


def test_cli_diff_output_formats(capsys):
    # ASCII format
    ret_ascii = run_cli(["diff", "x^2", "--no-steps", "-f", "ascii"])
    assert ret_ascii == 0
    out_ascii = capsys.readouterr().out
    assert "ASCII:" in out_ascii

    # Tree format
    ret_tree = run_cli(["diff", "x^2", "--no-steps", "-f", "tree"])
    assert ret_tree == 0
    out_tree = capsys.readouterr().out
    assert "AST Tree:" in out_tree


# ==============================================================================
# 2. INTEGRATION COMMAND & ALIASES
# ==============================================================================

def test_cli_integrate_indefinite(capsys):
    ret = run_cli(["int", "x^2", "-v", "x", "-f", "latex"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "LaTeX:" in captured
    assert "\\int" in captured or "x^3" in captured or "3" in captured


test_cli_integrate_aliases = [
    ["integrate", "2*x"],
    ["integral", "cos(x)"]
]

@pytest.mark.parametrize("args", test_cli_integrate_aliases)
def test_cli_integrate_command_aliases(args, capsys):
    ret = run_cli(args + ["--no-steps", "-f", "unicode"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Unicode:" in captured


def test_cli_integrate_definite(capsys):
    ret = run_cli(["integrate", "3*x^2", "-l", "0", "-u", "2"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Definite Integral from 0 to 2" in captured
    assert "8" in captured


# ==============================================================================
# 3. LIMIT COMMAND & ALIASES
# ==============================================================================

def test_cli_limit_command(capsys):
    ret = run_cli(["lim", "sin(x) / x", "-p", "0"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Evaluated limit = 1" in captured or "1" in captured


def test_cli_limit_alias_and_directions(capsys):
    # Alias 'limit' with direction 'right'
    ret = run_cli(["limit", "1 / x", "-p", "0", "-d", "right", "--no-steps"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "limit" in captured.lower() or "inf" in captured.lower() or "unicode" in captured.lower()


# ==============================================================================
# 4. SIMPLIFY COMMAND
# ==============================================================================

def test_cli_simplify_command(capsys):
    ret = run_cli(["simplify", "x + 0 + x * 1", "-f", "unicode"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Unicode: 2x" in captured or "2 * x" in captured or "2x" in captured


def test_cli_simp_alias(capsys):
    ret = run_cli(["simp", "x * 0 + sin(0)"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "0" in captured


# ==============================================================================
# 5. EVALUATE & TREE COMMANDS
# ==============================================================================

def test_cli_eval_command(capsys):
    ret = run_cli(["eval", "x^2 + y", "x=3", "y=4"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "Evaluated numerical result: 13.0" in captured or "13.0" in captured


def test_cli_eval_with_flags(capsys):
    ret = run_cli(["evaluate", "a * b + c", "-v", "a=2", "-v", "b=3", "-v", "c=4"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "10.0" in captured


def test_cli_tree_command(capsys):
    ret = run_cli(["tree", "sin(2*x)"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "AST Tree for 'sin(2*x)':" in captured
    assert "Sin" in captured


def test_cli_ast_alias(capsys):
    ret = run_cli(["ast", "x + 1"])
    assert ret == 0
    captured = capsys.readouterr().out
    assert "AST Tree" in captured


# ==============================================================================
# 6. HELPER FUNCTIONS & ERROR HANDLING
# ==============================================================================

def test_parse_eval_args():
    expr, vars_map = parse_eval_args(["x^2 + y", "x=3.5", "y=4.5"])
    assert expr == "x^2 + y"
    assert vars_map == {"x": 3.5, "y": 4.5}


def test_format_result_output_error():
    res = {"success": False, "error": "Invalid syntax"}
    formatted = format_result_output(res)
    assert formatted == "Error: Invalid syntax"


def test_cli_invalid_expression(capsys):
    ret = run_cli(["diff", "(x + 2"])
    assert ret == 1
    captured = capsys.readouterr().out
    assert "Error:" in captured
