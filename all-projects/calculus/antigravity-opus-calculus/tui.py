"""
Curses-based Terminal User Interface for the Symbolic Calculus Engine.
Zero external dependencies — uses only the Python standard library.

Layout:
  ┌─── ∫ Symbolic Calculus Engine ─────────────────────────┐
  │ f(x) = [expression input]                              │
  ├────────────┬────────────────────┬───────────────────────┤
  │ AST Tree   │ Derivation Steps   │ Graph                 │
  ├────────────┴────────────────────┴───────────────────────┤
  │ ESC Quit │ Enter Compute │ Ctrl+U Clear                 │
  └─────────────────────────────────────────────────────────┘
"""
import curses
import math
import locale

try:
    from .parser import parse, ParseError
    from .nodes import (Add, Sub, Mul, Div, Pow,
                        Sin, Cos, Tan, Ln, Exp, Const)
except ImportError:
    from parser import parse, ParseError
    from nodes import (Add, Sub, Mul, Div, Pow,
                       Sin, Cos, Tan, Ln, Exp, Const)


# ═══════════════════════════════════════════════════════════════
#  Safe curses helpers (swallow out-of-bounds writes)
# ═══════════════════════════════════════════════════════════════

def _put(win, row, col, text, attr=0):
    """Write a string to the window, ignoring overflow errors."""
    try:
        h, w = win.getmaxyx()
        if row < 0 or row >= h or col < 0 or col >= w:
            return
        maxn = w - col - 1
        if maxn > 0:
            win.addnstr(row, col, str(text), maxn, attr)
    except curses.error:
        pass


def _putch(win, row, col, ch, attr=0):
    """Write a single character, ignoring overflow errors."""
    try:
        h, w = win.getmaxyx()
        if 0 <= row < h and 0 <= col < w - 1:
            win.addch(row, col, ch, attr)
    except curses.error:
        pass


# ═══════════════════════════════════════════════════════════════
#  ASCII Graph Plotter (zero dependencies)
# ═══════════════════════════════════════════════════════════════

def _plot(expr, width, height, x_min=-10.0, x_max=10.0):
    """Return a list of strings rendering f(x) as an ASCII graph."""
    if width < 8 or height < 3:
        return ["(too small)"]

    label_w = 8                       # "  123.4┤"
    plot_w = max(3, width - label_w)

    # ── Sample the function ──
    xs = [x_min + i * (x_max - x_min) / max(1, plot_w - 1)
          for i in range(plot_w)]
    ys = []
    for x in xs:
        try:
            y = expr.evaluate({"x": x})
            if not isinstance(y, (int, float)) or not math.isfinite(y):
                y = None
        except Exception:
            y = None
        ys.append(y)

    valid = [y for y in ys if y is not None]
    if not valid:
        return ["  (no plottable data)"]

    # ── Compute y-range (percentile-based to handle outliers) ──
    sv = sorted(valid)
    n = len(sv)
    y_lo = sv[max(0, int(n * 0.02))]
    y_hi = sv[min(n - 1, int(n * 0.98))]
    pad = max(abs(y_hi - y_lo) * 0.1, 0.5)
    y_bot, y_top = y_lo - pad, y_hi + pad
    y_range = y_top - y_bot
    if y_range == 0:
        y_range = 1.0

    # ── Build character grid ──
    grid = [[" "] * plot_w for _ in range(height)]

    # Draw x-axis (y=0)
    zero_row = None
    if y_bot <= 0 <= y_top:
        zero_row = int((y_top - 0) / y_range * (height - 1))
        zero_row = max(0, min(height - 1, zero_row))
        for c in range(plot_w):
            grid[zero_row][c] = "─"

    # Draw y-axis (x=0)
    if x_min <= 0 <= x_max:
        c0 = int((0 - x_min) / (x_max - x_min) * (plot_w - 1))
        c0 = max(0, min(plot_w - 1, c0))
        for r in range(height):
            grid[r][c0] = "┼" if grid[r][c0] == "─" else "│"

    # ── Plot data points + interpolate gaps ──
    prev_row = None
    for i, y in enumerate(ys):
        if y is None:
            prev_row = None
            continue
        yc = max(y_bot, min(y_top, y))
        row = int((y_top - yc) / y_range * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][i] = "●"

        # Fill vertical gaps between consecutive points
        if prev_row is not None and abs(row - prev_row) > 1:
            step = 1 if row > prev_row else -1
            for r in range(prev_row + step, row, step):
                if 0 <= r < height and grid[r][max(0, i - 1)] == " ":
                    grid[r][max(0, i - 1)] = "·"
        prev_row = row

    # ── Build output lines with y-axis labels ──
    lines = []
    for r in range(height):
        yv = y_top - r * y_range / max(1, height - 1)
        if r == 0 or r == height - 1 or r == zero_row:
            label = f"{yv:>7.1f}┤"
        else:
            label = "       │"
        lines.append(label + "".join(grid[r]))

    # X-axis tick labels
    xl = " " * label_w
    xl += f"{x_min:<.0f}"
    xl += " " * max(0, plot_w - 6)
    xl += f"{x_max:>.0f}"
    lines.append(xl)

    return lines


# ═══════════════════════════════════════════════════════════════
#  Step-by-Step Derivation Generator
# ═══════════════════════════════════════════════════════════════

def _rule_name(expr):
    """Return a human-readable rule string for the top-level node."""
    if isinstance(expr, Add):
        return "Sum: (u+v)' = u' + v'"
    if isinstance(expr, Sub):
        return "Difference: (u-v)' = u' - v'"
    if isinstance(expr, Mul):
        return "Product: (uv)' = u'v + uv'"
    if isinstance(expr, Div):
        return "Quotient: (u/v)' = (u'v-uv')/v\u00b2"
    if isinstance(expr, Pow):
        if isinstance(expr.right, Const):
            return "Power: (u^n)' = n\u00b7u^(n-1)\u00b7u'"
        return "General power rule"
    if isinstance(expr, Sin):
        return "Chain: sin'(u) = cos(u)\u00b7u'"
    if isinstance(expr, Cos):
        return "Chain: cos'(u) = -sin(u)\u00b7u'"
    if isinstance(expr, Tan):
        return "Chain: tan'(u) = sec\u00b2(u)\u00b7u'"
    if isinstance(expr, Ln):
        return "Chain: ln'(u) = u'/u"
    if isinstance(expr, Exp):
        return "Chain: exp'(u) = exp(u)\u00b7u'"
    return None


def _wrap(text, width):
    """Hard-wrap text into chunks of at most `width` characters."""
    if not text:
        return [""]
    chunks = []
    while text:
        chunks.append(text[:width])
        text = text[width:]
    return chunks


def _steps(expr, var="x"):
    """Generate step-by-step derivation lines and the simplified result."""
    lines = []
    lines.append("f(x) = " + str(expr))
    lines.append("")

    rule = _rule_name(expr)
    if rule:
        lines.append("Rule: " + rule)
        lines.append("")

    # Show sub-expressions for context
    if hasattr(expr, "left") and hasattr(expr, "right"):
        lines.append("  u = " + str(expr.left))
        lines.append("  v = " + str(expr.right))
        lines.append("")
    elif hasattr(expr, "arg"):
        lines.append("  inner = " + str(expr.arg))
        lines.append("")

    # Raw derivative
    raw = expr.differentiate(var)
    lines.append("Raw derivative:")
    for chunk in _wrap(str(raw), 36):
        lines.append("  " + chunk)
    lines.append("")

    # Simplified
    simplified = raw.deep_simplify()
    lines.append("Simplified:")
    for chunk in _wrap(str(simplified), 36):
        lines.append("  " + chunk)

    return lines, simplified


# ═══════════════════════════════════════════════════════════════
#  Welcome Message
# ═══════════════════════════════════════════════════════════════

WELCOME = [
    "Welcome to the Calculus Engine!",
    "",
    "Type an expression above and",
    "press Enter to differentiate.",
    "",
    "Examples:",
    "  x^2 * sin(x)",
    "  cos(x) / (x + 1)",
    "  5*x^3 - 2*x + 7",
    "  tan(x)",
    "  ln(x^2 + 1)",
    "  exp(-x^2)",
    "  2x        (implicit mult.)",
    "",
    "Constants: pi, e",
]


# ═══════════════════════════════════════════════════════════════
#  Main TUI Loop
# ═══════════════════════════════════════════════════════════════

def run_tui():
    """Launch the interactive terminal UI."""
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(_loop)


def _loop(stdscr):
    """Core event loop running inside curses.wrapper."""
    curses.curs_set(1)
    stdscr.keypad(True)
    try:
        curses.set_escdelay(25)
    except AttributeError:
        pass

    # ── Colors ──
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK

    curses.init_pair(1, curses.COLOR_GREEN, bg)    # borders
    curses.init_pair(2, curses.COLOR_CYAN, bg)     # headers
    curses.init_pair(3, curses.COLOR_YELLOW, bg)   # highlights
    curses.init_pair(4, curses.COLOR_WHITE, bg)    # normal text
    curses.init_pair(5, curses.COLOR_RED, bg)      # errors

    CB = curses.color_pair(1)                      # border
    CH = curses.color_pair(2) | curses.A_BOLD      # header
    CY = curses.color_pair(3)                      # highlight
    CN = curses.color_pair(4)                      # normal
    CE = curses.color_pair(5) | curses.A_BOLD      # error

    # ── State ──
    expr_str = ""
    cpos = 0               # cursor position in expr_str
    ast_lines = []         # rendered AST tree
    step_lines = list(WELCOME)
    graph_lines = []
    err = ""

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Minimum size guard
        if h < 8 or w < 50:
            _put(stdscr, 0, 0, "Resize terminal (min 50x8)", CE)
            stdscr.refresh()
            k = stdscr.getch()
            if k == 27:
                break
            continue

        # ── Row 0 : Title Bar ──
        _put(stdscr, 0, 0, "\u2500" * w, CB)
        title = " \u222b Symbolic Calculus Engine "
        _put(stdscr, 0, max(0, (w - len(title)) // 2),
             title, CB | curses.A_BOLD)

        # ── Row 1 : Input Field ──
        lbl = " f(x) = "
        _put(stdscr, 1, 0, lbl, CH)
        iw = w - len(lbl) - 1
        vs = 0
        if iw > 0:
            vs = max(0, cpos - iw + 1) if cpos >= iw else 0
            vis = expr_str[vs:vs + iw]
            _put(stdscr, 1, len(lbl), vis, CN)

        # ── Row 2 : Separator ──
        _put(stdscr, 2, 0, "\u2500" * w, CB)

        # ── Content Area (rows 3 .. h-2) ──
        ct = 3                       # content top
        ch_ = h - 4                  # content height
        if ch_ < 2:
            ch_ = 2

        c1 = max(12, w * 25 // 100)  # AST width
        c2 = max(14, w * 35 // 100)  # Steps width
        c3 = max(14, w - c1 - c2)    # Graph width

        # Vertical dividers
        for r in range(ct, ct + ch_):
            _putch(stdscr, r, c1 - 1, "\u2502", CB)
            _putch(stdscr, r, c1 + c2 - 1, "\u2502", CB)

        # Panel headers (row ct)
        _put(stdscr, ct, 1, "AST Tree", CH)
        _put(stdscr, ct, c1 + 1, "Derivation Steps", CH)
        _put(stdscr, ct, c1 + c2 + 1, "Graph", CH)

        # Header underline (row ct+1)
        for col in range(w):
            _putch(stdscr, ct + 1, col, "\u2500", CB)
        _putch(stdscr, ct + 1, c1 - 1, "\u253c", CB)
        _putch(stdscr, ct + 1, c1 + c2 - 1, "\u253c", CB)

        rt = ct + 2                  # render top
        rh = ch_ - 2                 # render height
        if rh < 1:
            rh = 1

        # ── AST Panel ──
        for i, line in enumerate(ast_lines[:rh]):
            _put(stdscr, rt + i, 1, line[:c1 - 3], CN)

        # ── Steps Panel ──
        if err:
            _put(stdscr, rt, c1 + 1, err[:c2 - 3], CE)
        else:
            for i, line in enumerate(step_lines[:rh]):
                _put(stdscr, rt + i, c1 + 1, line[:c2 - 3], CN)

        # ── Graph Panel ──
        for i, line in enumerate(graph_lines[:rh]):
            _put(stdscr, rt + i, c1 + c2 + 1, line[:c3 - 2], CN)

        # ── Status Bar (row h-1) ──
        _put(stdscr, h - 1, 0, "\u2500" * w, CB)
        bar = " ESC Quit \u2502 Enter Compute \u2502 Ctrl+U Clear "
        _put(stdscr, h - 1, max(0, (w - len(bar)) // 2), bar, CY)

        # ── Position hardware cursor on input ──
        if iw > 0:
            cx = len(lbl) + cpos - vs
            try:
                if 0 <= cx < w:
                    stdscr.move(1, cx)
            except curses.error:
                pass

        stdscr.refresh()

        # ── Read Key ──
        try:
            k = stdscr.getch()
        except KeyboardInterrupt:
            break

        # ── Dispatch ──

        if k == 27:                             # ESC → quit
            break

        elif k in (10, 13, curses.KEY_ENTER):   # Enter → compute
            err = ""
            ast_lines = []
            step_lines = []
            graph_lines = []
            text = expr_str.strip()
            if not text:
                step_lines = list(WELCOME)
                continue
            try:
                ast = parse(text)

                # AST tree
                ast_lines = ast.tree_lines(is_root=True)

                # Derivation steps
                step_lines, _ = _steps(ast)

                # Graph
                gw = c3 - 2
                gh = max(3, rh - 1)
                if gw > 10 and gh > 3:
                    graph_lines = _plot(ast, gw, gh)

            except ParseError as e:
                err = f"Parse error: {e}"
            except Exception as e:
                err = f"Error: {e}"

        elif k == 21:                           # Ctrl+U → clear
            expr_str = ""
            cpos = 0
            ast_lines = []
            step_lines = list(WELCOME)
            graph_lines = []
            err = ""

        elif k in (curses.KEY_BACKSPACE, 127, 8):
            if cpos > 0:
                expr_str = expr_str[:cpos - 1] + expr_str[cpos:]
                cpos -= 1

        elif k == curses.KEY_DC:                # Delete key
            if cpos < len(expr_str):
                expr_str = expr_str[:cpos] + expr_str[cpos + 1:]

        elif k == curses.KEY_LEFT:
            cpos = max(0, cpos - 1)

        elif k == curses.KEY_RIGHT:
            cpos = min(len(expr_str), cpos + 1)

        elif k in (curses.KEY_HOME, 1):         # Home / Ctrl+A
            cpos = 0

        elif k in (curses.KEY_END, 5):          # End / Ctrl+E
            cpos = len(expr_str)

        elif k == curses.KEY_RESIZE:
            pass                                # re-render next loop

        elif 32 <= k < 127:                     # printable char
            expr_str = expr_str[:cpos] + chr(k) + expr_str[cpos:]
            cpos += 1
