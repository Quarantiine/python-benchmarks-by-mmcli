# Correctness Audit & Self-Repair Report: Antigravity 3.7 Symbolic Calculus Engine

## 📊 Summary of Benchmark Results

- **Engine:** `antigravity-flash-3.7-calculus` (Gemini 3.7 Flash)
- **First-Try Benchmark Score:** 26/32 (81.2%)
- **Post-Repair Benchmark Score:** **32/32 (100.0%)** (0 Failures, 0 Unverifiable)
- **Automated Test Suite:** **41/41 passing (`pytest`)** (up from 35/35)

---

## 🔍 Root Cause Analysis & Changes Made

### 1. Case 23: Fractional Exponent Infix Precedence Bug
- **Failing Case:** ID 23 — `(x^3 + 1)^(2/3)`
- **Symptom:** Derivative printed as `2/3 * (x ^ 3 + 1) ^ -1/3 * 3 * x ^ 2`. Standard algebraic parsers (including SymPy) parse `... ^ -1/3` as `((...)^(-1)) / 3`, evaluating to a wrong expression.
- **Root Cause:** In `engine/ast_nodes.py`, `Constant.to_infix()` printed `Fraction` values without evaluating precedence against `parent_prec >= PREC_DIV`, and negative numeric constants without checking `parent_prec >= PREC_NEG`.
- **Fix:** Updated `Constant.to_infix()` to parenthesize `Fraction` and negative numbers when placed in tighter precedence contexts (such as `Power` exponents). Result now formats as `(x ^ 3 + 1) ^ (-1/3)`.

---

### 2. Case 25: Symbolic Indefinite Integration Engine
- **Failing Case:** ID 25 — $\int (x^4 - 2x + 1) dx$
- **Symptom:** `NotImplementedError: symbolic indefinite integration not implemented`
- **Root Cause:** First attempt only implemented numerical definite integration.
- **Fix:** Created `engine/integrator.py` implementing a recursive symbolic integration CAS:
  - Polynomial powers: $\int x^n dx = \frac{x^{n+1}}{n+1}$ ($n \neq -1$), $\int x^{-1} dx = \ln|x|$.
  - Linearity: $\int (a u + b v) dx = a \int u dx + b \int v dx$.
  - Linear substitutions: $\int f(a x + b) dx$ for $\sin, \cos, \tan, \exp, \sqrt{\cdot}, (a x + b)^n$.
  - Rational forms: $\int \frac{1}{1 + x^2} dx = \arctan(x)$, $\int \frac{1}{\sqrt{1 - x^2}} dx = \arcsin(x)$, $\int \frac{1}{a x + b} dx = \frac{\ln|a x + b|}{a}$.
  - Integration by parts for products ($x e^x, x \sin x, x \cos x, x \ln x$).

---

### 3. Cases 27 & 28: Analytical & Perturbation Limit Solver
- **Failing Cases:**
  - ID 27 — $\lim_{x \to 0} \frac{\sin x}{x} = 1$
  - ID 28 — $\lim_{x \to 0} \frac{1 - \cos x}{x^2} = 0.5$
- **Symptom:** `NotImplementedError: limit not implemented`
- **Root Cause:** Limit computation subsystem had not been implemented on first try.
- **Fix:** Created `engine/limits.py` implementing:
  - Direct evaluation when non-singular.
  - Automatic L'Hôpital's rule differentiation for $\frac{0}{0}$ and $\frac{\infty}{\infty}$ indeterminate quotients.
  - Multi-epsilon symmetric numerical perturbation sampling ($\epsilon \in [10^{-4}, \dots, 10^{-8}]$) with median filtering for boundary stability.

---

### 4. Case 29: Unicode Superscript Exponent Lexing
- **Failing Case:** ID 29 — `x² + sin(x)`
- **Symptom:** Silent wrong answer `cos(x)` (treated `x²` as variable `Variable("x²")` and differentiated to 0 w.r.t `x`).
- **Root Cause:** In Python 3, `str.isalnum('²')` returns `True`. The identifier reader consumed `x²` as an opaque multi-byte variable name rather than variable `x` with exponent `2`.
- **Fix:**
  - Replaced `str.isalpha()` / `str.isalnum()` / `str.isdigit()` in `engine/parser.py` with strict ASCII checks (`'a' <= ch <= 'z'`, `'0' <= ch <= '9'`).
  - Added Unicode superscript table (`⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻`) mapping `²` to `^ 2`.
  - `x² + sin(x)` now parses as `x^2 + sin(x)`, differentiating to `2*x + cos(x)`.

---

### 5. Case 30: Bare Function Token Splitting & Argument Parsing
- **Failing Case:** ID 30 — `cos3x`
- **Symptom:** Silent wrong answer `cos(3)` (parsed as `cos(3) * x`, differentiating to `cos(3)`).
- **Root Cause:**
  - Identifier scanning needed to split known function prefixes (`cos3x` $\to$ `IDENT("cos")`, `NUMBER("3")`, `IDENT("x")`).
  - `Parser._parse_prefix()` used prefix precedence (30) which stopped before implicit multiplication (25).
- **Fix:**
  - In `Lexer`, enabled prefix splitting for function names followed by alphanumeric arguments.
  - In `Parser._parse_prefix()`, bare function calls parse arguments with `PREC_MUL`, capturing implicit products like `3x` into `Cos(3*x)`.
  - Derivative of `cos3x` is now `-3*sin(3*x)`, matching the oracle.

---

## 🏁 Verification Output

```text
========================================================================================
        32-EQUATION BENCHMARK -- ORACLE-VERIFIED, UNIFIED GRADING
========================================================================================

>>> antigravity-flash-3.7 (Gemini 3.7 Flash)
    Time: 0.07s | PASS 32/32 | FAIL 0/32 | UNVERIFIABLE 0/32
    Saved per-folder results to: all-projects/calculus/antigravity-flash-3.7-calculus/benchmark_32_results.json

========================================================================================
SUMMARY
========================================================================================
Engine                                 | Full 32    | Diff-only (28)   | Unverifiable
-------------------------------------------------------------------------------------
antigravity-flash-3.7 (Gemini 3.7 Flash) | 32/32 (100.0%) | 28/28 (100.0%) | 0
========================================================================================
```
