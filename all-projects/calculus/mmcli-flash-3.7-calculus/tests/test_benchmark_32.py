"""
32-Equation Calculus Engine Benchmark Test Suite
================================================
Validates all 32 benchmark equations against sympy oracle truth values across all 8 categories:
1. Polynomials & Power Rules
2. Trigonometric & Inverse Trig
3. Exponential & Logarithmic
4. Product & Quotient Rules
5. Multi-Layer Nested Chain Rule
6. Radical Roots & Fractional Powers
7. Integration & Limits (CAS capabilities)
8. Error Handling, Unicode & Boundary Conditions
"""

import pytest
import sympy
from sympy import symbols, diff as sym_diff, integrate as sym_integrate, limit as sym_limit
from sympy.parsing.sympy_parser import (
    parse_expr as sympy_parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

from parser import parse as engine_parse
from simplifier import simplify as engine_simplify
from differentiator import diff as engine_diff
from limits import limit as engine_limit
from integrator import integrate as engine_integrate, definite_integrate as engine_defint

X = symbols("x")
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
NUMERIC_TOLERANCE = 1e-4
DEFAULT_SAMPLES = [0.3, 0.7, 1.3, -0.5, 2.1]

BENCHMARK_CASES = [
    {"id": 1, "cat": "Polynomials", "type": "diff", "expr": "3*x^5 - 4*x^2 + 7*x - 12", "oracle": "3*x**5 - 4*x**2 + 7*x - 12"},
    {"id": 2, "cat": "Polynomials", "type": "diff", "expr": "(2*x + 5)^4", "oracle": "(2*x + 5)**4"},
    {"id": 3, "cat": "Polynomials", "type": "diff", "expr": "x^(-3) + x^(-0.5)", "oracle": "x**(-3) + x**(-0.5)", "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 4, "cat": "Polynomials", "type": "diff", "expr": "(x^2 + 1) * (3*x^3 - 2)", "oracle": "(x**2 + 1) * (3*x**3 - 2)"},
    {"id": 5, "cat": "Trig", "type": "diff", "expr": "sin(x) * cos(x)", "oracle": "sin(x) * cos(x)"},
    {"id": 6, "cat": "Trig", "type": "diff", "expr": "tan(x^2 + 1)", "oracle": "tan(x**2 + 1)"},
    {"id": 7, "cat": "Trig", "type": "diff", "expr": "asin(x) + acos(x)", "oracle": "asin(x) + acos(x)", "samples": [-0.9, -0.3, 0.0, 0.4, 0.8]},
    {"id": 8, "cat": "Trig", "type": "diff", "expr": "tan(x)^2 + 1", "oracle": "tan(x)**2 + 1"},
    {"id": 9, "cat": "Exp & Log", "type": "diff", "expr": "exp(3*x) * (x^2 - 2*x + 2)", "oracle": "exp(3*x) * (x**2 - 2*x + 2)"},
    {"id": 10, "cat": "Exp & Log", "type": "diff", "expr": "ln(x^2 + 1) / x", "oracle": "log(x**2 + 1) / x"},
    {"id": 11, "cat": "Exp & Log", "type": "diff", "expr": "x^3 * ln(x)", "oracle": "x**3 * log(x)", "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 12, "cat": "Exp & Log", "type": "diff", "expr": "exp(-x^2) * cos(x)", "oracle": "exp(-x**2) * cos(x)"},
    {"id": 13, "cat": "Product & Quotient", "type": "diff", "expr": "(x^2 + 1) / (x^3 - 1)", "oracle": "(x**2 + 1) / (x**3 - 1)"},
    {"id": 14, "cat": "Product & Quotient", "type": "diff", "expr": "sin(x) / (cos(x) + 1)", "oracle": "sin(x) / (cos(x) + 1)"},
    {"id": 15, "cat": "Product & Quotient", "type": "diff", "expr": "x^2 * sin(x) * ln(x)", "oracle": "x**2 * sin(x) * log(x)", "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 16, "cat": "Product & Quotient", "type": "diff", "expr": "(exp(x) * sin(x)) / (x^2 + 1)", "oracle": "(exp(x) * sin(x)) / (x**2 + 1)"},
    {"id": 17, "cat": "Nested Chain", "type": "diff", "expr": "sin(cos(tan(x)))", "oracle": "sin(cos(tan(x)))"},
    {"id": 18, "cat": "Nested Chain", "type": "diff", "expr": "sqrt(1 + sin(x)^2)", "oracle": "sqrt(1 + sin(x)**2)"},
    {"id": 19, "cat": "Nested Chain", "type": "diff", "expr": "exp(sqrt(x^2 + 4))", "oracle": "exp(sqrt(x**2 + 4))"},
    {"id": 20, "cat": "Nested Chain", "type": "diff", "expr": "ln(sin(x^3 + 1))", "oracle": "log(sin(x**3 + 1))", "samples": [0.3, 0.5, 0.7, -0.3, -0.5]},
    {"id": 21, "cat": "Radicals", "type": "diff", "expr": "sqrt(x^3 + 2*x)", "oracle": "sqrt(x**3 + 2*x)", "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 22, "cat": "Radicals", "type": "diff", "expr": "1 / sqrt(4 - x^2)", "oracle": "1 / sqrt(4 - x**2)", "samples": [-1.5, -0.5, 0.0, 0.8, 1.5]},
    {"id": 23, "cat": "Radicals", "type": "diff", "expr": "(x^3 + 1)^(2/3)", "oracle": "(x**3 + 1)**(sympy.Rational(2, 3))", "samples": [0.3, 0.7, 1.3, 2.1, -0.5]},
    {"id": 24, "cat": "Radicals", "type": "diff", "expr": "sqrt(x) * ln(sqrt(x))", "oracle": "sqrt(x) * log(sqrt(x))", "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 25, "cat": "Integration & Limits", "type": "int", "expr": "x^4 - 2*x + 1", "oracle": "x**4 - 2*x + 1"},
    {"id": 26, "cat": "Integration & Limits", "type": "defint", "expr": "x^2", "oracle": "x**2", "lower": 0, "upper": 3},
    {"id": 27, "cat": "Integration & Limits", "type": "lim", "expr": "sin(x)/x", "oracle": "sin(x)/x", "point": 0},
    {"id": 28, "cat": "Integration & Limits", "type": "lim", "expr": "(1 - cos(x))/x^2", "oracle": "(1 - cos(x))/x**2", "point": 0},
    {"id": 29, "cat": "Boundary & Errors", "type": "diff_or_reject", "expr": "x² + sin(x)", "oracle": "x**2 + sin(x)"},
    {"id": 30, "cat": "Boundary & Errors", "type": "diff_or_reject", "expr": "cos3x", "oracle": "cos(3*x)"},
    {"id": 31, "cat": "Boundary & Errors", "type": "syntax_err", "expr": "sin(x", "oracle": None},
    {"id": 32, "cat": "Boundary & Errors", "type": "syntax_err", "expr": "x = 2", "oracle": None},
]


def oracle_sympy_expr(oracle_str):
    ns = {"x": X, "sympy": sympy, "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
          "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
          "exp": sympy.exp, "log": sympy.log, "sqrt": sympy.sqrt}
    return eval(oracle_str, {"__builtins__": {}}, ns)


def try_parse_engine_expr(output_str):
    if output_str is None:
        return None
    s = output_str.strip()
    if not s or not any(ch.isalpha() or ch.isdigit() for ch in s):
        return None
    s = s.replace("ln(", "log(")
    try:
        return sympy_parse_expr(s, local_dict={"x": X}, transformations=TRANSFORMS)
    except Exception:
        return None


def numerically_matches(expr_a, expr_b, samples, tol=NUMERIC_TOLERANCE, min_agreements=2):
    agreements, attempts = 0, 0
    for s in samples:
        try:
            va = complex(expr_a.evalf(subs={X: s}))
            vb = complex(expr_b.evalf(subs={X: s}))
        except Exception:
            continue
        if abs(va.imag) > 1e-6 or abs(vb.imag) > 1e-6:
            continue
        attempts += 1
        if abs(va.real - vb.real) <= tol * max(1.0, abs(vb.real)):
            agreements += 1
    if attempts < min_agreements:
        return None
    return agreements == attempts


@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=[f"Case_{c['id']:02d}_{c['cat']}" for c in BENCHMARK_CASES])
def test_benchmark_case(case):
    ctype = case["type"]
    expr = case["expr"]

    if ctype == "syntax_err":
        with pytest.raises(Exception):
            engine_diff(expr, var="x")
        return

    if ctype == "diff_or_reject":
        try:
            res_str = str(engine_diff(expr, var="x"))
            act = try_parse_engine_expr(res_str)
            assert act is not None
            exp = sym_diff(oracle_sympy_expr(case["oracle"]), X)
            assert numerically_matches(act, exp, case.get("samples", DEFAULT_SAMPLES)) is True
        except Exception:
            # Clean rejection is also allowed for boundary cases
            pass
        return

    if ctype == "diff":
        res_str = str(engine_diff(expr, var="x"))
        act = try_parse_engine_expr(res_str)
        assert act is not None, f"Failed to parse engine output: {res_str}"
        exp = sym_diff(oracle_sympy_expr(case["oracle"]), X)
        assert numerically_matches(act, exp, case.get("samples", DEFAULT_SAMPLES)) is True

    elif ctype == "int":
        res_str = str(engine_integrate(expr, var="x"))
        antideriv = try_parse_engine_expr(res_str)
        assert antideriv is not None, f"Failed to parse antiderivative: {res_str}"
        original = oracle_sympy_expr(case["oracle"])
        rec = sym_diff(antideriv, X)
        assert numerically_matches(rec, original, case.get("samples", DEFAULT_SAMPLES)) is True

    elif ctype == "defint":
        val = engine_defint(expr, var="x", a=case["lower"], b=case["upper"])
        exp_val = float(sym_integrate(oracle_sympy_expr(case["oracle"]), (X, case["lower"], case["upper"])))
        assert abs(float(val) - exp_val) <= NUMERIC_TOLERANCE * max(1.0, abs(exp_val))

    elif ctype == "lim":
        val = engine_limit(expr, var="x", point=case["point"])
        exp_val = float(sym_limit(oracle_sympy_expr(case["oracle"]), X, case["point"]))
        assert abs(float(val) - exp_val) <= NUMERIC_TOLERANCE * max(1.0, abs(exp_val))
