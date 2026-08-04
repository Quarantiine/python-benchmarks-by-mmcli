# Internal Architecture & Design of the MMCLI Calculus Engine

Welcome to the internal architectural documentation for the **MMCLI Calculus Engine**. This document provides a comprehensive breakdown of how the symbolic calculus system works under the hood, detailing its Abstract Syntax Tree (AST), Lexer & Parser, Differentiation & Simplification Rules, and the Terminal User Interface (TUI) / Command-Line Interface (CLI).

---

## System Architecture Overview

The calculus engine is designed as a modular, recursive symbolic math processing pipeline in Python with zero external dependencies (relying entirely on Python's standard library).

```
  ┌───────────────┐      Lexer      ┌─────────────┐     Parser      ┌──────────────┐
  │ Expression    │ ──────────────> │ Tokens      │ <─────────────> │ AST          │
  │ String        │                 │ Stream      │                 │ (Nodes)      │
  └───────────────┘                 └─────────────┘                 └──────────────┘
                                                                           │
                                           ┌───────────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             ┌─────────────────────┐               ┌─────────────────────┐
             │ Calculus Engine     │               │ Evaluation & TUI    │
             │ - differentiate()   │               │ - evaluate()        │
             │ - simplify()        │               │ - render_tree()     │
             └─────────────────────┘               │ - interactive mode  │
                                                   └─────────────────────┘
```

---

## 1. Abstract Syntax Tree (AST) (`ast_nodes.py`)

At the heart of the system is the `Node` abstract base class. Every mathematical expression is represented as an immutable or cloneable tree of nodes.

### Core Interface (`Node`)

Every AST node implements the following contract:

- `evaluate(env: Dict[str, float]) -> float`: Recursively computes the numerical value of the expression given variable assignments (e.g., `{'x': 2.0}`).
- `__str__() -> str`: Returns a standard mathematical string representation.
- `get_variables() -> Set[str]`: Gathers all unique variable names present anywhere in the sub-tree.
- `clone() -> Node`: Deep-copies the node and all its descendants.
- Operator Overloads (`__add__`, `__mul__`, `__pow__`, etc.): Enables Pythonic expression construction like `node1 + node2` or `x * 2`.

### Node Hierarchy

1. **Terminals**:
   - `Number(value)`: Represents floating-point or integer constants.
   - `Variable(name)`: Represents symbolic identifiers (`x`, `y`, `t`, etc.).
2. **Binary Operators (`BinaryOp`)**:
   - `Add` (`+`), `Subtract` (`-`), `Multiply` (`*`), `Divide` (`/`), `Power` (`^` or `**`).
3. **Unary Operators (`UnaryOp`)**:
   - `Negate` (`-x`)
   - **Trigonometric Functions**: `Sin`, `Cos`, `Tan`, `Asin`, `Acos`, `Atan`.
   - **Exponential & Logarithmic Functions**: `Exp`, `Log` (natural log).
   - **Radicals**: `Sqrt`.

---

## 2. Lexical Analysis & Recursive Descent Parser (`parser.py`)

Converting a human-readable string into an AST involves a two-stage compilation pipeline: **Lexer** and **Parser**.

### A. Lexer (`Lexer`)

Scans the raw input string character-by-character and produces a stream of `Token` objects (`Token(type, value, position)`).

- Handles multi-character tokens such as floats (`3.14`), scientific notation (`1.5e-10`), and identifiers (`sin`, `cos`, `log`, `sqrt`, `pi`, `e`, `x`).
- Automatically recognizes implicit multiplication contexts (e.g., transforming `2x` into `2 * x` or `3sin(x)` into `3 * sin(x)`).

### B. Parser (`Parser`)

A Pratt-style or recursive descent parser implementing standard mathematical operator precedence (from lowest to highest):

1. **Addition / Subtraction (`+`, `-`)**
2. **Multiplication / Division (`*`, `/`)**
3. **Unary Operators & Negation (`-`, `sin`, `cos`, etc.)**
4. **Exponentiation (`^`, `**`) (Right-associative)\*\*
5. **Parentheses & Function Calls (`(...)`)**

Supports built-in mathematical constants:

- `pi` $\approx 3.14159...$
- `e` $\approx 2.71828...$

---

## 3. Calculus Engine (`engine.py`)

The calculus engine performs two major symbolic transformations: **Differentiation** and **Algebraic Simplification**.

### A. Symbolic Differentiation (`differentiate(node, var)`)

Computes exact symbolic derivatives recursively using fundamental calculus rules:

- **Constant Rule**: $\frac{d}{dx}(C) = 0$
- **Variable Rule**: $\frac{d}{dx}(x) = 1$ (if variable matches), else $0$.
- **Sum & Difference Rule**: $\frac{d}{dx}(f \pm g) = f' \pm g'$
- **Product Rule**: $\frac{d}{dx}(f \cdot g) = f'g + fg'$
- **Quotient Rule**: $\frac{d}{dx}\left(\frac{f}{g}\right) = \frac{f'g - fg'}{g^2}$
- **Chain Rule & Power Rule**:
  - Handles variable bases, variable exponents, and general function compositions.
- **Transcendental Rules**:
  - $\frac{d}{dx}(\sin f) = \cos f \cdot f'$
  - $\frac{d}{dx}(\cos f) = -\sin f \cdot f'$
  - $\frac{d}{dx}(\tan f) = \sec^2 f \cdot f'$
  - $\frac{d}{dx}(\ln f) = \frac{1}{f} \cdot f'$
  - $\frac{d}{dx}(e^f) = e^f \cdot f'$
  - $\frac{d}{dx}(\sqrt{f}) = \frac{1}{2\sqrt{f}} \cdot f'$
  - Inverse trigonometric derivatives (`asin`, `acos`, `atan`).

### B. Algebraic Simplification & Constant Folding (`simplify(node)`)

Raw derivatives often produce verbose expressions (e.g., `(1 * x + x * 0) + 0`). The `simplify` function runs multi-pass reduction (up to 15 convergence iterations) applying:

- **Constant Folding**: Computes arithmetic operations on literal numbers at compile time (`2 + 3` $\to$ `5`).
- **Zero & Identity Laws**:
  - $0 + x \to x$, $x + 0 \to x$
  - $1 \cdot x \to x$, $0 \cdot x \to 0$
  - $x^0 \to 1$, $x^1 \to x$, $0^x \to 0$ ($x > 0$)
- **Cancellation & Inverse Rules**:
  - Double negation elimination (`--x` $\to$ `x`)
  - Log-exp identities (`ln(e^x)` $\to$ `x`, $e^{\ln x}$ $\to$ `x`)
  - Square root folding ($\sqrt{x^2}$ $\to$ $x$)
- **Like-Term Combining**:
  - Automatically combines linear terms ($2x + 3x \to 5x$).
- **Trig Evaluation at Standard Angles**:
  - Evaluates $\sin(0)$, $\cos(\pi/2)$, $\arctan(1)$, etc., into exact numerical constants.

---

## 4. Terminal User Interface & CLI (`tui.py`, `cli.py`)

### A. Tree Renderer (`render_tree`)

Visually renders the AST as an ASCII/Unicode hierarchical tree structure, allowing developers and users to inspect the syntax tree structure directly in the terminal.

### B. Step-by-Step Derivations (`render_derivation_steps`)

Breaks down differentiation into clear intermediate steps:

1. Original expression
2. Unsimplified derivative
3. Simplified final derivative

### C. Interactive TUI & CLI Dispatcher (`cli.py`, `run_tui()`)

Provides a rich command-line interface supporting commands:

- `diff <expr> [--var x]`: Differentiate an expression.
- `simplify <expr>`: Simplify an expression.
- `eval <expr> [var=val...]`: Evaluate an expression numerically.
- `tree <expr>`: Render the AST structure.
- `tui`: Launch the interactive terminal user interface.

---

## Testing & Verification

The test suite in `tests/` uses `pytest` to validate AST correctness, parsing edge cases, derivative accuracy across all supported functions, and complex simplification rules.

Run tests via:

```bash
pytest
```
