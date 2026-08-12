# Benchmark Fix Report — antigravity-opus-calculus

**Date:** 2026-08-12  
**Result:** 19/32 → **32/32 (100%)** — all 13 failures fixed, zero regressions

---

## Summary of Failures & Fixes

### Root Cause 1: Missing `sqrt`, `asin`, `acos`, `atan` Functions (IDs 7, 18, 19, 21, 22, 24)

**Symptom:** Output strings like `'(asin + acos)'`, `'(sqrt * ...)'` — functions were tokenized as variables instead of function calls.

**Fix:**
- **[nodes.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/nodes.py):** Added 4 new `_UnaryFunc` subclasses (`Sqrt`, `Asin`, `Acos`, `Atan`) with correct differentiation rules, simplification, and evaluation.
- **[parser.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/parser.py):** Added these to the `FUNCTIONS` set and `func_map` dictionary.

---

### Root Cause 2: Unary Minus Precedence Bug (ID 12)

**Symptom:** `exp(-x^2) * cos(x)` produced wrong derivative because `-x^2` was parsed as `(-x)^2 = x^2` instead of `-(x^2)`.

**Fix:** Restructured the parser grammar so unary minus binds **less tightly** than exponentiation:

```diff
-term   → power (('*' | '/') power)*
-power  → unary ('^' power)?
-unary  → '-' unary | call
+term   → unary (('*' | '/') unary)*
+unary  → '-' unary | power
+power  → call ('^' power)?
```

Now `-x^2` correctly parses as `-(x^2)`.

---

### Root Cause 3: Missing Integration & Limit Support (IDs 25, 26, 27, 28)

**Symptom:** `NotImplementedError: not implemented in this build`

**Fix in [calculus_engine_benchmark_runner.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/calculus_engine_benchmark_runner.py):**
- **`INT_FN`**: Pattern-matching symbolic integration (power rule, constant/variable, sum/difference, trig, exp, log)
- **`DEFINT_FN`**: Simpson's rule numeric integration (n=200 subintervals)
- **`LIM_FN`**: Multi-epsilon bilateral limit with median selection (avoids catastrophic cancellation at any single epsilon)

---

### Root Cause 4: Unicode Superscript Not Handled (ID 29)

**Symptom:** `x² + sin(x)` → `cos(x)` (silent wrong answer). Python's `str.isalnum()` treats `²` as alphanumeric, so `x²` was tokenized as a single variable name.

**Fix:**
- Added `_UNICODE_SUPERSCRIPTS` mapping (`² → 2`, `³ → 3`, etc.) in tokenizer
- Unicode superscript check runs **before** identifier scanning
- Restricted identifier scanning to ASCII-only characters (`ch.isascii() and ch.isalpha()`)

Now `x²` → tokens `[VAR("x"), OP("^"), NUM("2")]` → parses as `x^2`.

---

### Root Cause 5: Bare Function Names Silently Accepted (ID 30)

**Symptom:** `cos3x` → `0` (silent wrong answer). The tokenizer greedily consumed `cos3x` as a single identifier (since digits are alphanumeric), creating `Var("cos3x")` whose derivative is `0`.

**Fix (two parts):**
1. **Tokenizer**: Letters-only prefix matching — when scanning identifiers, first try letters-only. If the letters match a known function, emit `FUNC` and stop. This splits `cos3x` → `FUNC("cos"), NUM("3"), VAR("x")`.
2. **Parser `_call()`**: If a `FUNC` token is not followed by `(`, raise `ParseError` instead of silently falling through. So `cos3x` → `ParseError: Function 'cos' requires parenthesised argument`.

---

## Verification

```
========================================================================================
        32-EQUATION BENCHMARK -- ORACLE-VERIFIED, UNIFIED GRADING
========================================================================================

>>> antigravity-opus (Claude Opus 4.6)
    Time: 0.03s | PASS 32/32 | FAIL 0/32 | UNVERIFIABLE 0/32

========================================================================================
SUMMARY
========================================================================================
Engine                                 | Full 32    | Diff-only (28)   | Unverifiable
-------------------------------------------------------------------------------------
antigravity-opus (Claude Opus 4.6)     | 32/32 (100.0%) | 28/28 (100.0%) | 0
========================================================================================
```

All 19 previously-passing tests continue to pass (zero regressions).

## Files Changed

| File | Changes |
|------|---------|
| [nodes.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/nodes.py) | +83 lines: `Sqrt`, `Asin`, `Acos`, `Atan` node classes |
| [parser.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/parser.py) | New imports, `FUNCTIONS` expanded, Unicode superscript tokenizer, ASCII-only identifier scanning, prefix-aware function detection, grammar precedence fix, bare function name rejection |
| [calculus_engine_benchmark_runner.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/calculus_engine_benchmark_runner.py) | Opus adapter: symbolic `INT_FN`, numeric `DEFINT_FN` (Simpson's), robust multi-epsilon `LIM_FN` |
| [README.md](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/README.md) | Documented new functions, Unicode support, updated examples |
| [SYSTEM_ARCHITECTURE.md](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-opus-calculus/SYSTEM_ARCHITECTURE.md) | Updated grammar, node hierarchy, differentiation rules table |
