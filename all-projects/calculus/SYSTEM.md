# Symbolic Calculus Engine — System Architecture & Mechanics

This document provides a comprehensive technical overview of the architecture, algorithms, and data structures powering the **Symbolic Calculus Engine**. The library is designed as a modular, pure-Python symbolic computation system that handles expression parsing, AST transformation, algebraic simplification, differentiation, integration, limits, multi-format rendering, and step-by-step reasoning.

---

## 1. Architectural Topology & Component Overview

The engine follows a functional, pipeline-oriented compiler architecture:

```
[ Input String ] ──► Tokenizer & Parser ──► [ AST Representation ]
                                                  │
             ┌────────────────────────────────────┼────────────────────────────────────┐
             ▼                                    ▼                                    ▼
   [ Simplification ]                  [ Differentiation ]                    [ Integration ]
             │                                    │                                    │
             ├────────────────────────────────────┼────────────────────────────────────┘
             ▼                                    ▼
     [ Limits Engine ]                    [ Rendering Pipeline ]
                                       (LaTeX, Unicode, ASCII Tree)
```

### Core Subsystems & File Layout

| Module         | Responsibility                                                                        | Key Abstractions & Functions                                            |
| :------------- | :------------------------------------------------------------------------------------ | :---------------------------------------------------------------------- |
| `ast.py`       | Symbolic Abstract Syntax Tree (AST) node definitions                                  | `Expr`, `Const`, `Symbol`, `BinaryOp`, `UnaryOp`, `Function`            |
| `parser.py`    | Regex lexer with implicit multiplication & precedence-climbing parser                 | `tokenize()`, `Parser`, `parse()`                                       |
| `simplify.py`  | Rule-based algebraic, trigonometric, and exponent simplifier                          | `simplify()`, `_simplify_step()`, `_extract_coef_term()`                |
| `diff.py`      | Exact symbolic differentiation engine (Chain Rule, Product Rule, Quotient Rule)       | `diff()`, `_differentiate()`                                            |
| `integrate.py` | Indefinite and definite integration (Substitution, Integration by Parts)              | `integrate()`, `_integrate_indefinite()`, `_try_integration_by_parts()` |
| `limits.py`    | Symbolic limit solver (Substitution, Cancellation, L'Hôpital's Rule, Infinity limits) | `limit()`, `_try_eval_at()`, `_numeric_limit_probe()`                   |
| `render.py`    | Multi-target math formatting (LaTeX, Unicode notation, ASCII tree structures)         | `to_latex()`, `render_pretty()`, `render_tree()`                        |
| `tui.py`       | Interactive Curses TUI and step-by-step explanation engine                            | `SymbolicCalculusTUI`, `StepByStepEngine`, `run_curses_tui()`           |
| `cli.py`       | Command-line interface parser and formatter                                           | `create_parser()`, `run_cli()`                                          |

---

## 2. Abstract Syntax Tree (AST) Domain Model (`ast.py`)

All symbolic expressions in the system are represented as immutable nodes inheriting from the `Expr` abstract base class.

```
                            Expr (ABC)
                             │
     ┌───────────────────────┼───────────────────────┬──────────────────────┐
     │                       │                       │                      │
   Const                  Symbol                  BinaryOp               UnaryOp / Function
 (int/float)           ("x", "pi", "e")        (Add, Sub, Mul,        (Neg, Sin, Cos, Tan,
                                               Div, Pow)              Exp, Ln, Sqrt, Abs)
```

### Core Contract of `Expr`

Every AST node implements three fundamental polymorphic methods:

1. `eval(var_dict: Dict[str, float]) -> float`: Recursively evaluates the expression given variable assignments.
2. `free_symbols() -> Set[str]`: Returns the set of all variable names present in the AST.
3. `subs(var: str, value: Union[float, Expr]) -> Expr`: Substitutes a variable with a numeric value or another sub-AST.

### Operator Overloading

`Expr` overrides standard Python numeric dunder methods (`__add__`, `__sub__`, `__mul__`, `__truediv__`, `__pow__`, `__neg__`, and their right-hand `__r*__` variants). This allows native Python expressions to automatically build AST instances:

```python
x = Symbol("x")
expr = x**2 + 2*x + 1  # Constructs Add(Add(Pow(x, Const(2)), Mul(Const(2), x)), Const(1))
```

---

## 3. Lexer & Parser Architecture (`parser.py`)

The parsing pipeline converts mathematical text strings into validated symbolic ASTs through a two-stage lexing and parsing pipeline.

### 3.1 Lexical Analysis & Implicit Multiplication Logic

`tokenize(expr_str: str)` uses regular expressions to match tokens (`NUMBER`, `IDENT`, `PLUS`, `MINUS`, `MUL`, `DIV`, `POW`, `LPAREN`, `RPAREN`, `COMMA`).

#### Implicit Multiplication Injection:

To allow user-friendly syntax like `2x`, `3(x+1)`, or `x sin(x)`, the tokenizer injects explicit `MUL` (`*`) tokens whenever:

- A `NUMBER` or `RPAREN` is immediately followed by an `IDENT`, `NUMBER`, or `LPAREN`.
- An `IDENT` (that is **not** a recognized function name like `sin`, `cos`, `ln`, `exp`) is followed by an `IDENT`, `NUMBER`, or `LPAREN`.

### 3.2 Precedence-Climbing Parser

The parser (`Parser`) utilizes precedence climbing to correctly construct operator trees according to standard mathematical order of operations:

| Operator Category  | Precedence | Associativity     | AST Node                                        |
| :----------------- | :--------- | :---------------- | :---------------------------------------------- |
| `+`, `-`           | 1          | Left-associative  | `Add`, `Sub`                                    |
| `*`, `/`           | 2          | Left-associative  | `Mul`, `Div`                                    |
| Unary `-`, `+`     | 3          | Right-associative | `Neg`                                           |
| `^`, `**`          | 4          | Right-associative | `Pow`                                           |
| Functions / Parens | Highest    | Non-associative   | `Sin`, `Cos`, `Tan`, `Exp`, `Ln`, `Sqrt`, `Abs` |

---

## 4. Symbolic Simplification Engine (`simplify.py`)

Simplification runs iteratively until a fixpoint is achieved (`expr == simplified_expr`) or `max_passes` (default: 10) is reached.

### Key Simplification Rules Applied in `_simplify_step`

1. **Constant Folding:** Direct computation of numerical sub-expressions (e.g., `Add(Const(2), Const(3))` $\rightarrow$ `Const(5)`).
2. **Neutral & Annihilating Elements:**
   - $x + 0 \rightarrow x$, $0 + x \rightarrow x$
   - $x \cdot 0 \rightarrow 0$, $x \cdot 1 \rightarrow x$
   - $x^0 \rightarrow 1$, $x^1 \rightarrow x$, $0^x \rightarrow 0$, $1^x \rightarrow 1$
   - $0 / x \rightarrow 0$
3. **Double Negation & Inversion:**
   - $-(-x) \rightarrow x$
   - $\ln(e^x) \rightarrow x$, $e^{\ln(x)} \rightarrow x$
   - $\sqrt{x^2} \rightarrow |x|$
4. **Like-Term Combination:**
   - Uses `_extract_coef_term()` to combine linear multiples: $c_1 x + c_2 x \rightarrow (c_1 + c_2) x$.
5. **Exponent Combination:**
   - Uses `_extract_base_exp()` to combine identical bases: $x^a \cdot x^b \rightarrow x^{a+b}$.

---

## 5. Symbolic Differentiation Engine (`diff.py`)

Differentiation is performed via recursive AST traversal in `_differentiate(expr, var)` using exact analytic calculus rules:

### Operational Differentiation Rules

- **Sum / Difference Rule:**
  $$\frac{d}{dx}(u \pm v) = \frac{du}{dx} \pm \frac{dv}{dx}$$
- **Product Rule:**
  $$\frac{d}{dx}(u \cdot v) = \frac{du}{dx} \cdot v + u \cdot \frac{dv}{dx}$$
- **Quotient Rule:**
  $$\frac{d}{dx}\left(\frac{u}{v}\right) = \frac{\frac{du}{dx} \cdot v - u \cdot \frac{dv}{dx}}{v^2}$$
- **Power Rule & Generalized Exponential Rule:**
  - Standard power: $\frac{d}{dx}(x^n) = n x^{n-1} \cdot \frac{dx}{dx}$
  - Variable exponent ($u^v$): $\frac{d}{dx}(u^v) = u^v \left( \frac{dv}{dx} \ln(u) + \frac{v}{u} \frac{du}{dx} \right)$
- **Chain Rule for Elementary Functions:**
  - $\frac{d}{dx}\sin(u) = \cos(u) \cdot u'$
  - $\frac{d}{dx}\cos(u) = -\sin(u) \cdot u'$
  - $\frac{d}{dx}\tan(u) = (1 + \tan^2(u)) \cdot u'$
  - $\frac{d}{dx}e^u = e^u \cdot u'$
  - $\frac{d}{dx}\ln(u) = \frac{u'}{u}$
  - $\frac{d}{dx}\sqrt{u} = \frac{u'}{2\sqrt{u}}$

---

## 6. Symbolic Integration Engine (`integrate.py`)

The integration engine (`integrate`) handles both indefinite ($\int f(x) \, dx$) and definite ($\int_a^b f(x) \, dx$) integrals.

### 6.1 Pattern Matching Hierarchy for Indefinite Integrals

1. **Linearity of Integration:**
   $$\int (u(x) \pm v(x)) \, dx = \int u(x) \, dx \pm \int v(x) \, dx$$
2. **Polynomial Power Rule:**
   $$\int x^n \, dx = \begin{cases} \ln|x| & \text{if } n = -1 \\ \frac{x^{n+1}}{n+1} & \text{if } n \neq -1 \end{cases}$$
3. **Linear Substitution Detection (`_extract_coefs`):**
   Matches composite functions of the form $f(a x + b)$ and applies scaling $\frac{1}{a} F(a x + b)$.
4. **Integration by Parts Fallback (`_try_integration_by_parts`):**
   Applies $\int u \, dv = u v - \int v \, du$ for products like $x e^x$, $x \sin(x)$, or $x \cos(x)$.

### 6.2 Definite Integration

Definite integrals apply the **Fundamental Theorem of Calculus**:
$$\int_a^b f(x) \, dx = F(b) - F(a)$$
where $F(x)$ is the symbolic anti-derivative.

---

## 7. Symbolic Limits Engine (`limits.py`)

The `limit(expr, var, point, direction)` engine evaluates analytical limits using a multi-tiered heuristic strategy:

```
[ Input: lim_{x -> x0} f(x) ]
              │
              ▼
    1. Direct Evaluation (Is f(x0) well-defined?)
      ├── Yes ──► Return f(x0)
      └── No  ──► Indeterminate / Undefined
              │
              ▼
    2. Algebraic Cancellation / Factor Reduction
              │
              ▼
    3. L'Hôpital's Rule (If form is 0/0 or ∞/∞)
       Apply lim_{x -> x0} f'(x) / g'(x)
              │
              ▼
    4. Limits at Infinity (Polynomial degree comparison)
              │
              ▼
    5. Numeric Epsilon Probing Fallback (_numeric_limit_probe)
```

### Infinity Limit Mechanics (`_limit_at_infinity`)

When $x \to \infty$ or $x \to -\infty$ for rational expressions $\frac{P(x)}{Q(x)}$:

- $\text{deg}(P) < \text{deg}(Q) \implies 0$
- $\text{deg}(P) == \text{deg}(Q) \implies \frac{\text{leading\_coeff}(P)}{\text{leading\_coeff}(Q)}$
- $\text{deg}(P) > \text{deg}(Q) \implies \pm\infty$

---

## 8. Rendering & Visual Formatting Pipeline (`render.py`)

The engine provides three rendering targets:

1. **LaTeX Generator (`to_latex`):**
   Produces standard LaTeX syntax suitable for document compilation or MathJax rendering (e.g., `\frac{d}{dx}`, `\int_{a}^{b}`, `\sin\left(x\right)`).
2. **Unicode Math Formatter (`render_pretty`):**
   Renders expressions using superscript numerals and mathematical unicode operators (e.g., `x³ + 2x² - 1`).
3. **ASCII AST Tree Visualizer (`render_tree`):**
   Displays the structural hierarchy of AST nodes as an ASCII tree diagram:
   ```
   Add
   ├── Mul
   │   ├── Const(2)
   │   └── Symbol(x)
   └── Const(1)
   ```

---

## 9. Interactive TUI & Step-by-Step Reasoning (`tui.py`, `cli.py`)

### Step-by-Step Reasoning Engine (`StepByStepEngine`)

Provides pedagogical step breakdowns for operations:

- Records transformation steps (Initial AST $\rightarrow$ Rule applied $\rightarrow$ Intermediate AST $\rightarrow$ Final Simplified Result).
- Generates natural language explanations suitable for visual UI modals or CLI study displays.

### Dual Interface Layer

- **Curses Terminal UI (`run_curses_tui`):** Full interactive modal navigation, live string parsing preview, AST visualization, and operational tab switching.
- **CLI Subcommand Wrapper (`cli.py`):** Structured command-line tool supporting subcommands (`diff`, `int`, `lim`, `simplify`, `eval`, `tree`) with formatting flags (`--format`, `--steps`, `--verbose`).
