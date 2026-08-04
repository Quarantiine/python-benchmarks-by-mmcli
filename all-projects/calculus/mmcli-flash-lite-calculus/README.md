# Symbolic Calculus Engine, CLI, and TUI

A lightweight, robust pure-Python symbolic calculus engine featuring an Abstract Syntax Tree (AST) parser, recursive algebraic differentiation rules, constant folding and algebraic simplification, ASCII/Unicode equation tree rendering, step-by-step derivation breakdowns, numerical evaluation, an interactive Terminal User Interface (TUI), and a powerful Command Line Interface (CLI).

---

## Features

- **Robust AST Parser**: Supports standard operators (`+`, `-`, `*`, `/`, `^`, `**`, unary `-`), parentheses, implicit multiplication (e.g. `2x`, `3sin(x)`), mathematical constants (`pi`, `e`), and functions (`sin`, `cos`, `tan`, `log`, `ln`, `exp`, `sqrt`, `asin`, `acos`, `atan`).
- **Symbolic Differentiation**: Implements the Power rule, Product rule, Quotient rule, Chain rule, Sum/Difference rule, and complete trigonometric, logarithmic, and exponential differentiation rules.
- **Algebraic Simplification**: Performs constant folding, zero/identity eliminations, power folding, log/exp cancellation identities, double negation elimination, and like-term combination.
- **Equation Tree Rendering**: Renders hierarchical Abstract Syntax Trees in clean ASCII/Unicode box-drawing format.
- **Step-by-Step Derivations**: Breaks down differentiation operations into clear, readable step-by-step transformations.
- **Interactive TUI & CLI**: Offers both a command-line utility for shell scripts and an interactive TUI menu for real-time mathematical exploration.

---

## Project Structure

```
mmcli-[some model]-calculus/
├── __init__.py      # Package exports (AST nodes, parser, engine, tui)
├── ast_nodes.py     # Abstract Syntax Tree definitions & evaluation
├── parser.py        # Lexer, Tokenizer, and Recursive Descent Parser
├── engine.py        # Symbolic differentiation & algebraic simplification rules
├── tui.py           # Equation tree rendering, steps, evaluation, & interactive TUI
└── cli.py           # Command-line interface dispatcher
```

---

## Installation & Execution

Ensure you have Python 3 (Python 3.8 or higher) installed on your system. Note that on macOS and many modern Linux/Unix environments, the Python interpreter is invoked via `python3` rather than `python`.

1. Navigate to the project root or package directory:

   ```bash
   cd all-projects/calculus/mmcli-[some model]-calculus
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in editable mode or include it in your Python path:
   ```bash
   pip install -e .
   ```
   _(Alternatively, you can run scripts directly by setting `PYTHONPATH=.` or executing the root `main.py` entry point)_

---

## Using the Python API

You can import the calculus engine directly into your Python scripts or Jupyter notebooks:

```python
from calculus import parse_expression, differentiate, simplify, evaluate_expression

# 1. Parse an expression string into an AST
expr_str = "x^3 + 2*sin(x) - ln(x)"
ast = parse_expression(expr_str)
print(f"Parsed AST: {ast}")

# 2. Differentiate with respect to 'x'
deriv = differentiate(ast, var='x')
print(f"Derivative: {deriv}")

# 3. Simplify the derivative
simplified_deriv = simplify(deriv)
print(f"Simplified Derivative: {simplified_deriv}")

# 4. Evaluate numerically at x = 2.0 (with pi/e support)
val = evaluate_expression(ast, {'x': 2.0})
print(f"Evaluated at x=2.0: {val}")
```

### Supported Mathematical Functions & Operators

- **Operators**: `+`, `-`, `*`, `/`, `^`, `**` (power)
- **Functions**: `sin`, `cos`, `tan`, `log` (or `ln`), `exp`, `sqrt`, `asin`, `acos`, `atan`
- **Constants**: `pi`, `e`

---

## Using the Command Line Interface (CLI) & Entry Points

The package provides a `calculus` command-line utility with multiple subcommands. You can run them using `python3` (or via the project root wrapper `main.py`).

### Running via Root `main.py` (Recommended from project root)

From the `python-practice` repository root, you can run interactive TUI or CLI commands directly:

```bash
# Launch interactive TUI
python3 main.py

# Differentiate an expression
python3 main.py diff "x^3 + sin(x)" -v x

# Definite / indefinite integral approximation
python3 main.py int "x^2" -l 0 -u 2

# Limit evaluation
python3 main.py lim "sin(x)/x" -p 0

# Simplify an expression
python3 main.py simplify "x + x + 0"

# Evaluate expression with variables
python3 main.py eval "x^2 + y" x=3 y=4

# Render AST tree
python3 main.py tree "sin(2*x)"
```

### Running via Package Module (`python3 -m calculus.cli`)

If you have installed the package or set your `PYTHONPATH`:

### 1. Differentiate (`diff`)

Compute the derivative of an expression with respect to a variable.

```bash
python3 -m calculus.cli diff "x^3 * sin(x)" --var x
```

### 2. Simplify (`simplify` or `simp`)

Simplify an algebraic expression.

```bash
python3 -m calculus.cli simplify "2*x + 3*x + 5 - 2"
```

### 3. Evaluate (`eval`)

Evaluate an expression numerically at given variable values.

```bash
python3 -m calculus.cli eval "x^2 + sin(x)" --vars x=1.57079632679
```

### 4. Tree Rendering (`tree`)

Display the hierarchical AST structure of an expression.

```bash
python3 -m calculus.cli tree "x^2 + 3*x + 2"
```

### 5. Step-by-Step Derivation (`steps`)

View the derivation breakdown.

```bash
python3 -m calculus.cli steps "x^3 * cos(x)" --var x
```

### 6. Interactive TUI Mode (`tui`)

Launch the interactive Terminal User Interface:

```bash
python3 -m calculus.cli tui
```

---

## Interactive TUI Guide

When you run `python3 main.py` or `python3 -m calculus.cli tui`, you are greeted with an interactive menu:

```
============================================================
           SYMBOLIC CALCULUS ENGINE - TUI MODE
============================================================
[1] Parse & Evaluate Expression
[2] Differentiate Expression
[3] Simplify Expression
[4] View Equation Tree (AST)
[5] View Step-by-Step Derivation
[6] Exit
------------------------------------------------------------
```

- Enter your choice (`1`-`6`) and follow the prompts to enter mathematical expressions and variable values in real-time.

---

## Running Tests

To run the unit test suite (from the repository root):

```bash
pytest tests/
```
