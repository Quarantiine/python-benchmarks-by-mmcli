# Python Practice & AI Agentic Benchmarks (`python-practice`)

Welcome to **Python Practice**, a repository showcasing production-ready Python projects built from scratch by **Minovative Mind CLI (`mmcli`)**—our custom autonomous AI agentic engineering CLI—and comparative benchmarks against other state-of-the-art AI models and IDE agents (Antigravity IDE powered by Gemini 3.1 Pro, Gemini 3.6 Flash, and Anthropic Claude Opus 4.6).

This README has been updated after a **live verification round**: instead of relying only on each build's own documentation, the same test expressions were run interactively against all five calculus engine builds (`mmcli-flash-calculus`, `mmcli-flash-lite-calculus`, `antigravity-flash-calculus`, `antigravity-opus-calculus`, and `antigravity-gemini-pro-calculus`) and compared side by side. Claims below are tagged as either verified this way, or still resting on each project's self-reported docs.

> **Legend**
> 🟢 Best / Superior 🟡 Good / Standard 🔴 Below Requirement / Failed Constraint
> ✅ = confirmed via live side-by-side testing

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
│       ├── antigravity-flash-calculus/      # Built by Antigravity IDE (Gemini 3.6 Flash)
│       ├── calculus_engine_benchmark_runner.py  # 32-Equation SymPy Oracle Benchmark Runner
│       └── benchmark_32_results_oracle_graded.json # Official JSON Results Breakdown
├── main.py                                  # Unified execution entry point & dynamic multi-engine project loader
├── requirements.txt                         # Global dependencies
└── README.md
```

### 🔀 Running & Switching Between Engine Implementations

You can switch between any of the calculus builds under `all-projects/calculus/` or run the 32-equation benchmark directly from `main.py`:

```bash
# 1. Interactively select/switch engine:
python3 main.py --select

# 2. Run the 32-Equation SymPy Oracle Benchmark Suite:
python3 main.py --benchmark

# 3. Run a specific engine by name or alias:
python3 main.py -p flash                  # Minovative Mind CLI (Gemini 3.6 Flash CAS)
python3 main.py -p lite                   # Minovative Mind CLI (Flash Lite Engine - Active Default)
python3 main.py -p opus                   # Antigravity IDE (Claude Opus 4.6 TUI)
python3 main.py -p ag-flash               # Antigravity IDE (Gemini 3.6 Flash TUI)
python3 main.py -p pro                    # Antigravity IDE (Gemini 3.1 Pro Textual TUI)

# 4. Pass subcommands directly to selected engine:
python3 main.py -p flash diff "x^3 + sin(x)" -v x
python3 main.py -p lite diff "x^3 * sin(x)" -v x -s     # Flash Lite step-by-step breakdown
python3 main.py -p lite int "x^2" -l 0 -u 2             # Flash Lite Simpson's rule numerical integration
python3 main.py -p lite lim "sin(x)/x" -p 0             # Flash Lite limit estimation
python3 main.py -p lite tree "sin(2*x)"                 # Flash Lite AST tree visualization

# 5. List all available engines and shortcuts:
python3 main.py --list-projects
```

---

## ⚖️ Featured Showcase: Symbolic Calculus & TUI Engines

Five independent implementations of a **Symbolic Calculus Engine & Interactive Terminal User Interface (TUI)**, all built under a strict pure-Python, zero-dependency constraint:

1. **`mmcli-flash-calculus`** — Minovative Mind CLI (Gemini 3.6 Flash Full CAS Engine — `thinkingLevels` un-set, used built-in Google model default: **`MEDIUM`** out of `MINIMAL, LOW, MEDIUM, HIGH`)
2. **`mmcli-flash-lite-calculus`** — Minovative Mind CLI (Gemini 3.5 Flash-Lite Engine — `thinkingLevels` un-set, used built-in Google model default: **`MINIMAL`** out of `MINIMAL, LOW, MEDIUM, HIGH`)
3. **`antigravity-gemini-pro-calculus`** — Antigravity IDE, Gemini 3.1 Pro (High)
4. **`antigravity-opus-calculus`** — Antigravity IDE, Claude Opus 4.6 (Thinking)
5. **`antigravity-flash-calculus`** — Antigravity IDE, Gemini 3.6 Flash (High)

---

### 📊 Detailed Architectural & Feature Comparison Matrix

| Evaluation Metric            | `mmcli-flash-calculus`                                                                                                                                                                      | `mmcli-flash-lite-calculus`                                                                                                                                                                                                   | `antigravity-gemini-pro-calculus`                                                                                                 | `antigravity-opus-calculus`                                                                                                                                                                                                                 | `antigravity-flash-calculus`                                                                                                                                                              |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model Engine**             | Gemini 3.6 Flash (`thinkingLevels` un-set; built-in Google model default: **`MEDIUM`** out of `MINIMAL, LOW, MEDIUM, HIGH`)                                                                 | Gemini 3.5 Flash-Lite (`thinkingLevels` un-set; built-in Google model default: **`MINIMAL`** out of `MINIMAL, LOW, MEDIUM, HIGH`)                                                                                             | Gemini 3.1 Pro (High)                                                                                                             | Claude Opus 4.6 (Thinking)                                                                                                                                                                                                                  | Gemini 3.6 Flash (High)                                                                                                                                                                   |
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

### 🧪 32-Equation Oracle-Verified Benchmark Suite

A comprehensive 32-equation benchmark was executed across all 5 calculus engines using an independent SymPy ground-truth oracle runner (`all-projects/calculus/calculus_engine_benchmark_runner.py`). Every derivative, integral, limit, and boundary condition was graded with a single, uniform rubric across 8 mathematical categories:

```text
========================================================================================
Summary Table: 32-Equation Benchmark Suite Results (Strict Oracle Grading)
========================================================================================
Engine                                   | Full 32 Score | Diff-Only (28) | Unverifiable
----------------------------------------------------------------------------------------
mmcli-flash (Gemini 3.6 Flash Full CAS)   | 30/32 (93.8%) |  26/28 (92.9%) |      0
mmcli-flash-lite (Gemini 3.5 Flash-Lite)  | 29/32 (90.6%) |  26/28 (92.9%) |      0
antigravity-flash (Gemini 3.6 Flash)     | 26/32 (81.2%) |  26/28 (92.9%) |      0
antigravity-opus (Claude Opus 4.6)       | 19/32 (59.4%) |  19/28 (67.9%) |      0
antigravity-gemini-pro (Gemini 3.1 Pro)   | 11/32 (34.4%) |  11/28 (39.3%) |      0
========================================================================================
```

#### Category Breakdown Across 32 Test Equations

| Category                                   | Description                                                                                                       | `mmcli-flash 3.6` | `mmcli-flash-lite 3.5` | `antigravity-flash 3.6` | `antigravity-opus 4.6` | `antigravity-gemini-pro 3.1` |
| :----------------------------------------- | :---------------------------------------------------------------------------------------------------------------- | :---------------- | :--------------------- | :---------------------- | :--------------------- | :--------------------------- |
| **Cat 1: Polynomials (4 eq)**              | $x^5$, $(2x+5)^4$, negative exponents, products                                                                   | 🟢 4/4            | 🟢 4/4                 | 🟢 4/4                  | 🟢 4/4                 | 🟢 4/4                       |
| **Cat 2: Trigonometric (4 eq)**            | $\sin\cos$, $\tan(x^2+1)$, $\arcsin+\arccos$, $\tan^2+1$                                                          | 🔴 3/4            | 🟢 4/4                 | 🔴 3/4                  | 🔴 3/4                 | 🔴 2/4                       |
| **Cat 3: Exp & Log (4 eq)**                | $e^{3x}(x^2-2x+2)$, $\frac{\ln(x^2+1)}{x}$, $x^3\ln x$, $e^{-x^2}\cos x$                                          | 🟢 4/4            | 🟢 4/4                 | 🟢 4/4                  | 🔴 3/4                 | 🔴 0/4                       |
| **Cat 4: Product/Quotient (4 eq)**         | $\frac{x^2+1}{x^3-1}$, $\frac{\sin x}{\cos x + 1}$, $x^2 \sin x \ln x$, $\frac{e^x \sin x}{x^2+1}$                | 🟢 4/4            | 🟢 4/4                 | 🟢 4/4                  | 🟢 4/4                 | 🔴 0/4                       |
| **Cat 5: Nested Chain Rule (4 eq)**        | $\sin(\cos(\tan x))$, $\sqrt{1+\sin^2 x}$, $e^{\sqrt{x^2+4}}$, $\ln(\sin(x^3+1))$                                 | 🟢 4/4            | 🟢 4/4                 | 🟢 4/4                  | 🔴 2/4                 | 🔴 0/4                       |
| **Cat 6: Radicals (4 eq)**                 | $\sqrt{x^3+2x}$, $\frac{1}{\sqrt{4-x^2}}$, $(x^3+1)^{2/3}$, $\sqrt{x} \ln(\sqrt{x})$                              | 🟢 4/4            | 🟢 4/4                 | 🟢 4/4                  | 🔴 1/4                 | 🔴 0/4                       |
| **Cat 7: CAS Integration & Limits (4 eq)** | $\int (x^4-2x+1) dx$, $\int_0^3 x^2 dx$, $\lim_{x \to 0} \frac{\sin x}{x}$, $\lim_{x \to 0} \frac{1-\cos x}{x^2}$ | 🟢 4/4            | 🔴 3/4                 | 🔴 0/4                  | 🔴 0/4                 | 🔴 0/4                       |
| **Cat 8: Boundary & Errors (4 eq)**        | $x^2+\sin x$ (Unicode), bare `cos3x`, syntax `sin(x`, syntax `x=2`                                                | 🔴 3/4            | 🔴 2/4                 | 🔴 3/4                  | 🔴 2/4                 | 🟢 4/4                       |

---

## 📈 Key Takeaways

1. **3-Way Tie on Pure Differentiation (92.9% Diff-only) & Qualitative Tiebreaker**:
   - On the 28 pure differentiation cases (Categories 1-6 + 8), `mmcli-flash`, `mmcli-flash-lite`, and `antigravity-flash` tie at **26/28 (92.9%)**. However, inspecting _which_ 2 cases each engine missed reveals a clear qualitative distinction:
     - **`mmcli-flash` & `antigravity-flash`** missed **Case 7** (`asin(x)+acos(x)` due to no inverse trig nodes) and **Case 30** (`cos3x`). Crucially, both **passed Case 29** by safely rejecting non-ASCII input (`x²`) with an explicit `ValueError`.
     - **`mmcli-flash-lite`** was the **only engine** in the entire benchmark to pass **Case 7** (`asin(x)+acos(x)` with full `asin`/`acos`/`atan` node support). However, it missed **Case 29** by silently returning `cos(x)` (treating `x²` as an opaque token with derivative 0), alongside **Case 30** (`cos3x`).
   - **Tiebreaker Verdict:** `mmcli-flash-lite` wins on **Mathematical Function Scope** (10 functions including inverse trig), while `mmcli-flash` and `antigravity-flash` win on **Input Safety & Error Handling** (explicit `ValueError` rejection of non-ASCII input).
2. **`mmcli-flash-lite` Unicode Silent Failure Confirmed** — On Case 29 (`x² + sin(x)`), `mmcli-flash-lite` returned `cos(x)` (silently dropping `x²` as an opaque token with derivative 0), matching the exact silent failure mode of Opus and Gemini Pro.
3. **Opus Operator Precedence Bug Discovered** — In Case 12 (`exp(-x²)·cos(x)`), Claude Opus 4.6 parsed `-x^2` as `(-x)^2` = `x^2`, differentiating a different function without raising an error. This is a distinct operator precedence flaw independent of its `sqrt` function gap.
4. **Opus `sqrt` Gap Confirmed at Scale** — All 5 `sqrt`-containing cases (Cases 18, 19, 21, 22, 24) failed in Opus because its parser lacks `sqrt` node support, outputting unparseable variable multiplications like `(sqrt * (...))`.
5. **Strict Rubric (0 Unverifiable)** — Corrupt or unparseable output strings (such as `'(asin + acos)'` in Case 7 for engines lacking inverse trig support) are strictly graded as **FAIL** rather than inconclusive.
6. **Gemini 3.1 Pro API vs. TUI Behavior** — In Case 29, Gemini 3.1 Pro returned `cos(x)` under programmatic API calls, confirming disqualification with 21/32 total failures (34.4%).
7. **Thinking Budget Efficiency Impact** — All Antigravity IDE builds (`antigravity-flash`, `antigravity-opus`, `antigravity-gemini-pro`) were generated using **maximum `HIGH` / `Thinking`** thinking levels. In contrast, the `mmcli` builds ran with un-set default thinking budgets (Gemini 3.6 Flash at Google's built-in **`MEDIUM`** default, and Gemini 3.5 Flash-Lite at Google's built-in **`MINIMAL`** default). Despite operating on lower/default thinking levels, the `mmcli` builds achieved equal or higher overall scores (93.8% and 90.6% vs. 81.2%, 59.4%, and 34.4%), highlighting the architectural prompt-framing efficiency of the `mmcli` agent.

---

## 🏆 Scorecard (updated with 32-equation benchmark data)

### 🥇 Minovative Mind CLI (`mmcli-flash`): 9.2 / 10 — **BENCHMARK WINNER**

- **The Good:** Undisputed winner in features, CAS scope, and accuracy. Passed **30/32 equations (93.8%)** in the SymPy oracle benchmark. Live-tested and verified full CAS capabilities (indefinite/definite integration, L'Hôpital's Rule limit solver), zero runtime dependencies, LaTeX export, and 41/41 passing unit tests (`pytest`).
- **Thinking Level Configuration:** Built with `thinkingLevels` un-set, utilizing built-in Google model default **`MEDIUM`** thinking level (out of `MINIMAL, LOW, MEDIUM, HIGH`).

- **The Miss:** Shares the `cos3x` bare-function parsing limitation with Opus and Flash. Top-level `ast.py` naming requires custom loader.

- **Verdict:** **Superior overall engine.** Highest verified 32-equation accuracy and broadest CAS feature set.

### 🥈 Minovative Mind CLI Flash-Lite (`mmcli-flash-lite-calculus`): 9.0 / 10 — **BEST LIGHTWEIGHT ENGINE**

- **The Good:** 0-revision clean build with zero external dependencies. Passed **29/32 equations (90.6%)** overall and **26/28 (92.9%)** on differentiation. Fixed standard library import collisions by using `ast_nodes.py`. 16/16 passing unit tests (`pytest`). Features: symbolic differentiation, 15-pass algebraic simplification, numerical Simpson's rule definite integration, limit estimation, AST equation tree visualization (`tree`), step-by-step breakdown cards (`diff -s`), and interactive TUI. Default active engine in `main.py`.
- **Thinking Level Configuration:** Built with `thinkingLevels` un-set, utilizing built-in Google model default **`MINIMAL`** thinking level (out of `MINIMAL, LOW, MEDIUM, HIGH`).

- **The Miss:** Parses Unicode exponent characters (such as `x²`) as single variable tokens rather than power nodes, requiring standard ASCII `x^2` for exact power-rule differentiation.

- **Verdict:** **Best lightweight modular engine.** Cleanest package structure, zero namespace collisions, 90.6% 32-equation accuracy, and versatile CLI/TUI capabilities.

### 🥉 Gemini 3.6 Flash (Antigravity IDE): 8.2 / 10

- **The Good:** The strongest differentiation-only engine. Passed **26/32 equations (81.2%)** overall and **26/28 (92.9%)** on differentiation. Zero runtime dependencies, 13/13 passing tests (`pytest`), clean package structure (`core/ast.py`), and **superior error handling** — explicitly rejects unsupported Unicode characters (`ValueError: Unexpected character`) rather than computing a silent wrong answer.

- **The Miss:** Scope limited strictly to differentiation (no integration or limit engine). Shares the `cos3x` bare-function parsing limitation.

- **Verdict:** **Best lightweight differentiation engine.** Excellent input validation, clean modular design, and robust test suite.

### 4️⃣ Claude Opus 4.6 (Antigravity IDE): 6.0 / 10

- **The Good:** Flawless zero-revision build, zero runtime dependencies, and the most visually polished 3-pane Curses TUI interface.

- **The Miss:** Passed **19/32 equations (59.4%)**. Vulnerable to silent wrong answers: lacks `sqrt` node support (producing `sqrt * (...)` variable multiplication) and silently drops Unicode exponents/dots without error, calculating derivatives for different expressions.

- **Verdict:** **Best UI presentation, but vulnerable input validation.** Strong visual polish undercut by silent failure risks on radical functions and non-ASCII input.

### 🔴 Gemini 3.1 Pro (Antigravity IDE): 2.5 / 10 — **DISQUALIFIED**

- **The Good:** Comprehensive multi-pane TUI architecture plan on paper.

- **The Miss:** Failed **21/32 equations (34.4%)**, throwing `ParseError` on basic trigonometric and nested function syntax.

- **The Fatal:** Violated the zero-dependency constraint by requiring `textual` and `plotext`, suffered module shadowing (`ast.py` colliding with Python's standard `ast`), relative import bugs, and zero automated tests.

- **Verdict:** **Disqualified.** Failed core architectural constraints, dependency limits, and basic syntax parsing across the 32-equation suite.

---
