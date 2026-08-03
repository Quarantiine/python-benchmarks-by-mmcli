# Python Practice & AI Agentic Benchmarks (`python-practice`)

Welcome to **Python Practice**, a repository showcasing production-ready Python projects built from scratch by **Minovative Mind CLI (`mmcli`)**—our custom autonomous AI agentic engineering CLI—and comparative benchmarks against other state-of-the-art AI models and IDE agents (Antigravity IDE powered by Gemini 3.1 Pro, Gemini 3.6 Flash, and Anthropic Claude Opus 4.6).

This README has been updated after a **live verification round**: instead of relying only on each build's own documentation, the same test expressions were run interactively against all four builds and compared side by side. Claims below are now tagged as either verified this way, or still resting on each project's self-reported docs.

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
│       ├── mmcli-agent-calculus/            # Built by Minovative Mind CLI (mmcli)
│       ├── antigravity-gemini-pro-calculus/ # Built by Antigravity IDE (Gemini 3.1 Pro)
│       ├── antigravity-opus-calculus/       # Built by Antigravity IDE (Opus 4.6)
│       └── antigravity-flash-calculus/      # Built by Antigravity IDE (Gemini 3.6 Flash)
├── main.py                                  # Unified execution entry point & dynamic importlib loader
├── requirements.txt                         # Global dependencies
└── README.md
```

---

## ⚖️ Featured Showcase: Symbolic Calculus & TUI Engines

Four independent implementations of a **Symbolic Calculus Engine & Interactive Terminal User Interface (TUI)**, all built under a strict pure-Python, zero-dependency constraint:

1. **`mmcli-agent-calculus`** — Minovative Mind CLI (Gemini 3.5 Flash-Lite / 3.6 Flash mix)
2. **`antigravity-gemini-pro-calculus`** — Antigravity IDE, Gemini 3.1 Pro (Thinking High)
3. **`antigravity-opus-calculus`** — Antigravity IDE, Claude Opus 4.6 (Thinking High)
4. **`antigravity-flash-calculus`** — Antigravity IDE, Gemini 3.6 Flash (High)

---

### 📊 Detailed Architectural & Feature Comparison Matrix

| Evaluation Metric            | `mmcli-agent-calculus`                                                                                                                                                                                                         | `antigravity-gemini-pro-calculus`                                                                                                    | `antigravity-opus-calculus`                                                                                                                                                                                                                       | `antigravity-flash-calculus`                                                                                                                                                                 |
| :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model Engine**             | Gemini 3.5 Flash-Lite / 3.6 Flash                                                                                                                                                                                              | Gemini 3.1 Pro (High)                                                                                                                | Claude Opus 4.6 (Thinking High)                                                                                                                                                                                                                   | Gemini 3.6 Flash (High)                                                                                                                                                                      |
| **First-Try Success**        | 🟢 0 Revisions (Clean build)                                                                                                                                                                                                   | 🔴 3 Revisions during build, **and** ✅ still failed to parse the live benchmark expression in _any_ format afterward — disqualified | 🟢 0 Revisions (Flawless execution)                                                                                                                                                                                                               | 🟢 0 Revisions (Clean build)                                                                                                                                                                 |
| **Dependency Discipline**    | 🟢 Zero Runtime Dependencies ✅                                                                                                                                                                                                | 🔴 Failed Constraint (`textual`, `plotext`) ✅                                                                                       | 🟢 Zero Runtime Dependencies ✅                                                                                                                                                                                                                   | 🟢 Zero Runtime Dependencies ✅                                                                                                                                                              |
| **Supported Math Functions** | 🟢 8 functions (`sin,cos,tan,exp,ln,log,sqrt,abs`)                                                                                                                                                                             | 🔴 2 functions only                                                                                                                  | 🟡 5 functions                                                                                                                                                                                                                                    | 🟢 7 functions                                                                                                                                                                               |
| **Parser Capabilities**      | 🟡 Implicit multiplication, 8 functions — **but** ✅ silently misparses a bare function name without explicit parens (`cos3x` is read as one opaque symbol, not `cos(3x)`)                                                     | 🔴 ✅ Could not parse the live benchmark expression at all, in either Unicode or plain ASCII form                                    | 🟡 Implicit multiplication, 5 functions — **but** ✅ shares the identical `cos3x` misparse bug, **and** ✅ separately dropped Unicode superscript/dot characters on paste, silently differentiating a different, simpler expression with no error | 🟢 ✅ Correctly parsed `cos(3x)` and the full test expression on the one live test run; not yet tried against the Unicode-paste or bare-function-name failure modes that broke the other two |
| **Interface & TUI Engine**   | 🟢 Curses TUI + text fallback + CLI subcommands                                                                                                                                                                                | 🔴 Textual multi-pane layout (violates dependency constraint)                                                                        | 🟢 3-pane Curses layout (AST / Steps / Graph), most polished visually ✅                                                                                                                                                                          | 🟡 ANSI/Unicode menu TUI + `--demo` mode, with the clearest per-rule step cards ✅                                                                                                           |
| **CLI Subcommand Support**   | 🟢 `diff, int, lim, simplify, eval, tree`                                                                                                                                                                                      | 🔴 Interactive TUI launcher only                                                                                                     | 🔴 Interactive Curses TUI launcher only                                                                                                                                                                                                           | 🟡 Interactive menu + `--demo` flag                                                                                                                                                          |
| **LaTeX & Export Support**   | 🟢 Only build with LaTeX + Unicode export                                                                                                                                                                                      | 🔴 None                                                                                                                              | 🔴 None                                                                                                                                                                                                                                           | 🔴 None                                                                                                                                                                                      |
| **Simplification Depth**     | 🟡 Cleans trivial `*1`/`+0` terms — **but** ✅ on the live test, left the same uncancelled common `(x³+2x)` factor as Opus and Flash. No evidence yet that any of the three has a genuinely deeper simplifier than the others. | 🔴 Untested (disqualified before reaching this stage)                                                                                | 🟡 Same uncancelled-factor result as mmcli and Flash ✅                                                                                                                                                                                           | 🟡 Same uncancelled-factor result as mmcli and Opus ✅                                                                                                                                       |
| **Calculus Subsystems**      | 🟢 ✅ Verified full CAS: indefinite/definite integration & limits via L'Hôpital's Rule (`lim(x->0) sin(x²cos(3x))/(x³+2x)² = 0.25`)                                                                                            | 🔴 Differentiation only, and that couldn't be verified either                                                                        | 🟡 Differentiation only (no integration/limits attempted)                                                                                                                                                                                         | 🟡 Differentiation only (no integration/limits attempted)                                                                                                                                    |
| **Module Naming Safety**     | 🟡 Top-level `ast.py`, bypassed via custom `importlib` loader                                                                                                                                                                  | 🟡 Renamed to `math_ast.py` after collision                                                                                          | 🟢 `nodes.py`, avoided collision by naming choice                                                                                                                                                                                                 | 🟢 `core/ast.py`, package-isolated                                                                                                                                                           |
| **Automated Test Coverage**  | 🟢 ✅ Verified 41/41 passing (`pytest`)                                                                                                                                                                                        | 🔴 No test suite                                                                                                                     | 🔴 No test suite                                                                                                                                                                                                                                  | 🟢 ✅ Verified 13/13 passing (`pytest`)                                                                                                                                                      |

---

## 🧪 Live Verification Round (this session)

Four tests were run identically across the builds still in contention, using the shared expression:

$$\frac{\sin(x^2 \cos(3x))}{(x^3 + 2x)^2}$$

| Test                                                | mmcli                                                                                                       | Opus 4.6                                                                                            | Gemini 3.6 Flash                                                                           | Gemini 3.1 Pro                                     |
| :-------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- | :------------------------------------------------- |
| **Unicode input** (`x²`, `x³`, `·` pasted directly) | Rejected outright, required ASCII reformat                                                                  | Silently dropped the exponents/dot and differentiated a different, simpler function with no warning | Explicitly rejected with clean error (`ValueError: Unexpected character in expression: ²`) | Rejected — never got a valid parse in this session |
| **Correct ASCII syntax** (`x^2`, `cos(3x)`, `^2`)   | ✅ Correct — matched hand-derived answer                                                                    | ✅ Correct — matched mmcli exactly                                                                  | ✅ Correct — matched mmcli and Opus exactly                                                | Still failed to parse                              |
| **Bare function name, no parens** (`cos3x`)         | ✅ Bug confirmed: parsed as opaque symbol, dropped the entire chain-rule term for `cos(3x)`, no error shown | ✅ Identical bug to mmcli                                                                           | ✅ Identical bug to mmcli & Opus (parsed as opaque variable `cos3x`, derivative = 0)       | N/A — disqualified before this round               |
| **Direct substitution syntax** (`x = 0`)            | Correctly threw a syntax error (expression grammar doesn't accept `=`)                                      | Correctly threw a syntax error — same, appropriate behavior                                         | Not tested                                                                                 | N/A                                                |
| **Indefinite Integral** (`∫ x² dx`)                 | ✅ Correct (`x³ / 3 + C`)                                                                                   | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **Definite Integral** (`∫_0^2 x² dx`)               | ✅ Correct (`2.6666666666666665`)                                                                           | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **L'Hôpital Limit** (`lim_{x->0} sin(x)/x`)         | ✅ Correct (`1.0`)                                                                                          | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |
| **Benchmark Singularity Limit at x=0**              | ✅ Correct (`0.25` via L'Hôpital's Rule on $\frac{\sin(x^2 \cos(3x))}{(x^3 + 2x)^2}$)                       | N/A (not implemented)                                                                               | N/A (not implemented)                                                                      | N/A                                                |

**Net result:** mmcli is the only build that successfully implemented and verified full CAS capabilities beyond differentiation—including indefinite integrals, definite integrals, and indeterminate limits using L'Hôpital's Rule.

---

## 📈 Key Takeaways

1. **Zero-Dependency Discipline vs. Framework Hallucination** — confirmed: `mmcli`, Opus, and Flash all honored the zero-dependency constraint; Gemini 3.1 Pro failed by pulling in `textual` and `plotext`.
2. **Automated Test Coverage Verified** — ran `pytest` across all test suites, independently verifying 54/54 passing tests (41/41 for `mmcli` and 13/13 for `antigravity-flash`).
3. **Full CAS Scope Proven for `mmcli`** — live terminal testing confirmed indefinite integration (`∫ x² dx = x³/3 + C`), definite integration (`∫_0^2 x² dx = 8/3`), and indeterminate limits via L'Hôpital's Rule (`lim_{x->0} sin(x²cos(3x))/(x³+2x)² = 0.25`).
4. **Input Error Handling Distinguishes Models** — Gemini 3.6 Flash cleanly rejects unsupported Unicode input with explicit `ValueError`, whereas Opus silently drops symbols and computes wrong derivatives.
5. **Shared Parsing Limitation** — All differentiation engines (`mmcli`, Opus, Flash) share an identical parsing behavior for bare function names without parentheses (`cos3x` is parsed as variable `cos3x` with derivative 0).

---

## 🏆 Scorecard (updated after live verification round)

### 🥇 Minovative Mind CLI (`mmcli`): 8.8 / 10 — **BENCHMARK WINNER**

- **The Good:** Undisputed winner in features, CAS scope, and test coverage. Live-tested and verified full CAS capabilities (indefinite/definite integration, L'Hôpital's Rule limit solver, step-by-step breakdowns), zero runtime dependencies, multi-format rendering (LaTeX, Unicode, AST Tree), and 41/41 passing tests (`pytest`).

- **The Miss:** Shares the `cos3x` bare-function parsing limitation with Opus and Flash (parsed as variable `cos3x` with derivative 0).

- **Verdict:** **Superior overall engine.** Broadest math scope, richest feature set, and highest verified test coverage.

### 🥈 Gemini 3.6 Flash (Antigravity IDE): 8 / 10

- **The Good:** The strongest differentiation-only engine. Zero runtime dependencies, 13/13 passing tests (`pytest`), clean package structure (`core/ast.py`), and **superior error handling** — explicitly rejects unsupported Unicode characters (`ValueError: Unexpected character`) rather than computing a silent wrong answer.

- **The Miss:** Scope limited strictly to differentiation (no integration or limit engine). Shares the `cos3x` bare-function parsing limitation.

- **Verdict:** **Best lightweight differentiation engine.** Excellent input validation, clean modular design, and robust test suite.

### 🥉 Claude Opus 4.6 (Antigravity IDE): 6.2 / 10

- **The Good:** Flawless zero-revision build, zero runtime dependencies, and the most visually polished 3-pane Curses TUI interface.

- **The Miss:** **Vulnerable to silent wrong answers:** silently drops Unicode exponents/dots without error, calculating a derivative for a completely different expression. Zero automated tests and differentiation-only scope.

- **Verdict:** **Best UI presentation, but vulnerable input validation.** Strong visual polish undercut by silent failure risks on non-ASCII input and lack of test suite.

### 🔴 Gemini 3.1 Pro (Antigravity IDE): 2.5 / 10 — **DISQUALIFIED**

- **The Good:** Comprehensive multi-pane TUI architecture plan on paper.

- **The Fatal:** Failed the zero-dependency constraint by installing `textual` and `plotext`, suffered module shadowing (`ast.py` colliding with Python's standard `ast`), relative import bugs, and zero automated tests.

- **Verdict:** **Disqualified.** Failed core architectural constraints and required manual code fixes to run.

---
