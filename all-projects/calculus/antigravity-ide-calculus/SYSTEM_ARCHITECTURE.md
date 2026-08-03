# System Architecture

> Antigravity IDE, using Gemini 3.1 Pro, Revised it's code (3) times after my first try using this Calculus TUI

> Verdict: Partially working on first try

---

# Agent documentation it wrote below:

The Calculus TUI project is built across three primary layers: **Parsing**, **The Abstract Syntax Tree (AST)**, and the **Terminal User Interface (TUI)**.

## 1. The Parser (`parser.py`)

When a user types a string like `x^2 * sin(x)`, the string must be converted into a machine-readable format. This is handled by a standard computer science technique called a **Recursive Descent Parser**.

- **Tokenizer**: Before parsing, a regex-based tokenizer slices the raw string into distinct tokens: `VAR("x")`, `OP("^")`, `NUMBER("2")`, `OP("*")`, `FUNC("sin")`, `OP("(")`, `VAR("x")`, `OP(")")`.
- **Grammar & Descent**: The parser relies on mathematical precedence rules (PEMDAS). It contains mutually recursive functions (`expr()`, `term()`, `factor()`, `base()`).
  - To parse addition (`expr()`), it first looks for multiplication (`term()`).
  - To parse multiplication, it first looks for exponents (`factor()`).
  - To parse exponents, it looks for numbers, variables, or parenthesis (`base()`).
- The parser outputs the root object of an Abstract Syntax Tree (AST).

## 2. The Core Engine & AST (`ast.py`)

An AST represents a mathematical expression as a tree structure. Each operation and operand is an individual `Node` object.

For example, `x * sin(x)` is represented as:

```text
      MulNode
      /     \
  VarNode   SinNode
    (x)        |
            VarNode
              (x)
```

The true power of this system is how these nodes interact through **recursive algorithms**:

### Differentiation (`.differentiate()`)

Every specific node subclass knows how to differentiate itself based on standard calculus rules.

- `VarNode("x").differentiate("x")` simply returns `ConstNode(1)`.
- `MulNode(left, right).differentiate("x")` executes the **Product Rule** recursively: `(u'v + uv')`. It constructs a new `AddNode` containing two new `MulNodes`, recursively calling `.differentiate("x")` on its left and right children.

### Simplification (`.simplify()`)

The raw derivative of `x^2` evaluates mathematically to `(2 * x^1) * 1 + x^2 * 0`. To make this readable, the system recursively visits nodes from the bottom-up:

- `MulNode` checks if either child is a `ConstNode(0)` and, if so, collapses into just `ConstNode(0)`.
- `AddNode` drops any child that is exactly `ConstNode(0)`.
- This efficiently reduces the messy derivative down to `2 * x`.

### Evaluation (`.evaluate(env)`)

For graph plotting, `.evaluate({"x": 5})` acts like a calculator. A `MulNode` simply takes the `evaluate()` of its left child and multiplies it by the `evaluate()` of its right child, bubbling the numerical answer all the way to the top.

## 3. The Interface Layer (`__main__.py`)

Instead of a basic CLI that prints out text, we use **Textual** and **Plotext** to create an event-driven interface.

- **Textual framework**: Provides a DOM-like CSS grid where we define panes for the visualizer, step-by-step logic, and a graph.
- **Rich Tree Generation**: The AST provides a `.to_tree()` method. When the expression is parsed, Textual renders this structure visually in the left pane using color-coded folders.
- **Step Tracing**: We intercept the AST calls. We first print the `__str__` representation of the parsed input. We then call `.differentiate()` and print the unsimplified form. Finally, we call `.simplify()` and print the output.
- **Plotext Integration**: Using the `.evaluate()` method, we iterate an `x` value from `-10` to `10`. `Plotext` calculates terminal coordinates to draw an ANSI-colored scatterplot, which is immediately piped back into a Textual `Static` widget.
