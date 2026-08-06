import sys
from parser import parse_expr
from math_ast import *

def test_expr(expr_str, env=None):
    if env is None:
        env = {'x': 2.0}
    print(f"--- Testing: {expr_str} ---")
    try:
        ast = parse_expr(expr_str)
        print("AST:", ast)
    except Exception as e:
        print("Parse Error:", e)
        return

    try:
        simp = ast.simplify()
        print("Simplified:", simp)
    except Exception as e:
        print("Simplify Error:", type(e).__name__, e)
    
    try:
        diff = ast.differentiate('x')
        print("Diff(x):", diff)
        diff_simp = diff.simplify()
        print("Diff(x) simplified:", diff_simp)
        diff_val = diff.evaluate(env)
        print("Diff Eval:", diff_val)
    except Exception as e:
        print("Diff Error:", type(e).__name__, e)

    try:
        val = ast.evaluate(env)
        print(f"Eval(env={env}):", val)
    except Exception as e:
        print("Eval Error:", type(e).__name__, e)

test_expr("0 / 0")
test_expr("x / 0")
test_expr("0 ^ -1")
test_expr("(-1) ^ 0.5")
test_expr("x ^ x")
test_expr("--x")
test_expr("sin(x) / cos(x)")
test_expr("1 / (x - x)", {'x': 5})
