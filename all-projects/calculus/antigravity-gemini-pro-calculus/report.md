# Calculus Engine Correctness Audit Report (Created by Antigravity [Gemini Pro 3.1 (HIGH)])

## 1. Adversarial Inputs Tried

I wrote a custom script (`audit.py`) to systematically test the calculus engine against several adversarial mathematical and edge cases. I focused on operations that often trigger undefined behavior, silent failures, or crashes in naive symbolic engines:

- **Zero divided by zero (`0 / 0`)**: Tests undefined behavior and `NaN` handling.
- **Division by zero with a variable (`x / 0`)**: Tests how the simplifier and evaluator handle non-zero numerators divided by zero.
- **Zero to a negative power (`0 ^ -1`)**: A mathematical impossibility that typically causes divide-by-zero or exponentiation errors.
- **Negative base to a fractional power (`(-1) ^ 0.5`)**: Yields complex numbers, which often break formatting or evaluation functions expecting reals.
- **Variable base to a variable exponent (`x ^ x`)**: Tests the generalized power rule logic.
- **Double unary minus (`--x`)**: Tests the parsing and simplification of consecutive unary operators.
- **Trigonometric division (`sin(x) / cos(x)`)**: Tests the chain and quotient rules acting together, and checks numerical stability.
- **Expressions collapsing to zero division (`1 / (x - x)`)**: Tests how expressions that evaluate to zero at runtime are handled during simplification and evaluation.

## 2. Findings

The audit surfaced several critical bugs, crashes, and mathematically unsafe behaviors:

1. **Silent Incorrect Result for Variable Exponents (`x ^ x`)**: The `differentiate()` method in `PowNode` blindly assumed that the exponent acts as a constant if the node wasn't explicitly checked, incorrectly yielding `x * x^(x-1)` instead of raising a `NotImplementedError` or returning the correct derivative `x^x * (ln(x) + 1)`. This is a silent failure yielding an incorrect mathematical result.
2. **Crash on Complex Numbers (`(-1) ^ 0.5`)**: Expressions that simplify to complex numbers caused the engine to crash when `__str__` was called on `ConstNode`, because `complex` objects in Python do not have the `is_integer()` method.
3. **Crash on Negative Power of Zero (`0 ^ -1`)**: `PowNode.simplify()` crashed with a `ZeroDivisionError` because it attempted to blindly evaluate `0 ** -1` using Python's exponentiation operator when both base and exponent were constants.
4. **Incorrect Simplification of `0^x`**: `PowNode.simplify()` aggressively simplified `0 ^ x` to `0` whenever the base was zero, regardless of the exponent. This meant that `0 ^ -1` would incorrectly simplify to `0` instead of remaining unsimplified or returning undefined.
5. **Mathematically Incorrect `0/0` Handling**: `DivNode.simplify()` returned `0` for `0/0` (because it checked if the numerator was zero before checking the denominator), and `DivNode.evaluate()` returned `inf` for `0/0`, both of which are mathematically incorrect (it should be `NaN`).

## 3. Changes Made and Why

To resolve these issues, I made the following modifications directly to `math_ast.py`:

- **Fixed `0 / 0` and Zero Division Logic in `DivNode`**:
  - In `simplify()`: Reordered checks so that if the denominator is `0`, the node doesn't simplify to `0`. If both numerator and denominator are `0`, it correctly simplifies to `ConstNode(float('nan'))`.
  - In `evaluate()`: Explicitly catch `den == 0`. If `num == 0`, it returns `float('nan')`. Otherwise, it returns `inf` or `-inf` depending on the sign of the numerator.
- **Added Complex Number Support in `ConstNode.__str__`**:
  - Added a check for `isinstance(self.value, complex)` and wrapped the `.is_integer()` call in a `try-except` block to ensure that mathematical expressions evaluating to complex numbers (like `(-1) ^ 0.5`) can be printed and simplified without crashing the program.
- **Fixed `ZeroDivisionError` in `PowNode.simplify`**:
  - Wrapped the python evaluation `left.value ** right.value` in a `try...except ZeroDivisionError` block. If a zero division occurs (e.g. `0 ^ -1`), the engine safely falls back to returning the unsimplified AST node instead of crashing.
  - Removed the overly aggressive shortcut that forced `0 ^ x = 0`. Now, `0 ^ x` remains structurally preserved unless `x` is explicitly evaluated.
- **Restored Mathematical Safety for `x ^ x` in `PowNode.differentiate`**:
  - Replaced the unsafe fallback that incorrectly applied the simple power rule to variable exponents. It now explicitly raises a `NotImplementedError` explaining that variable exponents require natural logarithms (`ln`), which are not currently implemented in the AST. This prevents silent incorrect outputs.

## Conclusion

```txt
Ran command: `python3 main.py -p lite --benchmark`
Listed directory antigravity-gemini-pro-calculus
Viewed parser.py:1-134
Viewed math_ast.py:1-335
Created audit.py
Ran command: `python3 audit.py`
Edited audit.py
Ran command: `python3 audit.py`
Edited math_ast.py
Ran command: `python3 audit.py`
Viewed math_ast.py:240-285
Edited math_ast.py
Ran command: `python3 audit.py`
Created report.md

I have completed the independent correctness audit of your symbolic calculus engine and have documented the entire process in the newly created [report.md](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-gemini-pro-calculus/report.md) file.

To summarize the effort:

1. **Adversarial Inputs Created**: I built an `audit.py` script containing inputs designed specifically to cause divide-by-zero errors, invalid simplifications, fractional powers of negative numbers, and unsupported complex chain-rule operations (e.g., `0/0`, `0^-1`, `(-1)^0.5`, `x^x`, `--x`).
2. **Key Bugs Found**:
    - `0/0` incorrectly simplified to `0` instead of `NaN`.
    - Differentiating `x^x` silently failed and returned `x * x^(x-1)` (an invalid mathematical assumption treating the exponent as a constant).
    - `0^-1` raised an unhandled `ZeroDivisionError` causing crashes during simplification.
    - Resolving `(-1)^0.5` returned a `complex` number, which subsequently crashed `ConstNode`'s `__str__` because `complex` objects lack the `.is_integer()` method.
    - Aggressively simplifying `0^x` to `0` meant that even cases like `0^-1` were structurally coerced to `0` leading to incorrect math.
3. **Changes Implemented**:
    - I completely fixed `DivNode`'s evaluation and simplification logic to properly return `NaN` or `inf` depending on context instead of `0`.
    - I updated `ConstNode.__str__` to safely ignore the `.is_integer()` formatting check if the value evaluates to a `complex` object.
    - I added a safe `try...except ZeroDivisionError` block in `PowNode.simplify()` to prevent crashing the simplification process when unviable math occurs, falling back to an unsimplified node instead.
    - I removed the generic shortcut that coerced `0^x` into `0`, so expressions retain accuracy when exponent values aren't guaranteed to be non-zero/positive constants.
    - `PowNode` differentiation now correctly raises a `NotImplementedError` for variable-based exponentiation rather than returning dangerously incorrect derivative answers.

You can run `python3 audit.py` to see the adversarial suite successfully run through the patched AST rules.
```
