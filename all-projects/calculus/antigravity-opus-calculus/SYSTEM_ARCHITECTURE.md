# System Architecture

> Antigravity IDE, using Opus 4.6 (Thinking (HIGH)), Revised it's code (0) times after my first try using this Calculus TUI

> Verdict: Works 100% after the first try

---

The engine follows a three-layer pipeline architecture:

```
[ User Input ] → Tokenizer → Parser → [ AST ] → { Differentiate, Simplify, Evaluate } → [ TUI Display ]
```

---

## 1. The Parser (`parser.py`)

### Tokenizer

Character-by-character scanning classifies input into typed tokens:

| Token Type | Examples                | Description                    |
| :--------- | :---------------------- | :----------------------------- |
| `NUM`      | `42`, `3.14`, `pi`, `e` | Numeric literals and constants |
| `VAR`      | `x`, `y`, `theta`       | Variable identifiers           |
| `FUNC`     | `sin`, `cos`, `ln`      | Recognized function names      |
| `OP`       | `+`, `-`, `^`, `(`      | Operators and delimiters       |

Constants `pi` and `e` are resolved to numeric values at tokenization time.

### Implicit Multiplication

A post-tokenization pass inserts `*` tokens where multiplication is implied:

```
2x        → 2 * x
2sin(x)   → 2 * sin(x)
(x+1)(x)  → (x+1) * (x)
x(x+1)    → x * (x+1)
```

### Recursive Descent Parser

Implements standard mathematical precedence via mutually recursive functions:

```
expr   → term (('+' | '-') term)*           ← lowest precedence
term   → power (('*' | '/') power)*
power  → unary ('^' power)?                 ← right-associative
unary  → '-' unary | call
call   → FUNC '(' expr ')' | atom
atom   → NUMBER | VARIABLE | '(' expr ')'   ← highest precedence
```

---

## 2. The AST Engine (`nodes.py`)

Every expression is represented as a tree of `Expr` node objects:

```
  (x^2) * sin(x)

      ×
     / \
    ^   sin
   / \   |
  x   2   x
```

### Node Hierarchy

| Category        | Nodes                             | Slots           |
| :-------------- | :-------------------------------- | :-------------- |
| **Leaves**      | `Const(value)`, `Var(name)`       | Single value    |
| **Binary Ops**  | `Add`, `Sub`, `Mul`, `Div`, `Pow` | `left`, `right` |
| **Unary Funcs** | `Sin`, `Cos`, `Tan`, `Ln`, `Exp`  | `arg`           |

### Differentiation Rules

Each node implements `differentiate(var)` returning a new AST:

| Node       | Rule              | Formula                   |
| :--------- | :---------------- | :------------------------ |
| `Const`    | Constant          | d/dx[c] = 0               |
| `Var(x)`   | Variable          | d/dx[x] = 1, d/dx[y] = 0  |
| `Add(u,v)` | Sum               | (u+v)' = u' + v'          |
| `Sub(u,v)` | Difference        | (u−v)' = u' − v'          |
| `Mul(u,v)` | **Product Rule**  | (uv)' = u'v + uv'         |
| `Div(u,v)` | **Quotient Rule** | (u/v)' = (u'v − uv') / v² |
| `Pow(u,n)` | **Power Rule**    | (u^n)' = n·u^(n−1)·u'     |
| `Pow(u,v)` | **General Power** | u^v · (v'·ln(u) + v·u'/u) |
| `Sin(u)`   | **Chain Rule**    | cos(u)·u'                 |
| `Cos(u)`   | **Chain Rule**    | −sin(u)·u'                |
| `Tan(u)`   | **Chain Rule**    | sec²(u)·u'                |
| `Ln(u)`    | **Chain Rule**    | u'/u                      |
| `Exp(u)`   | **Chain Rule**    | exp(u)·u'                 |

### Simplification

Bottom-up recursive simplification applies algebraic identities:

- **Constant folding**: `2 + 3` → `5`, `sin(0)` → `0`
- **Identity elements**: `x + 0` → `x`, `x * 1` → `x`
- **Annihilators**: `x * 0` → `0`, `0 / x` → `0`
- **Power identities**: `x^0` → `1`, `x^1` → `x`
- **Self-cancellation**: `x − x` → `0`, `x / x` → `1`
- **Negation**: `0 − x` → `−x`

`deep_simplify()` runs multiple passes until the string representation stabilizes.

### Evaluation

`evaluate(env)` recursively computes a float given variable bindings (e.g., `{'x': 2.0}`), enabling the graph plotter.

---

## 3. The Interface Layer (`tui.py`)

Built entirely with Python's built-in `curses` library — **zero external dependencies**.

### Layout

```
┌─── ∫ Symbolic Calculus Engine ─────────────────────────────┐
│ f(x) = x^2 * sin(x)                                       │
├──────────────┬────────────────────┬────────────────────────┤
│ AST Tree     │ Derivation Steps   │ Graph                  │
│──────────────┼────────────────────┼────────────────────────│
│ ×            │ f(x) = (x^2*sinx)  │   100.0┤     ●●       │
│ ├── ^        │                    │        │   ●    ●     │
│ │   ├── x    │ Rule: Product      │    0.0┼●●        ●●   │
│ │   └── 2    │  (uv)'= u'v + uv' │        │              │
│ └── sin      │                    │ -100.0┤               │
│     └── x    │ Simplified: ...    │                        │
├──────────────┴────────────────────┴────────────────────────┤
│ ESC Quit │ Enter Compute │ Ctrl+U Clear                    │
└────────────────────────────────────────────────────────────┘
```

### ASCII Graphing

The built-in plotter:

1. Samples `f(x)` across `[-10, 10]`
2. Uses **percentile-based y-range clipping** (2nd–98th) to handle outliers (e.g., `tan(x)` near asymptotes)
3. Renders Unicode box-drawing characters (`─`, `│`, `┼`, `●`, `·`) for axes and data points
4. Interpolates vertical gaps between consecutive points for smoother curves

### Step-by-Step Engine

For each expression, the derivation panel shows:

1. **Original expression** — `f(x) = ...`
2. **Rule identified** — Product, Quotient, Chain, Power, etc.
3. **Sub-expressions** — `u = ...`, `v = ...`
4. **Raw derivative** — before simplification
5. **Simplified result** — after deep simplification

---

## File Structure

```
antigravity-opus-calculus/
├── __init__.py              # Package marker
├── __main__.py              # Entry point
├── nodes.py                 # AST node classes with diff/simplify/eval
├── parser.py                # Tokenizer + recursive descent parser
├── tui.py                   # Curses TUI + ASCII plotting + step engine
├── README.md                # Usage documentation
└── SYSTEM_ARCHITECTURE.md   # This file
```
