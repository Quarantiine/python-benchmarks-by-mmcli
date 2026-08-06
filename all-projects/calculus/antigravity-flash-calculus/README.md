# Antigravity Calculus Core Engine & Terminal UI (TUI)

A zero-dependency Python symbolic calculus engine featuring Abstract Syntax Tree (AST) expression parsing, recursive differentiation, algebraic simplification, step-by-step derivation tracking, and an interactive Terminal User Interface (TUI) with ASCII/Unicode equation tree visualizer and real-time function graph plotter.

For detailed system architecture diagrams and component deep dives, see [SYSTEM_ARCHITECTURE.md](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/SYSTEM_ARCHITECTURE.md).

---

## Features

1. **Abstract Syntax Tree (AST) Core**:
   - Class hierarchy: [ast.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/core/ast.py) (`Node`, `Constant`, `Variable`, `AddNode`, `SubNode`, `MulNode`, `DivNode`, `PowNode`, `SinNode`, `CosNode`, `TanNode`, `AsinNode`, `AcosNode`, `AtanNode`, `ExpNode`, `LnNode`, `SqrtNode`).
   - Infix operator precedence and implicit multiplication parser (`2x`, `3sin(x)`, `cos3x`, `x(x+1)`).

2. **Recursive Symbolic Differentiation Engine**:
   - Implements Product Rule, Quotient Rule, Chain Rule, General Power Rule, Logarithmic & Exponential rules, Trigonometric and Inverse Trig (`asin`, `acos`, `atan`) rules.
   - Step recorder tracking intermediate derivation logic in [differentiator.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/core/differentiator.py).

3. **Symbolic Integration & Limits Engine**:
   - Symbolic antiderivative computation and Simpson's numerical definite integration in [integrator.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/core/integrator.py).
   - Direct and symmetric perturbation limit evaluation in [limits.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/core/limits.py).

4. **Algebraic Simplifier & Constant Folder**:
   - Recursive fixed-point simplification pass for identity elements (`0 + x -> x`, `1 * x -> x`, `x ^ 1 -> x`), constant folding (`2 + 3 -> 5`), zero cancellation, like-terms reduction, and trig/exp/ln identities in [simplifier.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/core/simplifier.py).

5. **Terminal User Interface (TUI)**:
   - **AST Tree Visualizer**: ASCII/Unicode box-drawing tree representation in [tree_renderer.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/tui/tree_renderer.py).
   - **Step-by-Step Breakdown**: Clear terminal report of all calculus rules applied in [derivation_view.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/tui/derivation_view.py).
   - **Real-Time Terminal Graph Plotter**: Plots $f(x)$ (`*`) and $f'(x)$ (`#`) on ASCII grid axes with auto-scaling in [plotter.py](file:///Users/danielward/Developer/Personal%20Projects/Machine%20Learning-AI/python-practice/all-projects/calculus/antigravity-flash-calculus/tui/plotter.py).

---

## Directory Structure

```
antigravity-flash-calculus/
├── __main__.py               # Entry point runner
├── README.md                 # Documentation and architecture breakdown
├── SYSTEM_ARCHITECTURE.md    # System architecture and data flow diagrams
├── report.md                 # Audit fix and benchmark verification report
├── core/                     # Calculus AST & Symbolic Engine
│   ├── __init__.py
│   ├── ast.py                # AST Node hierarchy
│   ├── parser.py             # Expression lexer & parser
│   ├── differentiator.py     # Symbolic differentiator & step recorder
│   ├── integrator.py         # Symbolic & numerical integration engine
│   ├── limits.py             # Limit evaluation engine
│   ├── simplifier.py         # Algebraic simplifier & constant folder
│   └── evaluator.py          # AST numerical evaluator
├── tui/                      # Terminal UI & Visualizers
│   ├── __init__.py
│   ├── app.py                # Interactive TUI app & menu state machine
│   ├── tree_renderer.py      # AST box-drawing tree visualizer
│   ├── plotter.py            # ASCII/Unicode function graph plotter
│   └── derivation_view.py    # Step-by-step derivation breakdown renderer
└── tests/                    # Unit test suite
    ├── __init__.py
    └── test_engine.py        # 17 comprehensive unit tests
```


---

## Quick Start & Usage

### 1. Interactive Terminal UI
Run the interactive menu TUI:
```bash
python3 all-projects/calculus/antigravity-flash-calculus/__main__.py
```

### 2. Automated Demonstration Mode
Run the non-interactive showcase:
```bash
python3 all-projects/calculus/antigravity-flash-calculus/__main__.py --demo
```

### 3. Run Automated Tests
Execute the unit test suite:
```bash
python3 -m unittest discover -s all-projects/calculus/antigravity-flash-calculus/tests
```
