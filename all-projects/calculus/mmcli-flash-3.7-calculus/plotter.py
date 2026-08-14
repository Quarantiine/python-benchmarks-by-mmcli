"""
Unicode Braille & ASCII Terminal Curve Plotter
==============================================
High-resolution 2D terminal plotting using Unicode Braille patterns (2x4 dot subpixels)
and standard ASCII characters, multi-curve plotting, Bresenham line rasterization,
asymptote detection, axis drawing, and color formatting.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Optional, Tuple, Union

try:
    from ast_nodes import Node
except ImportError:
    from .ast_nodes import Node


class PlotCanvas:
    """
    Braille 2D Canvas with 2x4 subpixel resolution per terminal character cell.
    Subpixel indices within a character cell:
      (row 0, col 0) -> 0x01   (row 0, col 1) -> 0x08
      (row 1, col 0) -> 0x02   (row 1, col 1) -> 0x10
      (row 2, col 0) -> 0x04   (row 2, col 1) -> 0x20
      (row 3, col 0) -> 0x40   (row 3, col 1) -> 0x80
    """

    BRAILLE_MAP = {
        (0, 0): 0x01,
        (1, 0): 0x02,
        (2, 0): 0x04,
        (0, 1): 0x08,
        (1, 1): 0x10,
        (2, 1): 0x20,
        (3, 0): 0x40,
        (3, 1): 0x80,
    }

    def __init__(
        self,
        width: int = 70,
        height: int = 20,
        x_min: float = -5.0,
        x_max: float = 5.0,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
    ) -> None:
        self.char_width = max(10, width)
        self.char_height = max(5, height)
        self.pixel_width = self.char_width * 2
        self.pixel_height = self.char_height * 4

        self.x_min = float(x_min)
        self.x_max = float(x_max)
        if self.x_min >= self.x_max:
            self.x_max = self.x_min + 1.0

        self.y_min = float(y_min) if y_min is not None else -5.0
        self.y_max = float(y_max) if y_max is not None else 5.0
        if self.y_min >= self.y_max:
            self.y_max = self.y_min + 1.0

        # 2D Grid of character bitmasks
        self.grid: List[List[int]] = [
            [0 for _ in range(self.char_width)] for _ in range(self.char_height)
        ]
        # Dominant color / style per character cell
        self.color_grid: List[List[Optional[str]]] = [
            [None for _ in range(self.char_width)] for _ in range(self.char_height)
        ]

    def set_pixel(self, px: int, py: int, color: Optional[str] = None) -> None:
        """Set a single subpixel at (px, py) on the subpixel grid."""
        if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
            cx = px // 2
            cy = py // 4
            sub_x = px % 2
            sub_y = py % 4
            self.grid[cy][cx] |= self.BRAILLE_MAP[(sub_y, sub_x)]
            if color:
                self.color_grid[cy][cx] = color

    def draw_line(
        self, px0: int, py0: int, px1: int, py1: int, color: Optional[str] = None
    ) -> None:
        """Rasterize a line between two subpixel points using Bresenham's algorithm."""
        dx = abs(px1 - px0)
        dy = abs(py1 - py0)
        sx = 1 if px0 < px1 else -1
        sy = 1 if py0 < py1 else -1
        err = dx - dy

        while True:
            self.set_pixel(px0, py0, color)
            if px0 == px1 and py0 == py1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                px0 += sx
            if e2 < dx:
                err += dx
                py0 += sy

    def _world_to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        """Convert mathematical Cartesian coordinates (x, y) to subpixel integer coordinates."""
        px = int(((x - self.x_min) / (self.x_max - self.x_min)) * (self.pixel_width - 1))
        # Mathematical y: y_max is top (py = 0), y_min is bottom (py = pixel_height - 1)
        py = int(((self.y_max - y) / (self.y_max - self.y_min)) * (self.pixel_height - 1))
        return px, py

    def add_curve(
        self,
        func: Callable[[float], float],
        color: Optional[str] = None,
        samples: int = 400,
        label: Optional[str] = None,
    ) -> None:
        """Sample a mathematical function and rasterize its curve onto the canvas."""
        step = (self.x_max - self.x_min) / max(1, samples - 1)
        points: List[Tuple[float, float]] = []

        for i in range(samples):
            x = self.x_min + i * step
            try:
                y = func(x)
                if isinstance(y, complex):
                    y = y.real
                if math.isnan(y) or math.isinf(y):
                    points.append((x, float("nan")))
                else:
                    points.append((x, float(y)))
            except Exception:
                points.append((x, float("nan")))

        y_range = self.y_max - self.y_min
        prev_px: Optional[int] = None
        prev_py: Optional[int] = None

        for x, y in points:
            if math.isnan(y):
                prev_px, prev_py = None, None
                continue

            # Check if point is severely out of bounds (asymptote spike)
            if y < self.y_min - y_range * 2.0 or y > self.y_max + y_range * 2.0:
                prev_px, prev_py = None, None
                continue

            px, py = self._world_to_pixel(x, y)

            if prev_px is not None and prev_py is not None:
                # If vertical jump is too steep across 1 step (likely asymptote discontinuity)
                if abs(py - prev_py) < self.pixel_height * 0.75:
                    self.draw_line(prev_px, prev_py, px, py, color)
                else:
                    self.set_pixel(px, py, color)
            else:
                self.set_pixel(px, py, color)

            prev_px, prev_py = px, py

    def render_lines(self, use_color: bool = True) -> List[str]:
        """Render the canvas grid into formatted terminal lines."""
        lines: List[str] = []
        y_label_width = 8

        # Calculate axis positions on the character grid
        x_axis_char_row = None
        if self.y_min <= 0 <= self.y_max:
            x_axis_char_row = int(
                ((self.y_max - 0.0) / (self.y_max - self.y_min)) * (self.char_height - 1)
            )

        y_axis_char_col = None
        if self.x_min <= 0 <= self.x_max:
            y_axis_char_col = int(
                ((0.0 - self.x_min) / (self.x_max - self.x_min)) * (self.char_width - 1)
            )

        for r in range(self.char_height):
            # Generate Y tick labels
            if r == 0:
                y_str = f"{self.y_max:7.2f} │"
            elif r == self.char_height - 1:
                y_str = f"{self.y_min:7.2f} │"
            elif r == self.char_height // 2:
                mid_y = (self.y_max + self.y_min) / 2.0
                y_str = f"{mid_y:7.2f} ┼"
            else:
                y_str = f"{' ':7s} │"

            row_chars: List[str] = []
            for c in range(self.char_width):
                mask = self.grid[r][c]
                color = self.color_grid[r][c]

                if mask != 0:
                    ch = chr(0x2800 | mask)
                else:
                    # Draw subtle axis lines when blank
                    is_x = (x_axis_char_row is not None and r == x_axis_char_row)
                    is_y = (y_axis_char_col is not None and c == y_axis_char_col)
                    if is_x and is_y:
                        ch = "┼"
                    elif is_x:
                        ch = "─"
                    elif is_y:
                        ch = "│"
                    else:
                        ch = " "

                if use_color and color and mask != 0:
                    row_chars.append(f"[{color}]{ch}[/{color}]")
                else:
                    row_chars.append(ch)

            lines.append(y_str + "".join(row_chars))

        # Bottom axis border
        axis_line = " " * y_label_width + "└" + "─" * self.char_width
        lines.append(axis_line)

        # X tick label line
        x_min_str = f"{self.x_min:.2f}"
        x_max_str = f"{self.x_max:.2f}"
        mid_x = (self.x_min + self.x_max) / 2.0
        x_mid_str = f"{mid_x:.2f}"

        spacing1 = max(1, (self.char_width // 2) - len(x_min_str))
        spacing2 = max(
            1,
            (self.char_width - (self.char_width // 2)) - len(x_max_str) - len(x_mid_str),
        )

        x_ticks = (
            " " * (y_label_width + 1)
            + x_min_str
            + " " * spacing1
            + x_mid_str
            + " " * spacing2
            + x_max_str
        )
        lines.append(x_ticks)

        return lines


class AsciiCanvas:
    """
    Standard ASCII 2D Canvas for environments without Braille font support.
    """

    DEFAULT_SYMBOLS = ["*", "o", "+", "#", "x", "@", "~"]

    def __init__(
        self,
        width: int = 60,
        height: int = 18,
        x_min: float = -5.0,
        x_max: float = 5.0,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
    ) -> None:
        self.width = max(10, width)
        self.height = max(5, height)
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        if self.x_min >= self.x_max:
            self.x_max = self.x_min + 1.0

        self.y_min = float(y_min) if y_min is not None else -5.0
        self.y_max = float(y_max) if y_max is not None else 5.0
        if self.y_min >= self.y_max:
            self.y_max = self.y_min + 1.0

        self.grid: List[List[str]] = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]
        self._init_axes()

    def _init_axes(self) -> None:
        """Initialize Cartesian axis lines."""
        if self.y_min <= 0 <= self.y_max:
            y_zero_row = int(
                ((self.y_max - 0.0) / (self.y_max - self.y_min)) * (self.height - 1)
            )
            for c in range(self.width):
                self.grid[y_zero_row][c] = "-"

        if self.x_min <= 0 <= self.x_max:
            x_zero_col = int(
                ((0.0 - self.x_min) / (self.x_max - self.x_min)) * (self.width - 1)
            )
            for r in range(self.height):
                if self.grid[r][x_zero_col] == "-":
                    self.grid[r][x_zero_col] = "+"
                else:
                    self.grid[r][x_zero_col] = "|"

    def add_curve(
        self,
        func: Callable[[float], float],
        symbol: str = "*",
        samples: int = 150,
        label: Optional[str] = None,
    ) -> None:
        """Sample function and place ASCII marker symbols on grid."""
        step = (self.x_max - self.x_min) / max(1, samples - 1)
        for i in range(samples):
            x = self.x_min + i * step
            try:
                y = func(x)
                if isinstance(y, complex):
                    y = y.real
                if math.isnan(y) or math.isinf(y):
                    continue
                if self.y_min <= y <= self.y_max:
                    col = int(((x - self.x_min) / (self.x_max - self.x_min)) * (self.width - 1))
                    row = int(((self.y_max - y) / (self.y_max - self.y_min)) * (self.height - 1))
                    if 0 <= row < self.height and 0 <= col < self.width:
                        self.grid[row][col] = symbol
            except Exception:
                continue

    def render_lines(self) -> List[str]:
        """Render grid into formatted ASCII lines with labels."""
        lines: List[str] = []
        for r in range(self.height):
            if r == 0:
                y_lbl = f"{self.y_max:7.2f} |"
            elif r == self.height - 1:
                y_lbl = f"{self.y_min:7.2f} |"
            elif r == self.height // 2:
                mid_y = (self.y_max + self.y_min) / 2.0
                y_lbl = f"{mid_y:7.2f} +"
            else:
                y_lbl = f"{' ':7s} |"

            lines.append(y_lbl + "".join(self.grid[r]))

        # Bottom border
        lines.append(" " * 8 + "+" + "-" * self.width)
        x_min_str = f"{self.x_min:.2f}"
        x_max_str = f"{self.x_max:.2f}"
        mid_x_str = f"{(self.x_min + self.x_max) / 2.0:.2f}"
        spacing = max(1, (self.width // 2) - len(x_min_str))
        spacing2 = max(1, self.width - (self.width // 2) - len(mid_x_str) - len(x_max_str))
        lines.append(" " * 9 + x_min_str + " " * spacing + mid_x_str + " " * spacing2 + x_max_str)
        return lines


def auto_scale_y(
    curves: List[Tuple[Callable[[float], float], str, str]],
    x_min: float,
    x_max: float,
    samples_per_curve: int = 100,
) -> Tuple[float, float]:
    """Calculate intelligent y_min and y_max based on curve sampling."""
    samples_y: List[float] = []
    step = (x_max - x_min) / max(1, samples_per_curve - 1)

    for func, _, _ in curves:
        for i in range(samples_per_curve):
            x = x_min + i * step
            try:
                y = func(x)
                if isinstance(y, complex):
                    y = y.real
                if not (math.isnan(y) or math.isinf(y)) and abs(y) < 1e6:
                    samples_y.append(float(y))
            except Exception:
                pass

    if not samples_y:
        return -5.0, 5.0

    # Filter extreme outliers using percentiles
    samples_y.sort()
    n = len(samples_y)
    p05_idx = int(n * 0.02)
    p95_idx = min(n - 1, int(n * 0.98))
    
    y_low = samples_y[p05_idx]
    y_high = samples_y[p95_idx]

    if y_low >= y_high:
        y_low -= 1.0
        y_high += 1.0

    pad = max(0.5, (y_high - y_low) * 0.1)
    return y_low - pad, y_high + pad


def plot_functions(
    curves: List[Tuple[Callable[[float], float], str, str]],  # (func, label, color)
    x_min: float = -5.0,
    x_max: float = 5.0,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    width: int = 70,
    height: int = 20,
    ascii_mode: bool = False,
    use_color: bool = True,
) -> str:
    """
    Plot multiple mathematical functions on a single terminal canvas with a legend.
    curves: list of tuples (func, label_text, color_name)
    """
    if y_min is None or y_max is None:
        auto_ymin, auto_ymax = auto_scale_y(curves, x_min, x_max)
        y_min = y_min if y_min is not None else auto_ymin
        y_max = y_max if y_max is not None else auto_ymax

    if y_min >= y_max:
        y_max = y_min + 1.0

    if ascii_mode:
        canvas = AsciiCanvas(
            width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
        )
        symbols = ["*", "o", "+", "#", "x", "@", "~"]
        legend_parts = []
        for idx, (func, label, _) in enumerate(curves):
            sym = symbols[idx % len(symbols)]
            canvas.add_curve(func, symbol=sym)
            legend_parts.append(f"[{sym}] {label}")
        legend = "   ".join(legend_parts)
        lines = canvas.render_lines()
        return f"\n{legend}\n" + "\n".join(lines)
    else:
        canvas = PlotCanvas(
            width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
        )
        legend_parts = []
        for func, label, color in curves:
            canvas.add_curve(func, color=color)
            if use_color and color:
                legend_parts.append(f"[{color}]── {label}[/{color}]")
            else:
                legend_parts.append(f"── {label}")

        lines = canvas.render_lines(use_color=use_color)
        legend = "   ".join(legend_parts)
        return f"\n{legend}\n" + "\n".join(lines)


def plot_expression(
    expr: Node,
    var: str = "x",
    include_derivative: bool = True,
    x_min: float = -5.0,
    x_max: float = 5.0,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    width: int = 70,
    height: int = 20,
    ascii_mode: bool = False,
) -> str:
    """Plot an AST expression f(x) and optionally its derivative f'(x)."""
    from simplifier import simplify

    f_func = lambda x: expr.evaluate({var: x})
    curves: List[Tuple[Callable[[float], float], str, str]] = [
        (f_func, f"f({var}) = {expr.to_infix()}", "cyan")
    ]

    if include_derivative:
        d_expr = simplify(expr.differentiate(var))
        df_func = lambda x: d_expr.evaluate({var: x})
        curves.append((df_func, f"f'({var}) = {d_expr.to_infix()}", "yellow"))

    return plot_functions(
        curves,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height,
        ascii_mode=ascii_mode,
    )


def render_braille_plot(
    expr: Node,
    var: str = "x",
    d_expr: Optional[Node] = None,
    d2_expr: Optional[Node] = None,
    tangent_fn: Optional[Callable[[float], float]] = None,
    x_min: float = -5.0,
    x_max: float = 5.0,
    width: int = 70,
    height: int = 20,
) -> str:
    """Convenient helper for plotting f(x), f'(x), f''(x), and tangent lines with Unicode Braille."""
    curves = [(lambda x: expr.evaluate({var: x}), f"f({var}) = {expr}", "cyan")]
    if d_expr is not None:
        curves.append(
            (lambda x: d_expr.evaluate({var: x}), f"f'({var}) = {d_expr}", "yellow")
        )
    if d2_expr is not None:
        curves.append(
            (lambda x: d2_expr.evaluate({var: x}), f"f''({var}) = {d2_expr}", "magenta")
        )
    if tangent_fn is not None:
        curves.append(
            (tangent_fn, "tangent", "green")
        )

    return plot_functions(curves, x_min=x_min, x_max=x_max, width=width, height=height)


def render_ascii_plot(
    expr: Node,
    var: str = "x",
    d_expr: Optional[Node] = None,
    x_min: float = -5.0,
    x_max: float = 5.0,
    width: int = 60,
    height: int = 18,
) -> str:
    """Convenient helper for plotting f(x) and f'(x) in pure ASCII."""
    curves = [(lambda x: expr.evaluate({var: x}), f"f({var}) = {expr}", "cyan")]
    if d_expr is not None:
        curves.append(
            (lambda x: d_expr.evaluate({var: x}), f"f'({var}) = {d_expr}", "yellow")
        )
    return plot_functions(
        curves, x_min=x_min, x_max=x_max, width=width, height=height, ascii_mode=True
    )


def plot_curve(
    func: Callable[[float], float],
    label: str = "f(x)",
    x_min: float = -5.0,
    x_max: float = 5.0,
    width: int = 70,
    height: int = 20,
    ascii_mode: bool = False,
) -> str:
    """Plot a single callable curve."""
    return plot_functions(
        [(func, label, "cyan")],
        x_min=x_min,
        x_max=x_max,
        width=width,
        height=height,
        ascii_mode=ascii_mode,
    )
