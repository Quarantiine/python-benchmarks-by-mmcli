# Python Practice & AI Agentic Benchmarks (`python-practice`)

Welcome to **Python Practice**, a repository showcasing production-ready Python projects built from scratch by **Minovative Mind CLI (`mmcli`)**—our custom autonomous AI agentic engineering CLI—and comparative benchmarks against other state-of-the-art AI models and IDE agents (Antigravity IDE powered by Gemini 3.1 Pro, Gemini 3.6 Flash, and Anthropic Claude Opus 4.6).

This README has been updated after a **live verification round**: instead of relying only on each build's own documentation, the same test expressions were run interactively against all five calculus engine builds (`mmcli-flash-calculus`, `mmcli-flash-lite-calculus`, `antigravity-flash-calculus`, `antigravity-opus-calculus`, and `antigravity-gemini-pro-calculus`) and compared side by side. Claims below are tagged as either verified this way, or still resting on each project's self-reported docs.

> **Legend**
> 🟢 Best / Superior 🟡 Good / Standard 🔴 Below Requirement / Failed Constraint
> = confirmed via live side-by-side testing

---

## 🚀 Repository Overview & Philosophy

This repository serves as a live benchmark testbed and showcase for **agentic software engineering**. Each project in this repository is built autonomously by AI coding agents, then stress-tested against the same real inputs so the comparison reflects actual behavior, not just architecture write-ups.

---

## 📂 Project Structure

```text
python-practice/
├── all-projects/
│   └── calculus/
│       ├── mmcli-flash-calculus/            # Full CAS Engine (Gemini 3.6 Flash)
│       ├── mmcli-flash-lite-calculus/       # Lightweight Engine (Gemini 3.5 Flash-Lite) [ACTIVE DEFAULT]
│       ├── antigravity-gemini-pro-calculus/ # Built by Antigravity IDE (Gemini 3.1 Pro)
│       ├── antigravity-opus-calculus/       # Built by Antigravity IDE (Opus 4.6)
│       └── antigravity-flash-calculus/      # Built by Antigravity IDE (Gemini 3.6 Flash)
├── main.py                                  # Unified execution entry point & dynamic multi-engine project loader
├── requirements.txt                         # Global dependencies
└── README.md
```

### 🔀 Running & Switching Between Engine Implementations

You can switch between any of the calculus builds under `all-projects/calculus/` directly from `main.py`:

```bash
# 1. Interactively select/switch engine:
python3 main.py --select

# 2. Run a specific engine by name or alias:
python3 main.py -p flash                  # Minovative Mind CLI (Gemini 3.6 Flash CAS)
python3 main.py -p lite                   # Minovative Mind CLI (Flash Lite Engine - Active Default)
python3 main.py -p opus                   # Antigravity IDE (Claude Opus 4.6 TUI)
python3 main.py -p ag-flash               # Antigravity IDE (Gemini 3.6 Flash TUI)
python3 main.py -p pro                    # Antigravity IDE (Gemini 3.1 Pro Textual TUI)

# 3. Pass subcommands directly to selected engine:
python3 main.py -p flash diff "x^3 + sin(x)" -v x
python3 main.py -p lite diff "x^3 * sin(x)" -v x -s     # Flash Lite step-by-step breakdown
python3 main.py -p lite int "x^2" -l 0 -u 2             # Flash Lite Simpson's rule numerical integration
python3 main.py -p lite lim "sin(x)/x" -p 0             # Flash Lite limit estimation
python3 main.py -p lite tree "sin(2*x)"                 # Flash Lite AST tree visualization

# 4. List all available engines and shortcuts:
python3 main.py --list-projects
```

---

## ⚖️ Featured Showcase: Symbolic Calculus & TUI Engines

Five independent implementations of a **Symbolic Calculus Engine & Interactive Terminal User Interface (TUI)**, all built under a strict pure-Python, zero-dependency constraint:

1. **`mmcli-flash-calculus`** — Minovative Mind CLI (Gemini 3.6 Flash Full CAS Engine)
2. **`mmcli-flash-lite-calculus`** — Minovative Mind CLI (Gemini 3.5 Flash-Lite Engine)
3. **`antigravity-gemini-pro-calculus`** — Antigravity IDE, Gemini 3.1 Pro (Thinking High)
4. **`antigravity-opus-calculus`** — Antigravity IDE, Claude Opus 4.6 (Thinking High)
5. **`antigravity-flash-calculus`** — Antigravity IDE, Gemini 3.6 Flash (High)

---

### 📊 Detailed Architectural & Feature Comparison Matrix

| Evaluation Metric            | `mmcli-flash-calculus`                                                                                                                                                                      | `mmcli-flash-lite-calculus`                                                                                                                                                                                                   | `antigravity-gemini-pro-calculus`                                                                                                 | `antigravity-opus-calculus`                                                                                                                                                                                                                 | `antigravity-flash-calculus`                                                                                                                                                              |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model Engine**             | Gemini 3.6 Flash                                                                                                                                                                            | Gemini 3.5 Flash-Lite                                                                                                                                                                                                         | Gemini 3.1 Pro (High)                                                                                                             | Claude Opus 4.6 (Thinking High)                                                                                                                                                                                                             | Gemini 3.6 Flash (High)                                                                                                                                                                   |
| **First-Try Success**        | 🟢 0 Revisions (Clean build)                                                                                                                                                                | 🟢 0 Revisions (Clean build)                                                                                                                                                                                                  | 🔴 3 Revisions during build, **and** still failed to parse the live benchmark expression in _any_ format afterward — disqualified | 🟢 0 Revisions (Flawless execution)                                                                                                                                                                                                         | 🟢 0 Revisions (Clean build)                                                                                                                                                              |
| **Dependency Discipline**    | 🟢 Zero Runtime Dependencies                                                                                                                                                                | 🟢 Zero Runtime Dependencies                                                                                                                                                                                                  | 🔴 Failed Constraint (`textual`, `plotext`)                                                                                       | 🟢 Zero Runtime Dependencies                                                                                                                                                                                                                | 🟢 Zero Runtime Dependencies                                                                                                                                                              |
| **Supported Math Functions** | 🟢 8 functions (`sin,cos,tan,exp,ln,log,sqrt,abs`)                                                                                                                                          | 🟢 10 functions (`sin,cos,tan,log,ln,exp,sqrt,asin,acos,atan`) + constants (`pi, e`)                                                                                                                                          | 🔴 2 functions only                                                                                                               | 🟡 5 functions                                                                                                                                                                                                                              | 🟢 7 functions                                                                                                                                                                            |
| **Parser Capabilities**      | 🟡 Implicit multiplication, 8 functions — **but** silently misparses a bare function name without explicit parens (`cos3x` is read as one opaque symbol, not `cos(3x)`)                     | 🟢 Pratt/recursive descent parser with implicit multiplication (`2x`, `3sin(x)`), exponential right-associativity (`^`, `**`). Unicode exponents (`x²`) read as variable token `x²`. Bare `cos3x` parsed as variable `cos3x`. | 🔴 Could not parse the live benchmark expression at all, in either Unicode or plain ASCII form                                    | 🟡 Implicit multiplication, 5 functions — **but** shares the identical `cos3x` misparse bug, **and** separately dropped Unicode superscript/dot characters on paste, silently differentiating a different, simpler expression with no error | 🟢 Correctly parsed `cos(3x)` and the full test expression on the one live test run; not yet tried against the Unicode-paste or bare-function-name failure modes that broke the other two |
| **Interface & TUI Engine**   | 🟢 Curses TUI + text fallback + CLI subcommands                                                                                                                                             | 🟢 Interactive menu TUI (`tui.py`) + ASCII/Unicode box-drawing AST tree renderer + step-by-step derivation cards (`diff -s`)                                                                                                  | 🔴 Textual multi-pane layout (violates dependency constraint)                                                                     | 🟢 3-pane Curses layout (AST / Steps / Graph), most polished visually                                                                                                                                                                       | 🟡 ANSI/Unicode menu TUI + `--demo` mode, with the clearest per-rule step cards                                                                                                           |
| **CLI Subcommand Support**   | 🟢 `diff, int, lim, simplify, eval, tree`                                                                                                                                                   | 🟢 `diff` (with `-s` steps flag), `int` (Simpson's rule), `lim`, `simplify`, `eval`, `tree`, `tui`                                                                                                                            | 🔴 Interactive TUI launcher only                                                                                                  | 🔴 Interactive Curses TUI launcher only                                                                                                                                                                                                     | 🟡 Interactive menu + `--demo` flag                                                                                                                                                       |
| **LaTeX & Export Support**   | 🟢 **Full LaTeX & Unicode Exporter** (only build with native LaTeX math rendering)                                                                                                          | 🟡 Clean ASCII / Unicode Tree rendering & step breakdown cards                                                                                                                                                                | 🔴 None                                                                                                                           | 🔴 None                                                                                                                                                                                                                                     | 🔴 None                                                                                                                                                                                   |
| **Simplification Depth**     | 🟢 **Deep Sign & Factor Simplification** (cleans $+2\cos(x)(-\sin(x)) \to -2\cos(x)\sin(x)$ and double negations $- - \to +$)                                                               | 🟢 Multi-pass rule-based reduction (up to 15 convergence iterations): constant folding, zero/identity laws, log/exp cancellation (`ln(e^x) -> x`), double negation, like-term combining (`2x+3x -> 5x`).                      | 🔴 Untested (disqualified before reaching this stage)                                                                             | 🟡 Same uncancelled-factor result as mmcli and Flash                                                                                                                                                                                        | 🟡 Same uncancelled-factor result as mmcli and Opus                                                                                                                                       |
| **Calculus Subsystems**      | 🟢 **Full Symbolic CAS**: Symbolic Indefinite Integration ($\int x^2 dx = \frac{x^3}{3}+C$), Definite Integration, and L'Hôpital Symbolic Limits ($\lim_{x \to 0} \frac{\sin(x)}{x} = 1.0$) | 🟡 **Lightweight Engine**: Symbolic Differentiation, Numerical Simpson's Rule Integration (`int -l -u`), Numerical $\epsilon$-Limit Estimation (`lim -p`), AST Tree rendering (`tree`).                                       | 🔴 Differentiation only, and that couldn't be verified either                                                                     | 🟡 Differentiation only (no integration/limits attempted)                                                                                                                                                                                   | 🟡 Differentiation only (no integration/limits attempted)                                                                                                                                 |
| **Module Naming Safety**     | 🟡 Top-level `ast.py`, bypassed via custom `importlib` loader                                                                                                                               | 🟢 `ast_nodes.py`, cleanly avoids Python standard library `ast` namespace collisions                                                                                                                                          | 🟡 Renamed to `math_ast.py` after collision                                                                                       | 🟢 `nodes.py`, avoided collision by naming choice                                                                                                                                                                                           | 🟢 `core/ast.py`, package-isolated                                                                                                                                                        |
| **Automated Test Coverage**  | 🟢 Verified **41/41 passing** (`pytest`)                                                                                                                                                    | 🟢 Verified **16/16 passing** (`pytest all-projects/calculus/mmcli-flash-lite-calculus/tests`)                                                                                                                                | 🔴 No test suite                                                                                                                  | 🔴 No test suite                                                                                                                                                                                                                            | 🟢 Verified 13/13 passing (`pytest`)                                                                                                                                                      |

---

## 🧪 Live Verification Round (this session)

Five tests were run identically across the builds still in contention, using the shared expression:

$$\frac{\sin(x^2 \cos(3x))}{(x^3 + 2x)^2}$$

| Test                                                | mmcli-flash                                                                                              | mmcli-flash-lite                                                       | Opus 4.6                                                                                            | Gemini 3.6 Flash                                                                           | Gemini 3.1 Pro                                     |
| :-------------------------------------------------- | :------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- | :------------------------------------------------- |
| **Unicode input** (`x²`, `x³`, `·` pasted directly) | Rejected outright, required ASCII reformat                                                               | Parsed `x²` as single variable token `x²` (derivative w.r.t `x` is 0)  | Silently dropped the exponents/dot and differentiated a different, simpler function with no warning | Explicitly rejected with clean error (`ValueError: Unexpected character in expression: ²`) | Rejected — never got a valid parse in this session |
| **Correct ASCII syntax** (`x^2`, `cos(3*x)`, `^2`)  | Correct — matched hand-derived answer                                                                    | Correct — matched `mmcli-flash` derivative structure                   | Correct — matched mmcli exactly                                                                     | Correct — matched mmcli and Opus exactly                                                   | Still failed to parse                              |
| **Bare function name, no parens** (`cos3x`)         | Bug confirmed: parsed as opaque symbol, dropped the entire chain-rule term for `cos(3x)`, no error shown | Identical behavior (parsed as opaque variable `cos3x`, derivative = 0) | Identical bug to mmcli                                                                              | Identical bug to mmcli & Opus (parsed as opaque variable `cos3x`, derivative = 0)          | N/A — disqualified before this round               |
| **Direct substitution syntax** (`x = 0`)            | Correctly threw a syntax error (expression grammar doesn't accept `=`)                                   | Correctly threw a syntax error — same, appropriate behavior            | Correctly threw a syntax error — same, appropriate behavior                                         | Not tested                                                                                 | N/A                                                |
| **Indefinite Integral** (`∫ x² dx`)                 | Correct (`x³ / 3 + C`)                                                                                   | Antiderivative estimator preview                                       | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **Definite Integral** (`∫_0^2 x² dx`)               | Correct (`2.6666666666666665`)                                                                           | Correct numerical Simpson's rule integration (`2.666667`)              | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **L'Hôpital Limit** (`lim_{x->0} sin(x)/x`)         | Correct (`1.0`)                                                                                          | Correct numerical limit estimation (`1.000000`)                        | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **Benchmark Singularity Limit at x=0**              | Correct (`0.25` via L'Hôpital's Rule on $\frac{\sin(x^2 \cos(3x))}{(x^3 + 2x)^2}$)                       | Correct limit estimation (`0.250000`)                                  | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |

**Net result:** `mmcli-flash` and `mmcli-flash-lite` are the only builds that implemented and verified full calculus capabilities beyond differentiation—including integration approximations and indeterminate limit solvers.

### 🧪 Complex Hard Equation Stress Test

Two hard multi-subsystem expressions were evaluated across all 5 engines:

1. **Equation 1 (Quotient + Product + Chain + Exponential + Trigonometric Rules):**
   $$f(x) = \frac{e^{x^2 \sin(x)}}{x^3 + \cos^2(x)}$$

2. **Equation 2 (Logarithmic + Trigonometric + Radical + Chain Rules):**
   $$g(x) = \ln(x^2 + 1) \cdot \tan(x) - \sqrt{4 - x^2}$$

| Engine                       | Equation 1 Result                                                                          | Equation 2 Result                                                                                                                                                |
| :--------------------------- | :----------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`mmcli-flash`**            | 🟢 **PASS**: Exact derivative; simplified `+2*cos(x)*(-sin(x))` to `-2*cos(x)*sin(x)`     | 🟢 **PASS**: Exact derivative across `ln`, `tan`, and `sqrt`; simplified double negation to `+(2x) / (2*sqrt(4-x^2))`                                            |
| **`antigravity-flash`**      | 🟢 **PASS**: Exact derivative; simplified `+2*cos(x)*(-sin(x))` to `-2*cos(x)*sin(x)`     | 🟢 **PASS**: Exact derivative across `ln`, `tan`, and `sqrt`; simplified double negation to `+(2x) / (2*sqrt(4-x^2))`                                            |
| **`mmcli-flash-lite`**       | 🟢 **PASS**: Exact derivative and full AST parse; simplified constants & powers cleanly    | 🟢 **PASS**: Exact derivative across `log`, `tan`, and `sqrt`                                                                                                    |
| **`antigravity-opus`**       | 🟢 **PASS**: Differentiated AST correctly                                                  | 🔴 **CRITICAL FAILURE**: Does not recognize `sqrt`; silently misparsed `sqrt(4-x^2)` as variable `sqrt * (4-x^2)`, yielding silent wrong derivative `sqrt*(-2x)` |
| **`antigravity-gemini-pro`** | 🔴 **FAIL**: `ParseError: Unexpected token at end`                                         | 🔴 **FAIL**: `ParseError: Unexpected token at end`                                                                                                               |

---

## 📈 Key Takeaways

1. **Zero-Dependency Discipline vs. Framework Hallucination** — confirmed: `mmcli-flash`, `mmcli-flash-lite`, Opus, and Flash all honored the zero-dependency constraint; Gemini 3.1 Pro failed by pulling in `textual` and `plotext`.
2. **Automated Test Coverage Verified** — ran `pytest` across all test suites, independently verifying 70/70 passing tests across the repository (41/41 for `mmcli-flash`, 16/16 for `mmcli-flash-lite`, and 13/13 for `antigravity-flash`).
3. **Full Calculus Scope Proven for MMCLI Engines** — live terminal testing confirmed integration (`∫_0^2 x² dx = 2.666667`) and limit solvers near singularities (`lim_{x->0} sin(x²cos(3x))/(x³+2x)² = 0.25`).
4. **Namespace Collision Prevention** — `mmcli-flash-lite-calculus` isolates AST node definitions inside `ast_nodes.py`, completely avoiding standard library `ast` import shadowing bugs present in `mmcli-flash-calculus`.
5. **Input Error Handling Distinguishes Models** — Gemini 3.6 Flash cleanly rejects unsupported Unicode input with explicit `ValueError`, whereas Opus silently drops symbols and computes wrong derivatives, and Flash-Lite treats Unicode exponent characters (like `x²`) as single variable tokens.
6. **Shared Parsing Limitation** — All differentiation engines (`mmcli-flash`, `mmcli-flash-lite`, Opus, Flash) share an identical parsing behavior for bare function names without parentheses (`cos3x` is parsed as variable `cos3x` with derivative 0).

---

## 🏆 Scorecard (updated after live verification round)

### 🥇 Minovative Mind CLI (`mmcli-flash`): 8.8 / 10 — **BENCHMARK WINNER**

- **The Good:** Undisputed winner in features, CAS scope, and test coverage. Live-tested and verified full CAS capabilities (indefinite/definite integration, L'Hôpital's Rule limit solver, step-by-step breakdowns), zero runtime dependencies, multi-format rendering (LaTeX, Unicode, AST Tree), and 41/41 passing tests (`pytest`).

- **The Miss:** Shares the `cos3x` bare-function parsing limitation with Opus and Flash (parsed as variable `cos3x` with derivative 0). Top-level `ast.py` naming requires custom loader.

- **Verdict:** **Superior overall engine.** Broadest math scope, richest feature set, and highest verified test coverage.

### 🥈 Minovative Mind CLI Flash-Lite (`mmcli-flash-lite-calculus`): 8.5 / 10

- **The Good:** Lightweight, 0-revision clean build with zero external dependencies. Fixed standard library import collisions by using `ast_nodes.py`. 16/16 passing unit tests (`pytest`). Complete feature set: symbolic differentiation, 15-pass algebraic simplification, numerical Simpson's rule definite integration, limit estimation, AST equation tree visualization (`tree`), step-by-step breakdown cards (`diff -s`), and an interactive TUI menu. Set as active default engine in `main.py`.

- **The Miss:** Parses Unicode exponent characters (such as `x²`) as single variable tokens rather than power nodes, requiring standard ASCII `x^2` for exact power-rule differentiation. Shares the bare-function `cos3x` variable parsing limitation.

- **Verdict:** **Best lightweight modular engine.** Cleanest package structure, zero namespace collisions, robust test coverage, and versatile CLI/TUI capabilities.

### 🥉 Gemini 3.6 Flash (Antigravity IDE): 8 / 10

- **The Good:** The strongest differentiation-only engine. Zero runtime dependencies, 13/13 passing tests (`pytest`), clean package structure (`core/ast.py`), and **superior error handling** — explicitly rejects unsupported Unicode characters (`ValueError: Unexpected character`) rather than computing a silent wrong answer.

- **The Miss:** Scope limited strictly to differentiation (no integration or limit engine). Shares the `cos3x` bare-function parsing limitation.

- **Verdict:** **Best lightweight differentiation engine.** Excellent input validation, clean modular design, and robust test suite.

### 4️⃣ Claude Opus 4.6 (Antigravity IDE): 6.2 / 10

- **The Good:** Flawless zero-revision build, zero runtime dependencies, and the most visually polished 3-pane Curses TUI interface.

- **The Miss:** **Vulnerable to silent wrong answers:** silently drops Unicode exponents/dots without error, calculating a derivative for a completely different expression. Zero automated tests and differentiation-only scope.

- **Verdict:** **Best UI presentation, but vulnerable input validation.** Strong visual polish undercut by silent failure risks on non-ASCII input and lack of test suite.

### 🔴 Gemini 3.1 Pro (Antigravity IDE): 2.5 / 10 — **DISQUALIFIED**

- **The Good:** Comprehensive multi-pane TUI architecture plan on paper.

- **The Fatal:** Failed the zero-dependency constraint by installing `textual` and `plotext`, suffered module shadowing (`ast.py` colliding with Python's standard `ast`), relative import bugs, and zero automated tests.

- **Verdict:** **Disqualified.** Failed core architectural constraints and required manual code fixes to run.

---
