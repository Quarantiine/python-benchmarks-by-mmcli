# Calculus Engine Bug Fix Report

## Overview
This report details the bug fixes made to the `antigravity-gemini-pro-calculus` symbolic calculus engine to address 23 test failures identified by the independent oracle-verified benchmark. After the fixes, the engine achieves a perfect 32/32 score (100%) on the benchmark suite with no regressions.

## Changes Made

### 1. Extended Parser Support for Transcendental Functions
**Issue:** The tokenizer and AST previously only supported `sin` and `cos`, causing a `ParseError: Unexpected token at end: ('OP', '(')` when it encountered other valid functions like `tan`, `asin`, `acos`, `exp`, `ln`, and `sqrt`.
**Fix:**
- Updated the `tokenize` regex for `FUNC` in `parser.py` to match `sin|cos|tan|asin|acos|exp|ln|sqrt`.
- Added corresponding AST nodes (`TanNode`, `AsinNode`, `AcosNode`, `ExpNode`, `LnNode`, `SqrtNode`) to `math_ast.py`.
- Updated `base()` in `parser.py` to instantiate these new nodes when parsing the respective functions.
- Implemented the correct chain-rule differentiation logic for each new function in `math_ast.py`.

### 2. Generalization of `PowNode` Differentiation
**Issue:** Test cases like `x^(-3) + x^(-0.5)` failed with a `NotImplementedError: Differentiation of variable exponents...` because negative exponents were parsed as multiplication nodes (e.g., `-1 * 3`), which the `PowNode`'s `differentiate` method refused to handle (as it explicitly required the exponent to be a `ConstNode`).
**Fix:**
- Modified `PowNode.differentiate` in `math_ast.py` to handle generalized `u^v` forms.
- Now, it checks if `v`'s derivative evaluates to 0 (i.e. `v` is constant with respect to the variable of differentiation). If so, it applies the standard power rule. If not, it falls back to the generalized formula: `u^v * (v' * ln(u) + v * u' / u)`.

### 3. Corrected Precedence of Unary Minus
**Issue:** The expression `exp(-x^2) * cos(x)` evaluated to an incorrect derivative because `-x^2` was parsed as `(-x)^2` instead of `-(x^2)`.
**Fix:**
- Corrected the parsing grammar in `parser.py`. Exponentiation (`^`) now binds tighter than unary negation (`-`).
- Introduced a dedicated `unary()` method in `Parser` that sits between `term` (multiplication/division) and `factor` (exponentiation), properly parsing `-x^2` into a `MulNode` of `-1` and `x^2`.

### 4. Restricted Variable Tokenization
**Issue:** The engine incorrectly parsed `x\u00b2` into a valid AST, treating the unicode exponent as part of the variable name, leading to a silent wrong answer.
**Fix:**
- Modified the `VAR` token specification in `parser.py` from `r'[a-zA-Z_]\w*'` to `r'[a-zA-Z_][a-zA-Z0-9_]*'`, strictly restricting identifiers to alphanumeric ASCII characters. This cleanly rejects arbitrary unicode numbers as `ParseError`s, restoring proper boundary handling.

### 5. Added Basic Integration and Limits Support
**Issue:** The runner specifically failed tests 25-28 (`int`, `defint`, `lim` categories) because the engine's `INT_FN`, `DEFINT_FN`, and `LIM_FN` endpoints in the benchmark runner threw a `NotImplementedError`.
**Fix:**
- Created a new `engine.py` module containing `integrate` and `limit` functions.
- Implemented basic polynomial integration (power rule and sum/difference distributions) to support the required integration tests.
- Implemented a numeric L'Hôpital-capable evaluation strategy for `limit` up to 10 derivative steps to resolve `0/0` or `inf/inf` singularities dynamically.
- Updated `calculus_engine_benchmark_runner.py`'s adapter for `antigravity-gemini-pro-calculus` to invoke the new `engine.py` functions, eliminating the `NotImplementedError`s and achieving correct mathematical evaluation.
