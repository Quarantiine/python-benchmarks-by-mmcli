# Symbolic Calculus Engine

A pure-Python symbolic math engine and interactive Terminal User Interface (TUI) for symbolic calculus, algebraic manipulation, and step-by-step mathematical problem solving.

---

## Key Features

- **Interactive TUI**: Terminal UI built with Curses (with automatic graceful text fallback) for live interactive expression testing, operation selection, and step-by-step reasoning.
- **CLI Subcommands**: Full-featured command-line interface for differentiation, integration, limit evaluation, simplification, numerical evaluation, and AST visualization.
- **Symbolic Differentiation**: Computes exact symbolic derivatives using product, quotient, power, chain, trigonometric, exponential, and logarithmic differentiation rules.
- **Symbolic Integration**: Supports indefinite and definite integration, handling polynomial powers, trigonometric, exponential, logarithmic, and linear substitution / integration-by-parts forms.
- **Limits Engine**: Evaluates symbolic limits via direct substitution, factor cancellation, L'Hôpital's Rule for indeterminate forms ($0/0$, $\infty/\infty$), infinity limits, and numeric epsilon probes.
- **Algebraic Simplification**: Simplifies algebraic, power, trigonometric, and logarithmic expressions with iterative fixpoint rules.
- **Rich Rendering**: Multiple output formats including Unicode math, LaTeX notation, and ASCII Abstract Syntax Tree (AST) tree diagrams.
- **Python API**: Clean, standard Python library interface with operator overloading on AST nodes for programmatic use.

---

## Installation & Requirements

### Requirements

- **Python 3.8+** (Note: macOS/Linux environments require `python3` instead of `python`).
- Zero third-party runtime dependencies required.

### Virtual Environment Setup

Activate the virtual environment before running the project:

- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows (Command Prompt / PowerShell)**:
  ```cmd
  venv\Scripts\activate
  ```

### Running from Project Root

From the top-level repository folder:

```bash
# Launch interactive TUI
python3 main.py

# Or launch CLI subcommand directly
python3 main.py diff "x^3 + sin(x)" -v x
```

### Direct Script Execution & PYTHONPATH Notes

To run the subproject directly without going through root `main.py`:

```bash
# From workspace root
python3 all-projects/calculus/mmcli-agent-calculus/__main__.py

# Or navigate into the subproject directory directly
cd all-projects/calculus/mmcli-agent-calculus
python3 __main__.py
```

> **Important Note on `PYTHONPATH` and Module Execution:**
> Running `PYTHONPATH=all-projects/calculus/mmcli-agent-calculus python3 -m calculus` fails with `No module named calculus` because the subproject directory on disk is named `mmcli-agent-calculus`, not `calculus`. Additionally, placing `mmcli-agent-calculus` directly into `PYTHONPATH` or `sys.path[0]` causes its local `ast.py` module to shadow Python's standard library `ast` module.
>
> To run commands cleanly:
>
> - Use the top-level entry point `python3 main.py [subcommand]` or `PYTHONPATH=. python3 main.py [subcommand]`.
> - Use `python3 all-projects/calculus/mmcli-agent-calculus/__main__.py [subcommand]`.
> - Run test suites using `pytest` from the root directory (`tests/conftest.py` configures `calculus` module loading dynamically without shadowing standard library modules).

---

## Interactive TUI Mode

Launch the interactive Terminal User Interface (TUI) by running `python3 main.py` or `python3 main.py tui`.

### Features

1. **Interactive Operation Selector**:
   - `1` - **Differentiate**: Compute exact symbolic derivative $f'(x)$.
   - `2` - **Integrate**: Compute indefinite or definite integral $\int f(x)\,dx$.
   - `3` - **Limit**: Evaluate limit $\lim_{x \to a} f(x)$.
   - `4` - **Simplify**: Algebraic and trigonometric expression reduction.
   - `5` - **Evaluate**: Variable substitution and numerical evaluation.
   - `6` - **AST Tree**: Interactive AST structural tree inspector.
2. **Step-by-Step Breakdown**: Explains applied calculus rules, trigonometric identities, limit indeterminate forms, or substitution steps.
3. **Multi-Format View**: Displays results formatted as Unicode Math, LaTeX code, and ASCII Tree structure.
4. **Curses & Fallback Modes**: Uses standard `curses` library on POSIX systems with an automatic fallback interactive mode if running in an unsupported environment.

---

## CLI Subcommands

The CLI entry point `main.py` provides several subcommands for single-line terminal execution.

### General Syntax

```bash
python3 main.py <subcommand> <expression> [options]
```

---

### 1. Differentiation (`diff`)

Aliases: `differentiate`, `derivative`

Computes the symbolic derivative of an expression.

```bash
# Basic derivative with respect to x
python3 main.py diff "x^3 + sin(x)"

# Derivative with respect to variable y
python3 main.py diff "y^2 * exp(y)" -v y

# Output format as LaTeX without step-by-step breakdown
python3 main.py diff "ln(x) / x" --no-steps -f latex
```

#### Options:

- `-v`, `--var <NAME>`: Target variable to differentiate with respect to (default: `x`).
- `--steps` / `--no-steps`: Enable or disable step-by-step breakdown (default: `--steps`).
- `-f`, `--format <unicode|latex|ascii|tree|all>`: Result rendering format (default: `all`).

---

### 2. Integration (`int`)

Aliases: `integrate`, `integral`

Computes indefinite integrals or definite integrals with lower and upper limits.

```bash
# Indefinite integral: ∫ x^2 dx
python3 main.py int "x^2"

# Definite integral: ∫_0^2 x^2 dx
python3 main.py int "x^2" -l 0 -u 2

# Definite integral with symbolic bounds
python3 main.py int "cos(x)" -l 0 -u "pi/2"
```

#### Options:

- `-v`, `--var <NAME>`: Variable of integration (default: `x`).
- `-l`, `--lower <VAL>`: Lower integration limit (for definite integrals).
- `-u`, `--upper <VAL>`: Upper integration limit (for definite integrals).
- `--steps` / `--no-steps`: Enable or disable step breakdown.
- `-f`, `--format <FORMAT>`: Output format style.

---

### 3. Limits (`lim`)

Aliases: `limit`

Evaluates symbolic limits as a variable approaches a target value.

```bash
# Standard limit: lim_{x->0} sin(x)/x
python3 main.py lim "sin(x)/x" -p 0

# Limit approaching infinity: lim_{x->oo} (2*x^2 + 1)/(x^2 - 3)
python3 main.py lim "(2*x^2 + 1) / (x^2 - 3)" -p "inf"

# One-sided limit from right: lim_{x->0+} ln(x)
python3 main.py lim "ln(x)" -p 0 -d right
```

#### Options:

- `-v`, `--var <NAME>`: Variable approaching the point (default: `x`).
- `-p`, `--point <VAL>`: Point limit target value (e.g. `0`, `pi/2`, `inf`, `-inf`) (default: `0`).
- `-d`, `--direction <both|left|right>`: Limit approach direction (default: `both`).
- `--steps` / `--no-steps`: Enable or disable step breakdown.
- `-f`, `--format <FORMAT>`: Output format style.

---

### 4. Simplification (`simplify`)

Aliases: `simp`

Reduces algebraic, logarithmic, exponential, and trigonometric expressions.

```bash
python3 main.py simplify "x + x + 2*x + 0*y"
python3 main.py simplify "sin(x)^2 + cos(x)^2"
```

#### Options:

- `--steps` / `--no-steps`: Enable or disable step breakdown.
- `-f`, `--format <FORMAT>`: Output format style.

---

### 5. Evaluation (`eval`)

Aliases: `evaluate`

Evaluates a mathematical expression given concrete values for its free variables.

```bash
# Evaluate x^2 + y at x=3, y=4
python3 main.py eval "x^2 + y" x=3 y=4

# Using -v argument flag
python3 main.py eval "2*a + b" -v a=5 -v b=10
```

---

### 6. AST Tree Diagram (`tree`)

Aliases: `ast`

Prints a visual multi-line ASCII tree representation of the expression's internal AST node structure.

```bash
python3 main.py tree "sin(2*x) + 3*x^2"
```

---

## Python API Usage

You can import and use the Symbolic Calculus Engine directly inside your Python scripts.

```python
from calculus import (
    parse,
    diff,
    integrate,
    limit,
    simplify,
    render_pretty,
    to_latex,
    render_tree,
    Symbol,
    Const,
    Add,
    Mul,
    Sin,
    Cos
)

# 1. Parsing mathematical string expressions
expr = parse("x^3 + sin(x)")
print(f"Parsed Expression: {expr}")

# 2. Symbolic Differentiation
derivative = diff(expr, var="x")
print(f"f'(x) = {render_pretty(derivative)}")
print(f"f'(x) LaTeX: {to_latex(derivative)}")

# 3. Symbolic Integration (Indefinite & Definite)
indef_integral = integrate(parse("x^2"), var="x")
print(f"∫ x^2 dx = {render_pretty(indef_integral)}")

def_integral = integrate(parse("x^2"), var="x", lower=0, upper=2)
print(f"∫_0^2 x^2 dx = {def_integral}")

# 4. Limit Evaluation
lim_val = limit(parse("sin(x)/x"), var="x", point=0)
print(f"lim_{{x->0}} sin(x)/x = {lim_val}")

# 5. Expression Simplification
raw_expr = parse("x + x + 0*y + 1*z")
simplified = simplify(raw_expr)
print(f"Simplified: {render_pretty(simplified)}")

# 6. AST Programmatic Construction
x = Symbol("x")
ast_expr = Add(Pow(x, Const(2)), Mul(Const(3), x))
print(f"Evaluated at x=4: {ast_expr.eval({'x': 4})}")

# 7. AST Visual Tree Output
print(render_tree(ast_expr))
```

---

## Step-by-Step Reasoning Engine

The `StepByStepEngine` class allows programmatically retrieving solution steps and reasoning breakdowns.

```python
from calculus.tui import StepByStepEngine

# Get derivative explanation
step_info = StepByStepEngine.explain_diff("x^3 + sin(x)", var_str="x")

print("Result:", step_info["result_str"])
print("LaTeX:", step_info["latex_str"])
print("Steps:")
for step in step_info["steps"]:
    print(f" - {step}")
```

---

## Project Architecture Overview

- `ast.py`: Defines immutable expression nodes (`Symbol`, `Const`, `Add`, `Sub`, `Mul`, `Div`, `Pow`, `Neg`, `Sin`, `Cos`, etc.).
- `parser.py`: Tokenizer and precedence climbing recursive-descent parser.
- `simplify.py`: Term combiner, constant fold, and identity algebraic simplifier.
- `diff.py`: Recursive symbolic differentiator implementing standard rules.
- `integrate.py`: Indefinite/definite integrator with linear substitution & integration by parts.
- `limits.py`: Indeterminate limit solver and direct/probe evaluator.
- `render.py`: Formatter for LaTeX code, Unicode math representation, and ASCII tree diagrams.
- `tui.py`: Terminal user interface & step-by-step reasoning engine.
- `cli.py`: Command-line interface subcommands & argument parsing.
