# Symbolic Calculus Engine & Interactive Terminal Interface (TUI)

A pure-Python Computer Algebra System (CAS) and interactive Terminal User Interface (TUI) engine for symbolic and numerical calculus, algebraic simplification, step-by-step derivation breakdowns, and high-resolution Unicode Braille / ASCII curve rendering.

---

## Highlights & Features

- **Robust Pratt Parser**:
  - Handles operator precedence, right-associative exponentiation (`^` / `**`), unary negation.
  - Implicit multiplication (`2x`, `3(x + 1)`, `(x+1)(x-1)`, `2x^2`, `x y`).
  - Unicode superscripts (`x² + 2x + 1`, `x⁻¹`).
  - Parenthesis-free function calls (`sin x`, `cos 3x`).
  - Absolute value bars (`|x - 5|`), scientific notation (`1.5e-3`), and standard named constants (`pi`, `e`, `tau`, `phi`).

- **Mathematical AST Node Hierarchy**:
  - Strongly typed, immutable expression nodes with operator overloading (`+`, `-`, `*`, `/`, `**`, unary `-`).
  - Rich tree formatting (`to_tree_string()`, `to_rich_tree()`) and LaTeX generation (`to_latex()`).
  - Comprehensive elementary and transcendental functions: trigonometric (`sin`, `cos`, `tan`, `sec`, `csc`, `cot`), inverse trigonometric (`asin`, `acos`, `atan`), hyperbolic (`sinh`, `cosh`, `tanh`), exponential (`exp`), logarithmic (`ln`, `log`), and radicals (`sqrt`, `cbrt`, `abs`).

- **Multi-Pass Fixed-Point Algebraic Simplification**:
  - Exact constant folding with rational fractions (`fractions.Fraction`).
  - Additive identities ($x + 0 = x$, $x - x = 0$, $x + (-x) = 0$).
  - Multiplicative identities ($x \cdot 1 = x$, $x \cdot 0 = 0$, $x / 1 = x$, $x / x = 1$).
  - Power laws ($x^0 = 1$, $x^1 = x$, $x^a \cdot x^b = x^{a+b}$, $x^a / x^b = x^{a-b}$, $(x^a)^b = x^{ab}$).
  - Like-term combining ($3x + 4x = 7x$, $5x - 2x = 3x$).
  - Transcendental reductions ($\sin(0) = 0$, $\cos(0) = 1$, $\ln(1) = 0$, $\ln(e^x) = x$, $e^{\ln(x)} = x$).

- **Symbolic Differentiation & Multivariable Engine**:
  - Full recursive application of Power Rule, Product Rule, Quotient Rule, and Generalized Chain Rule.
  - Higher-order derivatives ($f^{(n)}(x)$), partial derivatives ($\frac{\partial f}{\partial x_i}$), symbolic gradient vectors ($\nabla f$), and Hessian matrices ($H(f)$).
  - Taylor series polynomial expansions about arbitrary points $x_0$.
  - Tangent line equations ($y = mx + b$).
  - Root finding via Newton-Raphson method and automatic critical point classification (local minima, local maxima, inflection points).

- **Hierarchical Step-by-Step Derivation Tracker**:
  - Records nested rule application trees (Rule Name, Mathematical Formula, Input Expression, Target Variable, Intermediate Result, Simplified Result).
  - Terminal text rendering and full `Rich` colorized tree diagrams.

- **Symbolic & Numerical Integration**:
  - Indefinite antiderivatives ($∫ f(x) \, dx$) via linear decomposition, power rule, exponential/trigonometric tables, and integration by parts ($∫ u \, dv = uv - ∫ v \, du$).
  - Definite integration ($∫_a^b f(x) \, dx$) utilizing Fundamental Theorem of Calculus ($F(b) - F(a)$) with fallback to adaptive Simpson's quadrature.

- **Analytical & Numerical Limits Engine**:
  - Direct substitution and continuity analysis.
  - Multi-pass symbolic L'Hôpital's rule for indeterminate forms ($\frac{0}{0}$, $\frac{\infty}{\infty}$).
  - Multi-epsilon perturbation sampling with symmetric Richardson extrapolation.
  - One-sided limits ($x \to a^+$, $x \to a^-$) and infinite limits ($x \to \pm\infty$).

- **High-Resolution Terminal Visualizer**:
  - 2x4 subpixel Unicode Braille plotting (`PlotCanvas`) with Bresenham line rasterization.
  - Standard ASCII plotting (`AsciiCanvas`) fallback.
  - Multi-curve overlay (function $f(x)$, first derivative $f'(x)$, second derivative $f''(x)$, and tangent lines).
  - Automatic $y$-axis scaling with outlier and asymptote clipping.

- **Interactive Terminal User Interface (TUI)**:
  - Full-screen interactive terminal app built with clean fallback between modern `Textual` and standard ANSI/curses mode.
  - Real-time expression evaluation, interactive AST visualizer, step derivation viewer, and dynamic curve plotting.

---

## 32-Equation Benchmark Performance

The engine passes **32/32 (100%)** equations in the standard benchmark suite, validated against independent SymPy oracle truth models across all 8 categories:

| Category | Equations | Result |
| :--- | :--- | :--- |
| 1. Polynomials & Power Rules | `3x^5 - 4x^2 + 7x - 12`, `(2x+5)^4`, `x^-3 + x^-0.5`, `(x^2+1)(3x^3-2)` | **PASS (4/4)** |
| 2. Trigonometric & Inverse Trig | `sin(x)cos(x)`, `tan(x^2+1)`, `asin(x)+acos(x)`, `tan(x)^2+1` | **PASS (4/4)** |
| 3. Exponential & Logarithmic | `exp(3x)(x^2-2x+2)`, `ln(x^2+1)/x`, `x^3 ln(x)`, `exp(-x^2)cos(x)` | **PASS (4/4)** |
| 4. Product & Quotient Rules | `(x^2+1)/(x^3-1)`, `sin(x)/(cos(x)+1)`, `x^2 sin(x) ln(x)`, `(exp(x)sin(x))/(x^2+1)` | **PASS (4/4)** |
| 5. Multi-Layer Nested Chain Rule | `sin(cos(tan(x)))`, `sqrt(1+sin(x)^2)`, `exp(sqrt(x^2+4))`, `ln(sin(x^3+1))` | **PASS (4/4)** |
| 6. Radical Roots & Fractional Powers | `sqrt(x^3+2x)`, `1/sqrt(4-x^2)`, `(x^3+1)^(2/3)`, `sqrt(x)ln(sqrt(x))` | **PASS (4/4)** |
| 7. Integration & Limits | `∫ (x^4-2x+1) dx`, `∫_0^3 x^2 dx`, `lim_{x->0} sin(x)/x`, `lim_{x->0} (1-cos(x))/x^2` | **PASS (4/4)** |
| 8. Boundary Conditions & Unicode | `x² + sin(x)`, `cos3x`, syntax error rejection on `sin(x` and `x = 2` | **PASS (4/4)** |

---

## Installation & Quickstart

```bash
# Clone and enter workspace
git clone <repo_url>
cd calculus-engine

# Install optional dependencies
pip install -r requirements.txt
```

### Running the Interactive TUI
```bash
# Launch interactive TUI
python3 app.py

# Or via package entrypoint
python3 -m engine
```

### CLI Commands

```bash
# Differentiate an expression with step-by-step breakdown
python3 cli.py "x^2 * sin(x)" --diff x --steps

# Plot function and its derivative on terminal
python3 cli.py "sin(x^2)" --plot --x-min -3 --x-max 3

# Compute definite integral
python3 cli.py "x^2 + 3*x" --integral 0 3

# Compute limit with L'Hopital rule
python3 cli.py "sin(x) / x" --limit 0

# Compute Taylor polynomial expansion
python3 cli.py "exp(x)" --taylor 4 --eval 0.1

# Compute tangent line and critical points
python3 cli.py "x^3 - 3*x" --tangent 1.5 --critical --roots
```

---

## Python API Usage

```python
from engine import (
    parse, diff, simplify, integrate, definite_integrate,
    limit, gradient, hessian, DerivationTracker,
    plot_expression, render_ast_tree
)

# 1. Parsing & Simplification
ast = parse("3*x + 4*x + 0")
simplified = simplify(ast)
print(simplified)  # 7 * x

# 2. Symbolic Differentiation with Step Tracking
tracker = DerivationTracker()
derivative = diff("sin(x^2)", var="x", tracker=tracker)
print("Derivative:", derivative)  # 2 * x * cos(x ^ 2)
print(tracker.format_text())

# 3. Multivariable Gradient & Hessian
grad = gradient("x^2 + 3*y^2", ["x", "y"])
print("Gradient:", grad)  # [2 * x, 6 * y]

# 4. Symbolic and Definite Integration
anti = integrate("x * exp(x)", "x")
print("Antiderivative:", anti)  # (x - 1) * exp(x)

def_int = definite_integrate("x^2", "x", lower=0, upper=3)
print("∫_0^3 x^2 dx =", def_int)  # 9.0

# 5. Limits
lim_val = limit("sin(x) / x", "x", point=0)
print("lim_{x->0} sin(x)/x =", lim_val)  # 1.0

# 6. Terminal Braille Plotting
plot_str = plot_expression(parse("sin(x)"), var="x", include_derivative=True)
print(plot_str)
```

---

## Running Test Suites

Run the full pytest suite:

```bash
pytest
```

Output:
```
============================= 155 passed in 0.55s ==============================
```
