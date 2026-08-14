# System Architecture & Technical Specifications

This document details the architectural design, algorithmic workflows, data structures, and mathematical subsystems of the Symbolic Calculus & Interactive Terminal Interface Engine.

---

## Architecture Overview

```
                                  ┌───────────────────────────────┐
                                  │   Mathematical Expression     │
                                  │       String Input            │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    Lexer & Token Stream       │
                                  │ (Unicode, Identifiers, Ops)   │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │      Pratt Top-Down           │
                                  │  Operator-Precedence Parser   │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │  Abstract Syntax Tree (AST)   │
                                  │   (Immutable Node Hierarchy)  │
                                  └───────────────┬───────────────┘
                                                  │
            ┌───────────────────┬─────────────────┼─────────────────┬───────────────────┐
            │                   │                 │                 │                   │
            ▼                   ▼                 ▼                 ▼                   ▼
    ┌───────────────┐   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐   ┌───────────────┐
    │  Fixed-Point  │   │   Recursive   │ │   Symbolic    │ │  Multi-Pass   │   │ Unicode/ASCII │
    │  Simplifier   │   │ Differentiator│ │  Integrator   │ │    Limits     │   │ 2D Plotter &  │
    │  & Reducer    │   │ (Step Tracker)│ │  (Quadrature) │ │  (L'Hôpital)  │   │ Tree Renderer │
    └───────┬───────┘   └───────┬───────┘ └───────┬───────┘ └───────┬───────┘   └───────┬───────┘
            │                   │                 │                 │                   │
            └───────────────────┴─────────────────┼─────────────────┴───────────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │  Interactive Terminal UI &    │
                                  │      CLI Command Engine       │
                                  └───────────────────────────────┘
```

---

## 1. Abstract Syntax Tree (AST) Subsystem

### Node Hierarchy
All mathematical expressions are modeled as an immutable tree of `Node` instances:
- **Leaves**:
  - `Constant(value: Union[int, float, Fraction])`: Exact integer, floating point, or rational constants.
  - `NamedConstant(name: str, value: float, latex_name: Optional[str])`: Standard constants like $\pi$, $e$, $\tau$, $\phi$.
  - `Variable(name: str)`: Symbolic identifiers ($x, y, z$).
- **Unary Operators**:
  - `Negate(child: Node)`: Represents unary negation ($-x$).
  - Elementary Functions: `Sin`, `Cos`, `Tan`, `Sec`, `Csc`, `Cot`, `Asin`, `Acos`, `Atan`, `Sinh`, `Cosh`, `Tanh`, `Exp`, `Ln`, `Log`, `Sqrt`, `Abs`.
- **Binary Operators**:
  - `Add(left, right)`, `Subtract(left, right)`, `Multiply(left, right)`, `Divide(left, right)`, `Power(left, right)`.

### Key Interface Methods
Every `Node` subclass implements:
1. `evaluate(env: Optional[Dict[str, float]]) -> float`: Numerical evaluation with variable environment mapping.
2. `differentiate(var: str, tracker: Optional[DerivationTracker]) -> Node`: Computes symbolic derivative $\frac{d}{d\text{var}} \text{Node}$.
3. `to_infix(parent_prec: int) -> str`: Formats human-readable infix expression with minimal parentheses.
4. `to_latex() -> str`: Emits valid LaTeX notation.
5. `to_tree_string() -> str`: Formats box-drawing ASCII/Unicode visual tree.
6. `to_rich_tree(parent) -> Tree`: Constructs a `rich.tree.Tree` for colored terminal visualization.

---

## 2. Pratt Parsing Engine

The parser uses Pratt top-down operator precedence parsing to handle complex mathematical syntax with zero ambiguity:

### Binding Powers & Associativity
| Operator | Binding Power | Associativity | Example |
| :--- | :--- | :--- | :--- |
| `+`, `-` (binary) | `PREC_ADD = 10` | Left | `a - b - c` $\to$ `(a - b) - c` |
| `*`, `/` | `PREC_MUL = 20` | Left | `a / b / c` $\to$ `(a / b) / c` |
| Implicit `*` | `PREC_IMPLICIT_MUL = 25` | Left | `2x^2` $\to$ `2 * (x^2)` |
| `-` (unary prefix) | `PREC_PREFIX = 30` | Right | `-x^2` $\to$ `-(x^2)` |
| `^`, `**` | `PREC_POWER = 40` | Right | `2^3^2` $\to$ `2^(3^2) = 512` |

### Special Parsing Handlers
- **Implicit Multiplication**: Inserts multiplication nodes between adjacent tokens when applicable (`Number Var`, `Number (`, `) (`, `) Var`, `Var Var`).
- **Unicode Superscripts**: Automatically maps superscripts (`x²`, `x³`, `x⁻¹`) into standard `Power` nodes.
- **Parenthesis-Free Functions**: Allows calling elementary functions without brackets (`sin x`, `cos 3x`).
- **Absolute Value Enclosures**: Parses `|expr|` into `Abs(expr)`.

---

## 3. Fixed-Point Algebraic Simplification

The simplifier applies recursive bottom-up rewrites until reaching a fixed point:
$$f_{k+1} = \text{simplify\_pass}(f_k), \quad \text{stopping when } f_{k+1} \equiv f_k$$

### Rule Reductions
1. **Constant Folding**: Exact arithmetic on rational numbers using Python `Fraction` to avoid floating-point drift:
   $$\frac{1}{2} + \frac{1}{3} \to \frac{5}{6}$$
2. **Identity Annihilation**:
   $$x + 0 \to x, \quad x \cdot 1 \to x, \quad x \cdot 0 \to 0, \quad x - x \to 0, \quad x / x \to 1$$
3. **Power Laws**:
   $$x^0 \to 1, \quad x^1 \to x, \quad x^a \cdot x^b \to x^{a+b}, \quad \frac{x^a}{x^b} \to x^{a-b}, \quad (x^a)^b \to x^{ab}$$
4. **Like-Terms Combining**:
   $$c_1 x + c_2 x \to (c_1 + c_2) x$$
5. **Transcendental Reductions**:
   $$\sin(0) = 0, \quad \cos(0) = 1, \quad \tan(0) = 0, \quad \ln(1) = 0, \quad \ln(e^x) = x, \quad e^{\ln(x)} = x$$

---

## 4. Symbolic Differentiation & Multivariable Calculus

### Differentiation Rules
- **Power Rule**: $\frac{d}{dx}[u^v] = u^v \left( v' \ln(u) + \frac{v u'}{u} \right)$
- **Product Rule**: $\frac{d}{dx}[u \cdot v] = u' v + u v'$
- **Quotient Rule**: $\frac{d}{dx}\left[\frac{u}{v}\right] = \frac{u' v - u v'}{v^2}$
- **Chain Rule**: $\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$

### Multivariable Calculus
- **Gradient**: $\nabla f = \left[ \frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \dots, \frac{\partial f}{\partial x_n} \right]^T$
- **Hessian Matrix**: $H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$
- **Taylor Polynomial**: $P_n(x) = \sum_{k=0}^n \frac{f^{(k)}(x_0)}{k!} (x - x_0)^k$

---

## 5. Integration Engine

1. **Symbolic Antiderivatives**:
   - Polynomial terms: $\int x^n dx = \frac{x^{n+1}}{n+1}$ ($n \neq -1$), $\int \frac{1}{x} dx = \ln|x|$
   - Exponential terms: $\int e^{ax+b} dx = \frac{1}{a} e^{ax+b}$
   - Trigonometric terms: $\int \sin(ax+b) dx = -\frac{1}{a}\cos(ax+b)$, $\int \cos(ax+b) dx = \frac{1}{a}\sin(ax+b)$
   - Integration by parts: $\int x e^{ax} dx = \frac{ax - 1}{a^2} e^{ax}$, $\int x \sin(x) dx = \sin(x) - x\cos(x)$, $\int x^n \ln(x) dx = \frac{x^{n+1}}{n+1}\ln(x) - \frac{x^{n+1}}{(n+1)^2}$
2. **Definite Integration**:
   - Analytical: By the Fundamental Theorem of Calculus $I = F(b) - F(a)$.
   - Numerical Quadrature: High-precision Adaptive Simpson's Rule with automatic tolerance subdivision.

---

## 6. Limits Engine

Calculates $\lim_{x \to a} f(x)$ via a 4-tier pipeline:
1. **Direct Substitution**: If $f(a)$ is defined and finite, return $f(a)$.
2. **L'Hôpital's Rule**: For indeterminate forms $\frac{0}{0}$ or $\frac{\infty}{\infty}$, iteratively computes:
   $$\lim_{x \to a} \frac{u(x)}{v(x)} = \lim_{x \to a} \frac{u'(x)}{v'(x)}$$
3. **Richardson Perturbation Sampling**: Evaluates symmetric perturbations $f(a \pm \epsilon)$ across $\epsilon \in \{10^{-4}, 10^{-5}, 10^{-6}, 10^{-7}, 10^{-8}\}$.
4. **Infinite Limits**: Evaluates $x \to \pm\infty$ using asymptotic sequences.

---

## 7. Unicode Braille 2D Canvas Plotting

The terminal plotter achieves $2 \times 4$ subpixel resolution per character cell using the Unicode Braille Patterns block (`U+2800` through `U+28FF`).

### Braille Bitmask Layout
Each character cell contains 8 subpixel dots mapped to the bitmask:
```
  [0, 0] (0x01)   [0, 1] (0x08)
  [1, 0] (0x02)   [1, 1] (0x10)
  [2, 0] (0x04)   [2, 1] (0x20)
  [3, 0] (0x40)   [3, 1] (0x80)
```
Unicode character computation:
$$\text{char\_code} = \text{0x2800} + \sum \text{bitmasks}$$

Line segments between consecutive sample points are rendered using Bresenham's line algorithm on the subpixel grid.
