# Symbolic Calculus Engine — Interactive TUI

A **zero-dependency**, pure Python symbolic calculus engine with an interactive curses-based terminal user interface. Built entirely from the Python standard library.

---

## Quick Start

```bash
cd all-projects/calculus/antigravity-opus-calculus
python3 __main__.py
```

> **Note:** No `pip install` needed. Zero external dependencies.

---

## Features

| Feature | Description |
| :--- | :--- |
| **Symbolic Differentiation** | Product rule, quotient rule, chain rule, power rule |
| **Algebraic Simplification** | Constant folding, identity reduction, multi-pass deep simplification |
| **AST Visualization** | Real-time Unicode tree rendering of expression structure |
| **Step-by-Step Derivation** | Shows the rule applied, raw derivative, and simplified result |
| **ASCII Function Graphing** | Plots f(x) with Unicode axes, y-labels, and percentile-based outlier clipping |
| **Implicit Multiplication** | Write `2x`, `2sin(x)`, `2(x+1)` naturally |
| **Built-in Constants** | `pi` (π) and `e` (Euler's number) are recognized automatically |

---

## Controls

| Key | Action |
| :--- | :--- |
| `Enter` | Parse expression and compute derivative |
| `ESC` | Quit the application |
| `Ctrl+U` | Clear input and reset |
| `←` / `→` | Move cursor in input field |
| `Backspace` | Delete character before cursor |
| `Delete` | Delete character after cursor |
| `Ctrl+A` / `Home` | Jump to start of input |
| `Ctrl+E` / `End` | Jump to end of input |

---

## Example Expressions

```
x^2                   → d/dx = 2x
sin(x)                → d/dx = cos(x)
x * sin(x)            → Product rule
cos(x) / (x + 1)      → Quotient rule
5*x^3 - 2*x + 7       → Power rule: 15x² - 2
tan(x)                → sec²(x) via chain rule
ln(x^2 + 1)           → Chain rule (logarithmic)
exp(-x^2)             → Chain rule (exponential)
2x                    → Implicit multiplication
```

---

## Supported Functions

- `sin(x)`, `cos(x)`, `tan(x)`
- `ln(x)` — natural logarithm
- `exp(x)` — exponential function

## Supported Operators

`+`, `-`, `*`, `/`, `^` (exponentiation)

Parentheses `()` for grouping. Exponentiation is **right-associative**: `2^3^2` = `2^(3^2)` = `2^9` = `512`.

---

## Architecture

See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for a detailed technical breakdown.

---

## Dependencies

**Zero runtime dependencies.** Uses only the Python standard library:

| Module | Purpose |
| :--- | :--- |
| `curses` | Terminal UI rendering |
| `math` | Mathematical functions |
| `locale` | Unicode support |
