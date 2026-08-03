# Calculus TUI

An interactive terminal application built in Python for parsing, visualizing, differentiating, and graphing mathematical expressions in real time.

## Prerequisites

Ensure you have installed the required dependencies from the project root:

```bash
pip install -r requirements.txt
```

_(Specifically requires `textual` and `plotext`)_

## How to Run

From the workspace root directory:

```bash
# Direct execution via Python
python3 all-projects/calculus/antigravity-gemini-pro-calculus/__main__.py
```

Or navigate to the subproject directory directly:

```bash
cd all-projects/calculus/antigravity-gemini-pro-calculus
python3 __main__.py
```

> **Important Note on `PYTHONPATH`:**
> Do NOT set `PYTHONPATH=all-projects/calculus/antigravity-gemini-pro-calculus` or `PYTHONPATH=all-projects/calculus`. Doing so causes the local `ast.py` file to shadow Python's standard library `ast` module, breaking dependencies like `textual` and `rich`. Run the script directly via `__main__.py` as shown above.

## How to Use the Interface

1. **Input Field**: Once the interface opens, type a mathematical expression in the top input bar and press `Enter`.
2. **Supported Syntax**:
   - Variables: `x`, `y`
   - Numbers: Integers (`42`) and decimals (`3.14`)
   - Operators: `+`, `-`, `*`, `/`, `^`
   - Functions: `sin(x)`, `cos(x)`
   - Parentheses: `(x + 2) * 3`
3. **AST Visualizer Pane**: Automatically builds and displays a directory-tree representation of how the engine interpreted your math.
4. **Derivation Steps Pane**: Displays:
   - Your original parsed expression.
   - The raw, unsimplified derivative applying the Product, Chain, or Quotient rules.
   - The final, algebraically simplified derivative.
5. **Graph Pane**: Displays an ASCII plot of your original expression ranging from `x = -10` to `x = 10`.

**Examples to try**:

- `x^2 * sin(x)`
- `cos(x) / (x + 1)`
- `(x - 5)^3`

Press `q` at any time to quit the application.
