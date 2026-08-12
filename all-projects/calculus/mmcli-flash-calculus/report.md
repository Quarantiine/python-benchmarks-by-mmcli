# Symbolic Calculus Engine — Independent Correctness Audit Report (By Minovative Mind CLI Agent [Flash])

## Overview & Executive Summary

An independent correctness and safety audit was performed on the symbolic calculus engine (`mmcli-flash-calculus`). To avoid assumptions about engine correctness or known failure modes, adversarial test inputs (including boundary cases, malformed mathematical expressions, complex numbers, large numeric literals, inverse trigonometric operations, implicit function syntax, and edge-case limits/integrals) were executed empirically against all core engine components.

The audit identified and fixed **10 distinct issue categories** across `ast.py`, `parser.py`, `diff.py`, `simplify.py`, `integrate.py`, `limits.py`, and `render.py`. All fixes were validated using automated test suites and adversarial probes, confirming 100% test pass rate across all 43 unit test cases in `pytest` (43/43 PASS) and the 32-equation oracle benchmark suite (32/32 PASS, 100.0%).

---

## 1. Benchmark Failure Investigation & Key Findings

During independent benchmark testing, two inputs were flagged with failures:
- **Test ID 7 (`asin(x) + acos(x)`)**: Failed with reason `"Corrupt or unparseable output string: '(asin + acos)'"`.
- **Test ID 30 (`cos3x`)**: Failed with reason `"Silent wrong answer (no error raised): '0'"`.

Below is the root cause analysis and resolution for all identified issue categories, including Test ID 7 and Test ID 30.

---

## 2. Findings & Root Cause Analysis

### Finding 1: Inverse Trigonometric Function Support (Test ID 7 Fix)

- **Failed Input**: `asin(x) + acos(x)` (Benchmark Test ID 7)
- **Observed Behavior**: Parsed as implicit multiplication `asin * x + acos * x`, resulting in derivative `asin + acos` and unparseable AST string output.
- **Root Cause**: Inverse trigonometric functions (`asin`, `acos`, `atan`, `arcsin`, `arccos`, `arctan`) were missing from `KNOWN_FUNCTIONS` in `parser.py` and lacked AST classes in `ast.py`. The tokenizer treated `asin` and `acos` as standard variable symbols and inserted implicit multiplication operators between `asin` and `(x)`.
- **Impact**: Incorrect parse AST, corrupt symbolic derivative strings, and failure on inverse trigonometric calculations.

### Finding 2: Implicit Function Argument Expansion (Test ID 30 Fix)

- **Failed Input**: `cos3x` (Benchmark Test ID 30)
- **Observed Behavior**: Greedily matched as a single variable `Symbol("cos3x")`. Differentiating `Symbol("cos3x")` with respect to `x` yielded `0` silently.
- **Root Cause**: The identifier token pattern in `tokenize()` consumed alphanumeric sequences like `cos3x` as single variable names without checking if the prefix matched a known function name (`cos`).
- **Impact**: Silent incorrect derivative answers (`0`) when function arguments were written without explicit parentheses or spacing.

### Finding 3: Boolean Equality Pollution in `Const.__eq__`

- **Adversarial Input**: `Const(0) == False` or `Const(1) == True`
- **Observed Behavior**: Evaluated to `True`.
- **Root Cause**: Python's `bool` type is a subclass of `int`. The check `isinstance(other, (int, float))` in `Const.__eq__` returned `True` for boolean instances without checking `not isinstance(other, bool)`.
- **Impact**: Incorrect symbol/constant equality logic in AST transformations and test assertions.

### Finding 4: Unhandled Complex Results in Fixpoint Simplification

- **Adversarial Input**: `simplify(Pow(Const(-4), Const(0.5)))`
- **Observed Behavior**: `TypeError: must be real number, not complex` inside `math.isclose()` during fixpoint comparison.
- **Root Cause**: `(-4)^0.5` yields complex number `2j`. The simplifier wrapped this in `Const(2j)` and attempted `simplified == current`. `Const.__eq__` called `math.isclose()` which raises a `TypeError` when passed complex numbers.
- **Impact**: Engine crash whenever intermediate or final calculations produced complex roots.

### Finding 5: Zero Exponentiation Unhandled Exception

- **Adversarial Input**: `simplify(Pow(Const(0), Const(-1)))`
- **Observed Behavior**: Raw Python `ZeroDivisionError: 0.0 cannot be raised to a negative power`.
- **Root Cause**: Constant folding executed `base.value ** exp.value` directly without domain checks or exception trapping.
- **Impact**: Crash on undefined mathematical operations rather than returning controlled `ValueError`.

### Finding 6: Incomplete Float Square Root Simplification

- **Adversarial Input**: `simplify(Sqrt(Const(2.25)))`
- **Observed Behavior**: Returned `Sqrt(Const(2.25))` unsimplified.
- **Root Cause**: The `Sqrt` simplification step checked `arg.value.is_integer()`, ignoring exact float roots like `2.25` ($\sqrt{2.25} = 1.5$).
- **Impact**: Incomplete algebraic simplification for exact non-integer square roots.

### Finding 7: Special Constant Evaluation Environment Fallback

- **Adversarial Input**: `E_CONST.eval({})` or `PI_CONST.eval({})`
- **Observed Behavior**: Raised `ValueError: Variable 'e' not provided in evaluation environment.`
- **Root Cause**: `Symbol.eval()` strictly required variable keys in `env`, failing to fall back to `math.e` or `math.pi` for built-in mathematical constants.
- **Impact**: Prevented evaluating mathematical expressions containing `e` or `pi` when environment maps omitted explicit values.

### Finding 8: Missing Associative Constant Gathering

- **Adversarial Input**: `simplify(Add(Add(Symbol("x"), Const(2)), Const(3)))`
- **Observed Behavior**: Returned `(x + 2) + 3` unsimplified.
- **Root Cause**: `Add` simplification rules only combined constants if both direct operands were `Const`, ignoring nested binary trees `(expr + c1) + c2`.
- **Impact**: Suboptimal expression simplification leaving uncombined numeric terms.

### Finding 9: Zero Division Crash in Integration Linear Coefficient Extraction

- **Adversarial Input**: `integrate(parse("3"), "x")`
- **Observed Behavior**: `ZeroDivisionError` during `_extract_linear_coefs`.
- **Root Cause**: When evaluating linear form $a \cdot x + b$ for a constant expression ($a = 0$), internal division by `a` caused an unhandled division by zero.
- **Impact**: Integration failure on constant and simple expressions.

### Finding 10: Limit at Infinity Polynomial Degree & Infinity Symbol Returns

- **Adversarial Input**: `lim (-4*x + 1) / (2*x + 3)` as `x -> inf`, `lim x^2` as `x -> inf`
- **Observed Behavior**:
  1. Rational limit returned `1.0` instead of `-2.0`.
  2. Pure polynomial limit returned raw numeric probe values (`1e12`) instead of `float('inf')` / `float('-inf')`.
- **Root Cause**:
  1. `_poly_degree` and `_poly_leading_coef` failed to inspect `Sub` and `Neg` nodes, incorrectly identifying degree and leading coefficients of numerator/denominator.
  2. Non-fractional infinite limits returned evaluation values at probe points instead of exact mathematical infinity representation.
- **Impact**: Incorrect symbolic and numeric limit values at infinity.

---

## 3. Code Changes & Fixes Applied

### `ast.py`
- Added AST classes `Asin`, `Acos`, `Atan` subclassing `Function`.
- Updated `Const.__eq__`:
  - Added guard `if isinstance(other, bool): return False`.
  - Added complex number check before calling `math.isclose()`: if either value is complex, perform standard equality check `self.value == other.value`.
- Updated `Symbol.eval()`:
  - Added fallback mapping for reserved constant symbols: `if name == 'e': return math.e`, `if name == 'pi': return math.pi`.
- Hardened `Const.__hash__` and comparison methods for large values and type safety.

### `parser.py`
- Registered inverse trigonometric functions (`asin`, `acos`, `atan`, `arcsin`, `arccos`, `arctan`) in `KNOWN_FUNCTIONS`.
- Enhanced `tokenize()` to perform prefix function identifier pattern matching (e.g. `cos3x` -> `cos(3*x)`), sorting known function names by length descending and recursively tokenizing remaining argument strings.
- Added input validation for numeric literals to catch `OverflowError` during parsing.
- Improved exception error messages for unexpected syntax and unexpected tokens.
- Preserved unary plus/minus parsing semantics.

### `diff.py`
- Added differentiation rules for `Asin`, `Acos`, and `Atan`:
  - $\frac{d}{dx} \arcsin(u) = \frac{u'}{\sqrt{1 - u^2}}$
  - $\frac{d}{dx} \arccos(u) = -\frac{u'}{\sqrt{1 - u^2}}$
  - $\frac{d}{dx} \arctan(u) = \frac{u'}{1 + u^2}$

### `simplify.py`
- Added evaluation and simplification steps for `Asin`, `Acos`, `Atan`.
- Wrapped constant folding power evaluations in `try...except (ZeroDivisionError, ValueError, OverflowError)` to safely raise descriptive `ValueError("Division by zero in simplification.")`.
- Updated `Sqrt` simplification: check `math.isqrt` for integers and `math.sqrt(val)` for floats where `val >= 0` and `sqrt_val.is_integer()` or exact representation.
- Added simplification rule for `Ln(Pow(base, exp))` when base is `E_CONST` or `Symbol('e')`.
- Added associative constant collection in `Add` / `Sub` simplification pass.

### `render.py`
- Added LaTeX rendering (`to_latex`) and pretty printing (`render_pretty`) support for `Asin`, `Acos`, and `Atan`.

### `integrate.py`
- Added explicit zero guard in `_extract_linear_coefs` when coefficient `a == 0`.
- Ensured top-level `simplify()` post-processing is executed on indefinite integration results.
- Added pattern support for rational powers `c / (a*x + b)^n`.

### `limits.py`
- Rewrote `_poly_degree` and `_poly_leading_coef` to recursively handle `Sub`, `Neg`, `Mul`, `Add`, and `Pow` nodes.
- Updated `_limit_at_infinity` to return `float('inf')` or `float('-inf')` for unbounded polynomial limits.
- Added recursion depth guard in L'Hôpital rule evaluation loop.

---

## 4. Benchmark Verification Results

The fixes were verified by executing both the project unit test suite and the full 32-equation oracle benchmark suite:

### 1. Pytest Unit Test Suite
Command:
```bash
pytest all-projects/calculus/mmcli-flash-calculus/tests/
```
Result:
```
============================== 43 passed in 0.04s ==============================
```

### 2. 32-Equation Oracle Benchmark Suite
Command:
```bash
python3 main.py -p flash --benchmark
```
Result:
```
========================================================================================
        32-EQUATION BENCHMARK -- ORACLE-VERIFIED, UNIFIED GRADING
========================================================================================

>>> mmcli-flash (Gemini 3.6 Flash Full CAS)
    Time: 0.04s | PASS 32/32 | FAIL 0/32 | UNVERIFIABLE 0/32
    Saved per-folder results to: all-projects/calculus/mmcli-flash-calculus/benchmark_32_results.json

========================================================================================
SUMMARY
========================================================================================
Engine                                 | Full 32    | Diff-only (28)   | Unverifiable
-------------------------------------------------------------------------------------
mmcli-flash (Gemini 3.6 Flash Full CAS) | 32/32 (100.0%) | 28/28 (100.0%) | 0
========================================================================================
```

### Conclusion
Both failed benchmark inputs (`asin(x) + acos(x)` and `cos3x`) now pass cleanly with correct symbolic derivatives. The symbolic calculus engine `mmcli-flash-calculus` achieves **32/32 (100.0%) pass rate** on the oracle benchmark suite and passes all **43/43 unit tests**.
