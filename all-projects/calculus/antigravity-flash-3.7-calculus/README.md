# Antigravity 3.7 Symbolic Calculus Engine & Terminal TUI

A high-performance symbolic calculus engine featuring an Abstract Syntax Tree (AST), recursive algebraic differentiation, step-by-step derivation breakdown, algebraic simplification, and a rich interactive Terminal User Interface (TUI) with Unicode Braille graph plotting.

---

## 🌟 Key Features

1. **Abstract Syntax Tree (AST) & Parser**:
   - Pratt / Precedence-climbing mathematical parser supporting standard operators (`+`, `-`, `*`, `/`, `^`), unary operators, and implicit multiplication (e.g. `2x`, `3sin(x)`, `(x+1)(x-1)`).
   - Complete AST hierarchy: `Constant`, `NamedConstant` ($\pi, e, \tau, \phi$), `Variable`, binary operations, and elementary functions ($\sin, \cos, \tan, \sec, \csc, \cot, \arcsin, \arccos, \arctan, \sinh, \cosh, \tanh, \exp, \ln, \log_b, \sqrt{\cdot}, |\cdot|$).
   - Rich AST visualizer: collapsible and color-coded tree structure.

2. **Recursive Symbolic Differentiation**:
   - **Constant & Variable Rules**: $\frac{d}{dx}[c] = 0$, $\frac{d}{dx}[x] = 1$.
   - **Sum & Difference Rules**: $(u \pm v)' = u' \pm v'$.
   - **Product & Constant Multiple Rules**: $(u \cdot v)' = u'v + uv'$, $(c \cdot u)' = c \cdot u'$.
   - **Quotient Rule**: $\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}$.
   - **Power Rules**:
     - Standard Power Rule: $\frac{d}{dx}[u^n] = n u^{n-1} u'$
     - Exponential Rule: $\frac{d}{dx}[a^u] = a^u \ln(a) u'$
     - General Power Rule: $\frac{d}{dx}[u^v] = u^v \left( v' \ln u + \frac{v u'}{u} \right)$
   - **Chain Rule**: $\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$ across all elementary functions.
   - **Multivariable Calculus**: Partial derivatives $\frac{\partial f}{\partial x_i}$, Gradient vector $\nabla f$, Hessian matrix $H$.
   - **Higher-Order Derivatives**: $n$-th order symbolic differentiation.

3. **Symbolic Indefinite & Definite Integration**:
   - Polynomial & Power rules: $\int x^n dx = \frac{x^{n+1}}{n+1}$, $\int x^{-1} dx = \ln|x|$.
   - Linearity: $\int (a u + b v) dx = a \int u dx + b \int v dx$.
   - Linear substitution for trig, exponentials, roots, and fractions ($\sin(ax+b), \cos(ax+b), e^{ax+b}, \frac{1}{ax+b}, \frac{1}{1+x^2}, \frac{1}{\sqrt{1-x^2}}$).
   - Integration by parts for products ($x e^x, x \sin x, x \cos x, x \ln x$).

4. **Analytical & Numerical Limit Solver**:
   - Automatic L'Hôpital's rule differentiation for $\frac{0}{0}$ and $\frac{\infty}{\infty}$ indeterminate quotients.
   - Multi-epsilon perturbation sampling with median filtering.

5. **Step-by-Step Derivation Breakdown**:
   - Hierarchical tree tracking of every rule applied during differentiation.
   - Displays rule name, exact mathematical formula, input sub-expressions, intermediate unsimplified results, and simplified steps.

6. **Algebraic Simplification Engine**:
   - Constant folding with exact fractional arithmetic (`fractions.Fraction`).
   - Identity reductions ($x+0=x$, $x \cdot 1=x$, $x \cdot 0=0$, $x^1=x$, $x^0=1$, $0/x=0$, etc.).
   - Linear term grouping ($3x + 2x = 5x$), power combining ($x^a \cdot x^b = x^{a+b}$), double negation ($-(-x) = x$).
   - Trigonometric & exponential reductions ($\sin(0)=0, \cos(0)=1, \exp(0)=1, \ln(1)=0, \ln(e)=1$).

7. **Unicode Braille & ASCII Graph Plotter**:
   - High-resolution 2D subpixel plotting using Unicode Braille characters ($2 \times 4$ dot resolution per terminal character cell).
   - Multi-curve rendering: $f(x)$, $f'(x)$, $f''(x)$, and tangent lines with distinct colors and legend.
   - Automatic axis drawing, zero-crossing coordinates, and tick annotations.

8. **Interactive Terminal User Interface (TUI)**:
   - Built with [Textual](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/).
   - Live expression evaluation as you type.
   - 5 Dedicated tabs:
     - **Overview**: Formula cards, numerical evaluations, tangent lines, and LaTeX code.
     - **AST Tree**: Interactive syntax tree hierarchy.
     - **Derivation Steps**: Visual breakdown of differentiation rules.
     - **Graph Plot**: Live 2D Braille plot with interactive zoom in/out.
     - **Calculus Analysis**: Critical points, local extrema classification ($f''(x)$ test), real roots (Newton-Raphson), Taylor series approximation, and Simpson's numerical integration.

---

## 📁 Directory Structure

```
all-projects/calculus/antigravity-flash-3.7-calculus/
├── README.md                  # Project documentation & reference
├── report.md                  # Correctness audit & self-repair report
├── app.py                     # Main CLI / TUI entrypoint
├── cli.py                     # Rich CLI interface
├── engine/                    # Core mathematical calculus engine
│   ├── __init__.py            # High-level engine exports
│   ├── ast_nodes.py           # AST Node hierarchy & operator overloads
│   ├── parser.py              # Pratt parser & lexer
│   ├── differentiator.py      # Symbolic differentiation & calculus tools
│   ├── integrator.py          # Symbolic indefinite & definite integration
│   ├── limits.py              # Analytical & perturbation limit solver
│   ├── simplifier.py          # Algebraic reduction & constant folding
│   ├── tracker.py             # Derivation step recorder
│   └── plotter.py             # Unicode Braille 2D terminal plotter
├── tui/                       # Terminal User Interface
│   ├── __init__.py
│   ├── app.py                 # Textual application & layout
│   └── widgets.py             # Overview, Tree, Steps, Plot, Analysis widgets
└── tests/                     # Comprehensive test suite (41 tests)
    ├── __init__.py
    ├── test_ast.py
    ├── test_parser.py
    ├── test_simplifier.py
    ├── test_differentiation.py
    ├── test_integration_and_limits.py
    ├── test_tracker.py
    └── test_plotter.py
```

---

## 🚀 Quick Start

### 1. Launch the Interactive TUI
```bash
python3 app.py
# or
python3 app.py --tui
```

#### TUI Keyboard Shortcuts
- `O`: Switch to **Overview** tab
- `T`: Switch to **AST Tree** tab
- `S`: Switch to **Derivation Steps** tab
- `P`: Switch to **Graph Plot** tab
- `A`: Switch to **Calculus Analysis** tab
- `Ctrl+R`: Recalculate / Refresh
- `Q`: Quit

---

### 2. Command Line Interface (CLI)

#### Basic Differentiation
```bash
python3 app.py "sin(x^2) / (x + 1)" --diff x
```

#### Step-by-Step Derivation & AST Tree
```bash
python3 app.py "sin(x^2) / (x + 1)" --steps --tree
```

#### High-Resolution Unicode Braille Graph
```bash
python3 app.py "x * exp(-x^2)" --plot --xmin -3 --xmax 3
```

#### Complete Calculus Analysis (Roots, Critical Points, Taylor, Tangent)
```bash
python3 app.py "x^3 - 3*x^2 + 2" --critical --roots --taylor 4 --center 1.0 --tangent 2.0 --eval 2.0
```

#### Numerical & Symbolic Integration
```bash
python3 app.py "exp(-x^2)" --integral 0 1
```

---

## 🧪 Test Suite

Run the full pytest suite:
```bash
pytest tests/ -v
```
All 41 unit tests cover AST construction, lexer/parser error handling, operator precedence, algebraic simplification rules, differentiation rules, symbolic integration, limits, step tracking, and terminal graph rendering.
