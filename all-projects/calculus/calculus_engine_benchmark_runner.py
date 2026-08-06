"""
32-Equation Calculus Engine Benchmark Runner
=============================================

Run Full Benchmark (All Engines, saves to oracle_graded):
    python3 main.py --benchmark

Run Individual Benchmarks (saves to multi_test):
    python3 main.py -p ag-flash --benchmark
    python3 main.py -p pro --benchmark
    python3 main.py -p opus --benchmark
    python3 main.py -p flash --benchmark
    python3 main.py -p lite --benchmark

Key differences from the earlier version:
  1. Every diff/int/defint/lim case is graded against a real expected value,
     computed independently by sympy (the "oracle") -- not just "did it run
     without raising."
  2. Engine subprocesses do ONE job: attempt the computation and report back
     either a raw output string or an error. All grading/classification
     happens in the parent process, through ONE shared function
     (`grade_case`) applied identically to all five engines. No engine gets
     a bespoke try/except that changes what counts as a pass.
  3. Boundary-condition cases (Unicode input, bare function names, syntax
     errors) are graded with the same rubric for everyone:
        - Raises a clean exception               -> PASS  (clean rejection)
        - Returns a result matching the oracle    -> PASS  (correctly handled)
        - Returns a result NOT matching the oracle -> FAIL (silent wrong answer)
     "Silently returns something" is never a pass by default -- it only
     passes if that something is actually correct.
  4. If an engine's output can't be parsed back into a comparable symbolic
     form, that's reported as UNVERIFIABLE, not folded into PASS or FAIL --
     so format quirks don't silently inflate or deflate a score.
"""

import subprocess
import sys
import json
import time
from pathlib import Path

import sympy
from sympy import symbols, sympify, diff as sym_diff, integrate as sym_integrate, limit as sym_limit
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

REPO_ROOT = "/Users/danielward/Developer/Personal Projects/Machine Learning-AI/python-practice"
SUBPROCESS_TIMEOUT_SEC = 20
NUMERIC_TOLERANCE = 1e-4
DEFAULT_SAMPLES = [0.3, 0.7, 1.3, -0.5, 2.1]

X = symbols("x")
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)

# ---------------------------------------------------------------------------
# Test cases: engine-facing expression string + a sympy-facing oracle string
# + (optionally) a restricted sample domain to avoid singularities/undefined
# regions for that specific expression.
# ---------------------------------------------------------------------------

test_cases = [
    # Category 1: Polynomials & Power Rules
    {"id": 1, "cat": "Polynomials", "type": "diff",
     "expr": "3*x^5 - 4*x^2 + 7*x - 12", "oracle": "3*x**5 - 4*x**2 + 7*x - 12"},
    {"id": 2, "cat": "Polynomials", "type": "diff",
     "expr": "(2*x + 5)^4", "oracle": "(2*x + 5)**4"},
    {"id": 3, "cat": "Polynomials", "type": "diff",
     "expr": "x^(-3) + x^(-0.5)", "oracle": "x**(-3) + x**(-0.5)",
     "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 4, "cat": "Polynomials", "type": "diff",
     "expr": "(x^2 + 1) * (3*x^3 - 2)", "oracle": "(x**2 + 1) * (3*x**3 - 2)"},

    # Category 2: Trigonometric & Inverse Trig
    {"id": 5, "cat": "Trig", "type": "diff",
     "expr": "sin(x) * cos(x)", "oracle": "sin(x) * cos(x)"},
    {"id": 6, "cat": "Trig", "type": "diff",
     "expr": "tan(x^2 + 1)", "oracle": "tan(x**2 + 1)"},
    {"id": 7, "cat": "Trig", "type": "diff",
     "expr": "asin(x) + acos(x)", "oracle": "asin(x) + acos(x)",
     "samples": [-0.9, -0.3, 0.0, 0.4, 0.8]},
    {"id": 8, "cat": "Trig", "type": "diff",
     "expr": "tan(x)^2 + 1", "oracle": "tan(x)**2 + 1"},

    # Category 3: Exponential & Logarithmic
    {"id": 9, "cat": "Exp & Log", "type": "diff",
     "expr": "exp(3*x) * (x^2 - 2*x + 2)", "oracle": "exp(3*x) * (x**2 - 2*x + 2)"},
    {"id": 10, "cat": "Exp & Log", "type": "diff",
     "expr": "ln(x^2 + 1) / x", "oracle": "log(x**2 + 1) / x"},
    {"id": 11, "cat": "Exp & Log", "type": "diff",
     "expr": "x^3 * ln(x)", "oracle": "x**3 * log(x)",
     "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 12, "cat": "Exp & Log", "type": "diff",
     "expr": "exp(-x^2) * cos(x)", "oracle": "exp(-x**2) * cos(x)"},

    # Category 4: Product & Quotient Rules
    {"id": 13, "cat": "Product & Quotient", "type": "diff",
     "expr": "(x^2 + 1) / (x^3 - 1)", "oracle": "(x**2 + 1) / (x**3 - 1)"},
    {"id": 14, "cat": "Product & Quotient", "type": "diff",
     "expr": "sin(x) / (cos(x) + 1)", "oracle": "sin(x) / (cos(x) + 1)"},
    {"id": 15, "cat": "Product & Quotient", "type": "diff",
     "expr": "x^2 * sin(x) * ln(x)", "oracle": "x**2 * sin(x) * log(x)",
     "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 16, "cat": "Product & Quotient", "type": "diff",
     "expr": "(exp(x) * sin(x)) / (x^2 + 1)", "oracle": "(exp(x) * sin(x)) / (x**2 + 1)"},

    # Category 5: Multi-Layer Nested Chain Rule
    {"id": 17, "cat": "Nested Chain", "type": "diff",
     "expr": "sin(cos(tan(x)))", "oracle": "sin(cos(tan(x)))"},
    {"id": 18, "cat": "Nested Chain", "type": "diff",
     "expr": "sqrt(1 + sin(x)^2)", "oracle": "sqrt(1 + sin(x)**2)"},
    {"id": 19, "cat": "Nested Chain", "type": "diff",
     "expr": "exp(sqrt(x^2 + 4))", "oracle": "exp(sqrt(x**2 + 4))"},
    {"id": 20, "cat": "Nested Chain", "type": "diff",
     "expr": "ln(sin(x^3 + 1))", "oracle": "log(sin(x**3 + 1))",
     "samples": [0.3, 0.5, 0.7, -0.3, -0.5]},

    # Category 6: Radical Roots & Fractional Powers
    {"id": 21, "cat": "Radicals", "type": "diff",
     "expr": "sqrt(x^3 + 2*x)", "oracle": "sqrt(x**3 + 2*x)",
     "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},
    {"id": 22, "cat": "Radicals", "type": "diff",
     "expr": "1 / sqrt(4 - x^2)", "oracle": "1 / sqrt(4 - x**2)",
     "samples": [-1.5, -0.5, 0.0, 0.8, 1.5]},
    {"id": 23, "cat": "Radicals", "type": "diff",
     "expr": "(x^3 + 1)^(2/3)", "oracle": "(x**3 + 1)**(sympy.Rational(2, 3))",
     "samples": [0.3, 0.7, 1.3, 2.1, -0.5]},
    {"id": 24, "cat": "Radicals", "type": "diff",
     "expr": "sqrt(x) * ln(sqrt(x))", "oracle": "sqrt(x) * log(sqrt(x))",
     "samples": [0.3, 0.7, 1.3, 2.1, 3.5]},

    # Category 7: Integration & Limits (CAS capabilities)
    {"id": 25, "cat": "Integration & Limits", "type": "int",
     "expr": "x^4 - 2*x + 1", "oracle": "x**4 - 2*x + 1"},
    {"id": 26, "cat": "Integration & Limits", "type": "defint",
     "expr": "x^2", "oracle": "x**2", "lower": 0, "upper": 3},
    {"id": 27, "cat": "Integration & Limits", "type": "lim",
     "expr": "sin(x)/x", "oracle": "sin(x)/x", "point": 0},
    {"id": 28, "cat": "Integration & Limits", "type": "lim",
     "expr": "(1 - cos(x))/x^2", "oracle": "(1 - cos(x))/x**2", "point": 0},

    # Category 8: Error Handling, Unicode & Boundary Conditions
    {"id": 29, "cat": "Boundary & Errors", "type": "diff_or_reject",
     "expr": "x\u00b2 + sin(x)", "oracle": "x**2 + sin(x)"},
    {"id": 30, "cat": "Boundary & Errors", "type": "diff_or_reject",
     "expr": "cos3x", "oracle": "cos(3*x)"},
    {"id": 31, "cat": "Boundary & Errors", "type": "syntax_err",
     "expr": "sin(x", "oracle": None},
    {"id": 32, "cat": "Boundary & Errors", "type": "syntax_err",
     "expr": "x = 2", "oracle": None},
]

# ---------------------------------------------------------------------------
# Oracle: ground-truth values, computed once via sympy, independent of any
# engine under test.
# ---------------------------------------------------------------------------

def oracle_sympy_expr(oracle_str):
    """Parse a case's oracle string (already in sympy/python syntax) into a
    sympy expression. Uses eval() only against a controlled sympy namespace
    since these strings are authored by us, not by engine output."""
    ns = {"x": X, "sympy": sympy, "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
          "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
          "exp": sympy.exp, "log": sympy.log, "sqrt": sympy.sqrt}
    return eval(oracle_str, {"__builtins__": {}}, ns)


def oracle_derivative(case):
    return sym_diff(oracle_sympy_expr(case["oracle"]), X)


def oracle_definite_integral(case):
    return float(sym_integrate(oracle_sympy_expr(case["oracle"]), (X, case["lower"], case["upper"])))


def oracle_limit(case):
    return float(sym_limit(oracle_sympy_expr(case["oracle"]), X, case["point"]))


# ---------------------------------------------------------------------------
# Parsing engine output back into something comparable
# ---------------------------------------------------------------------------

def try_parse_engine_expr(output_str):
    """Best-effort parse of an engine's stringified symbolic result into a
    sympy expression. Returns None (not an exception) if it can't be parsed,
    so callers can route to UNVERIFIABLE instead of guessing PASS/FAIL."""
    if output_str is None:
        return None
    s = output_str.strip()
    if not s or not any(ch.isalpha() or ch.isdigit() for ch in s):
        return None
    s = s.replace("ln(", "log(")
    try:
        expr = parse_expr(s, local_dict={"x": X}, transformations=TRANSFORMS)
        return expr
    except Exception:
        return None


def numerically_matches(expr_a, expr_b, samples, tol=NUMERIC_TOLERANCE, min_agreements=2):
    """Compares two sympy expressions by numeric evaluation at several sample
    points, skipping points where either side is undefined/complex. Requires
    at least `min_agreements` valid, matching sample points to call it a
    match -- if fewer than that could even be evaluated, result is None
    (inconclusive / domain issue), not a silent pass."""
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


# ---------------------------------------------------------------------------
# Unified grading -- the SAME function is applied to every engine's result
# for a given case. No engine gets special-cased logic here.
# ---------------------------------------------------------------------------

def grade_case(case, raw_output, error):
    ctype = case["type"]

    if ctype == "syntax_err":
        return ("PASS", "Clean syntax error raised") if error else \
               ("FAIL", "Did not reject invalid syntax")

    if ctype == "diff_or_reject":
        # Boundary cases: rejecting cleanly OR computing the right answer
        # both count as a pass. Computing a wrong answer without raising
        # is the one outcome that fails -- that's the silent-failure mode.
        if error:
            return "PASS", f"Clean rejection: {error}"
        actual = try_parse_engine_expr(raw_output)
        if actual is None:
            return "FAIL", f"Corrupt or unparseable output string: {raw_output!r}"
        expected = oracle_derivative(case)
        match = numerically_matches(actual, expected, case.get("samples", DEFAULT_SAMPLES))
        if match is None:
            return "UNVERIFIABLE", "Domain issues prevented numeric comparison"
        return ("PASS", "Correctly parsed and differentiated") if match else \
               ("FAIL", f"Silent wrong answer (no error raised): {raw_output!r}")

    if error:
        return "FAIL", f"Raised unexpectedly: {error}"

    if ctype == "diff":
        actual = try_parse_engine_expr(raw_output)
        if actual is None:
            return "FAIL", f"Corrupt or unparseable output string: {raw_output!r}"
        expected = oracle_derivative(case)
        match = numerically_matches(actual, expected, case.get("samples", DEFAULT_SAMPLES))
        if match is None:
            return "UNVERIFIABLE", "Domain issues prevented numeric comparison"
        return ("PASS", "Matches oracle derivative") if match else \
               ("FAIL", f"Does not match oracle derivative: {raw_output!r}")

    if ctype == "int":
        # Grade by differentiating the engine's antiderivative and comparing
        # to the ORIGINAL function -- sidesteps "+C" and formatting mismatches.
        antideriv = try_parse_engine_expr(raw_output)
        if antideriv is None:
            return "UNVERIFIABLE", f"Could not parse antiderivative output: {raw_output!r}"
        original = oracle_sympy_expr(case["oracle"])
        recovered_derivative = sym_diff(antideriv, X)
        match = numerically_matches(recovered_derivative, original, case.get("samples", DEFAULT_SAMPLES))
        if match is None:
            return "UNVERIFIABLE", "Domain issues prevented numeric comparison"
        return ("PASS", "Antiderivative differentiates back to the original") if match else \
               ("FAIL", f"Antiderivative is wrong: {raw_output!r}")

    if ctype == "defint":
        try:
            actual_val = float(raw_output)
        except (TypeError, ValueError):
            return "UNVERIFIABLE", f"Output is not a parseable number: {raw_output!r}"
        expected_val = oracle_definite_integral(case)
        match = abs(actual_val - expected_val) <= NUMERIC_TOLERANCE * max(1.0, abs(expected_val))
        return ("PASS", f"{actual_val} ~= {expected_val}") if match else \
               ("FAIL", f"{actual_val} != expected {expected_val}")

    if ctype == "lim":
        try:
            actual_val = float(raw_output)
        except (TypeError, ValueError):
            return "UNVERIFIABLE", f"Output is not a parseable number: {raw_output!r}"
        expected_val = oracle_limit(case)
        match = abs(actual_val - expected_val) <= NUMERIC_TOLERANCE * max(1.0, abs(expected_val))
        return ("PASS", f"{actual_val} ~= {expected_val}") if match else \
               ("FAIL", f"{actual_val} != expected {expected_val}")

    return "UNVERIFIABLE", f"Unhandled case type: {ctype}"


# ---------------------------------------------------------------------------
# Engine adapters -- ONLY responsible for producing a raw output string or
# raising. They do NOT decide pass/fail; grade_case() does that, uniformly.
# ---------------------------------------------------------------------------

ENGINE_ADAPTER_TEMPLATE = r"""
import sys, json
from pathlib import Path
p = Path({project_path!r}).resolve()
sys.path.insert(0, str(p))

{import_block}

cases = json.loads({cases_json!r})
results = []

for c in cases:
    cid, ctype, expr_str = c["id"], c["type"], c["expr"]
    entry = {{"id": cid}}
    try:
        if ctype in ("diff", "diff_or_reject"):
            entry["output"] = str(DIFF_FN(expr_str))
        elif ctype == "int":
            entry["output"] = str(INT_FN(expr_str))
        elif ctype == "defint":
            entry["output"] = str(DEFINT_FN(expr_str, c["lower"], c["upper"]))
        elif ctype == "lim":
            entry["output"] = str(LIM_FN(expr_str, c["point"]))
        elif ctype == "syntax_err":
            entry["output"] = str(DIFF_FN(expr_str))
        entry["error"] = None
    except Exception as e:
        entry["output"] = None
        entry["error"] = f"{{type(e).__name__}}: {{e}}"
    results.append(entry)

print(json.dumps(results))
"""

# NOTE: the DIFF_FN / INT_FN / DEFINT_FN / LIM_FN wiring below is per-engine
# because each project exposes a different API surface -- that's unavoidable
# glue code, not grading logic. If an engine doesn't implement int/defint/lim,
# its adapter should raise NotImplementedError, which grade_case() will
# correctly score as FAIL for those specific cases (it's in scope for the
# benchmark even if the engine's author chose not to build it -- see the
# reporting note at the bottom about scope-adjusted scoring).

projects = [
    {
        "name": "mmcli-flash-calculus",
        "title": "mmcli-flash (Gemini 3.6 Flash Full CAS)",
        "project_path": "all-projects/calculus/mmcli-flash-calculus",
        "import_block": """
import importlib.util
spec = importlib.util.spec_from_file_location("calculus", p / "__init__.py", submodule_search_locations=[str(p)])
mod = importlib.util.module_from_spec(spec)
sys.modules["calculus"] = mod
spec.loader.exec_module(mod)

from calculus.parser import parse
from calculus.diff import diff as _diff
from calculus.integrate import integrate as _integrate
from calculus.limits import limit as _limit
from calculus.simplify import simplify as _simplify

def DIFF_FN(s):
    return _simplify(_diff(parse(s), var="x"))

def INT_FN(s):
    return _integrate(parse(s), "x")

def DEFINT_FN(s, lo, hi):
    return _integrate(parse(s), "x", lower=lo, upper=hi)

def LIM_FN(s, point):
    return _limit(parse(s), "x", point)
""",
    },
    {
        "name": "mmcli-flash-lite-calculus",
        "title": "mmcli-flash-lite (Gemini 3.5 Flash-Lite)",
        "project_path": "all-projects/calculus/mmcli-flash-lite-calculus",
        "import_block": """
import importlib.util
spec = importlib.util.spec_from_file_location("calculus", p / "__init__.py", submodule_search_locations=[str(p)])
mod = importlib.util.module_from_spec(spec)
sys.modules["calculus"] = mod
spec.loader.exec_module(mod)

from calculus.parser import parse_expression
from calculus.engine import differentiate, simplify
from calculus.tui import evaluate_expression

def DIFF_FN(s):
    return simplify(differentiate(parse_expression(s), var="x"))

def INT_FN(s):
    raise NotImplementedError("flash-lite only offers a numeric preview, not a symbolic antiderivative")

def DEFINT_FN(s, lo, hi):
    ast = parse_expression(s)
    n = 200
    h = (hi - lo) / n
    total = evaluate_expression(ast, {"x": lo}) + evaluate_expression(ast, {"x": hi})
    for i in range(1, n):
        xv = lo + i * h
        total += (4 if i % 2 else 2) * evaluate_expression(ast, {"x": xv})
    return total * (h / 3)

def LIM_FN(s, point):
    ast = parse_expression(s)
    eps = 1e-6
    vl = evaluate_expression(ast, {"x": point - eps})
    vr = evaluate_expression(ast, {"x": point + eps})
    return (vl + vr) / 2
""",
    },
    {
        "name": "antigravity-flash-calculus",
        "title": "antigravity-flash (Gemini 3.6 Flash)",
        "project_path": "all-projects/calculus/antigravity-flash-calculus",
        "import_block": """
from core.parser import parse_expression
from core.differentiator import differentiate_with_steps

def DIFF_FN(s):
    _, simp_d, _ = differentiate_with_steps(parse_expression(s), var="x")
    return simp_d

def INT_FN(s):
    raise NotImplementedError("not implemented in this build")

def DEFINT_FN(s, lo, hi):
    raise NotImplementedError("not implemented in this build")

def LIM_FN(s, point):
    raise NotImplementedError("not implemented in this build")
""",
    },
    {
        "name": "antigravity-opus-calculus",
        "title": "antigravity-opus (Claude Opus 4.6)",
        "project_path": "all-projects/calculus/antigravity-opus-calculus",
        "import_block": """
from parser import parse

def DIFF_FN(s):
    return parse(s).differentiate("x").deep_simplify()

def INT_FN(s):
    raise NotImplementedError("not implemented in this build")

def DEFINT_FN(s, lo, hi):
    raise NotImplementedError("not implemented in this build")

def LIM_FN(s, point):
    raise NotImplementedError("not implemented in this build")
""",
    },
    {
        "name": "antigravity-gemini-pro-calculus",
        "title": "antigravity-gemini-pro (Gemini 3.1 Pro)",
        "project_path": "all-projects/calculus/antigravity-gemini-pro-calculus",
        "import_block": """
from parser import Parser

def DIFF_FN(s):
    return Parser(s).parse().differentiate("x").simplify()

def INT_FN(s):
    raise NotImplementedError("not implemented in this build")

def DEFINT_FN(s, lo, hi):
    raise NotImplementedError("not implemented in this build")

def LIM_FN(s, point):
    raise NotImplementedError("not implemented in this build")
""",
    },
]


def run_engine(proj, cases_json):
    script = ENGINE_ADAPTER_TEMPLATE.format(
        project_path=proj["project_path"],
        import_block=proj["import_block"],
        cases_json=cases_json,
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return None, f"Timed out after {SUBPROCESS_TIMEOUT_SEC}s"

    out = proc.stdout.strip()
    if not out.startswith("["):
        return None, proc.stderr.strip() or "No JSON output produced"
    return json.loads(out), None


ALIAS_MAP = {
    "flash": "mmcli-flash-calculus",
    "mmcli-flash": "mmcli-flash-calculus",
    "mmcli-flash-calculus": "mmcli-flash-calculus",
    "lite": "mmcli-flash-lite-calculus",
    "flash-lite": "mmcli-flash-lite-calculus",
    "mmcli-flash-lite": "mmcli-flash-lite-calculus",
    "mmcli-flash-lite-calculus": "mmcli-flash-lite-calculus",
    "ag-flash": "antigravity-flash-calculus",
    "antigravity-flash": "antigravity-flash-calculus",
    "antigravity-flash-calculus": "antigravity-flash-calculus",
    "opus": "antigravity-opus-calculus",
    "antigravity-opus": "antigravity-opus-calculus",
    "antigravity-opus-calculus": "antigravity-opus-calculus",
    "pro": "antigravity-gemini-pro-calculus",
    "antigravity-pro": "antigravity-gemini-pro-calculus",
    "antigravity-gemini-pro": "antigravity-gemini-pro-calculus",
    "antigravity-gemini-pro-calculus": "antigravity-gemini-pro-calculus",
}


def main():
    target_engine_name = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--project", "-p", "--engine", "-e"):
            if i + 1 < len(args):
                target_engine_name = ALIAS_MAP.get(args[i + 1].lower(), args[i + 1])
                i += 2
                continue
        elif arg.startswith("--project=") or arg.startswith("-p=") or arg.startswith("--engine=") or arg.startswith("-e="):
            val = arg.split("=", 1)[1]
            target_engine_name = ALIAS_MAP.get(val.lower(), val)
            i += 1
            continue
        elif arg.lower() in ALIAS_MAP:
            target_engine_name = ALIAS_MAP[arg.lower()]
            i += 1
            continue
        i += 1

    run_projects = projects
    if target_engine_name:
        run_projects = [p for p in projects if p["name"] == target_engine_name]
        if not run_projects:
            print(f"Error: Unknown engine '{target_engine_name}'. Available aliases: {list(ALIAS_MAP.keys())}", file=sys.stderr)
            sys.exit(1)

    cases_by_id = {c["id"]: c for c in test_cases}
    cases_json = json.dumps(test_cases)

    all_graded = {}

    print("=" * 88)
    print("        32-EQUATION BENCHMARK -- ORACLE-VERIFIED, UNIFIED GRADING")
    print("=" * 88)

    for proj in run_projects:
        print(f"\n>>> {proj['title']}")
        start = time.time()
        raw_results, run_error = run_engine(proj, cases_json)
        elapsed = time.time() - start

        graded = []
        if raw_results is None:
            print(f"    [RUNNER ERROR] {run_error}")
            for c in test_cases:
                graded.append({"id": c["id"], "status": "FAIL", "reason": f"Runner error: {run_error}"})
        else:
            for r in raw_results:
                case = cases_by_id[r["id"]]
                status, reason = grade_case(case, r.get("output"), r.get("error"))
                graded.append({"id": r["id"], "status": status, "reason": reason})

        proj_graded_data = {"title": proj["title"], "time": elapsed, "results": graded}
        all_graded[proj["name"]] = proj_graded_data

        passes = sum(1 for g in graded if g["status"] == "PASS")
        fails = sum(1 for g in graded if g["status"] == "FAIL")
        unverif = sum(1 for g in graded if g["status"] == "UNVERIFIABLE")
        print(f"    Time: {elapsed:.2f}s | PASS {passes}/32 | FAIL {fails}/32 | UNVERIFIABLE {unverif}/32")

        # Save single-engine results JSON into the specific project folder
        folder_path = Path(__file__).resolve().parent / proj["name"]
        folder_path.mkdir(parents=True, exist_ok=True)
        folder_json_path = folder_path / "benchmark_32_results.json"
        with open(folder_json_path, "w") as f:
            json.dump({proj["name"]: proj_graded_data}, f, indent=2)
        print(f"    Saved per-folder results to: {folder_json_path}")

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------
    diff_only_ids = {c["id"] for c in test_cases if c["cat"] != "Integration & Limits"}

    print("\n" + "=" * 88)
    print("SUMMARY")
    print("=" * 88)
    header = f"{'Engine':<38} | {'Full 32':<10} | {'Diff-only (28)':<16} | {'Unverifiable':<12}"
    print(header)
    print("-" * len(header))
    for name, data in all_graded.items():
        res = data["results"]
        full_pass = sum(1 for g in res if g["status"] == "PASS")
        diff_pass = sum(1 for g in res if g["status"] == "PASS" and g["id"] in diff_only_ids)
        diff_total = len(diff_only_ids)
        unverif = sum(1 for g in res if g["status"] == "UNVERIFIABLE")
        print(f"{data['title']:<38} | {full_pass}/32 ({full_pass/32*100:4.1f}%) | "
              f"{diff_pass}/{diff_total} ({diff_pass/diff_total*100:4.1f}%) | {unverif}")

    print("=" * 88)

    # Save / Update global results JSON
    if target_engine_name:
        global_out_name = "benchmark_32_results_multi_test.json"
    else:
        global_out_name = "benchmark_32_results_oracle_graded.json"
        
    global_out_path = Path(__file__).resolve().parent / global_out_name
    global_data = {}
    if global_out_path.exists():
        try:
            with open(global_out_path, "r") as f:
                global_data = json.load(f)
        except Exception:
            global_data = {}
    
    global_data.update(all_graded)

    with open(global_out_path, "w") as f:
        json.dump(global_data, f, indent=2)
    print(f"\nUpdated global benchmark summary at: {global_out_path}")


if __name__ == "__main__":
    main()