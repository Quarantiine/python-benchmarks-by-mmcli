"""
Unicode Braille & Terminal Graph Plotter
========================================
High-resolution 2D terminal plotting using Unicode Braille patterns (2x4 dot subpixels),
multi-curve support, line rasterization, axis drawing, and ANSI/Rich color rendering.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Optional, Tuple, Union
from .ast_nodes import Node


class PlotCanvas:
    """
    Braille 2D Canvas with 2x4 subpixel resolution per terminal character cell.
    """

    # Braille dot bitmask offsets: (sub_row, sub_col) -> bitmask
    # sub_row in 0..3, sub_col in 0..1
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
        y_max: Optional[float] = None
    ) -> None:
        self.char_width = max(20, width)
        self.char_height = max(10, height)
        self.pixel_width = self.char_width * 2
        self.pixel_height = self.char_height * 4

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        # Grid of bitmasks for characters
        self.grid = [[0 for _ in range(self.char_width)] for _ in range(self.char_height)]
        # Grid of colors (store dominant curve color per cell)
        self.color_grid: List[List[Optional[str]]] = [
            [None for _ in range(self.char_width)] for _ in range(self.char_height)
        ]

    def set_pixel(self, px: int, py: int, color: Optional[str] = None) -> None:
        if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
            cx = px // 2
            # py=0 is top in terminal, but mathematically we want py=0 at bottom or top:
            # Let py=0 be top of screen
            cy = py // 4
            sub_x = px % 2
            sub_y = py % 4
            self.grid[cy][cx] |= self.BRAILLE_MAP[(sub_y, sub_x)]
            if color:
                self.color_grid[cy][cx] = color

    def draw_line(self, px0: int, py0: int, px1: int, py1: int, color: Optional[str] = None) -> None:
        """Bresenham line algorithm on subpixel grid."""
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
        px = int(((x - self.x_min) / (self.x_max - self.x_min)) * (self.pixel_width - 1))
        # Mathematical y: y_max is top (py=0), y_min is bottom (py=pixel_height-1)
        py = int(((self.y_max - y) / (self.y_max - self.y_min)) * (self.pixel_height - 1))
        return px, py

    def add_curve(
        self,
        func: Callable[[float], float],
        color: Optional[str] = None,
        samples: int = 400
    ) -> None:
        """Sample and draw a mathematical curve on the canvas."""
        step = (self.x_max - self.x_min) / max(1, samples - 1)
        points: List[Tuple[float, float]] = []

        for i in range(samples):
            x = self.x_min + i * step
            try:
                y = func(x)
                if not (math.isnan(y) or math.isinf(y)):
                    points.append((x, y))
                else:
                    points.append((x, float('nan')))
            except Exception:
                points.append((x, float('nan')))

        prev_px, prev_py = None, None
        for x, y in points:
            if math.isnan(y):
                prev_px, prev_py = None, None
                continue

            # Skip vertical asymptote spikes
            if y < self.y_min - (self.y_max - self.y_min) or y > self.y_max + (self.y_max - self.y_min):
                prev_px, prev_py = None, None
                continue

            px, py = self._world_to_pixel(x, y)
            if prev_px is not None and prev_py is not None:
                # If gap is not gigantic (discontinuity filter)
                if abs(py - prev_py) < self.pixel_height * 0.8:
                    self.draw_line(prev_px, prev_py, px, py, color)
                else:
                    self.set_pixel(px, py, color)
            else:
                self.set_pixel(px, py, color)

            prev_px, prev_py = px, py

    def render_lines(self) -> List[str]:
        """Render canvas grid into formatted terminal strings."""
        lines: List[str] = []
        y_label_width = 8

        # Determine y-axis tick positions
        for r in range(self.char_height):
            # Calculate corresponding y value for tick label
            y_val = self.y_max - (r / max(1, self.char_height - 1)) * (self.y_max - self.y_min)
            
            if r == 0:
                y_str = f"{self.y_max:7.2f} │"
            elif r == self.char_height - 1:
                y_str = f"{self.y_min:7.2f} │"
            elif r == self.char_height // 2:
                mid_y = (self.y_max + self.y_min) / 2.0
                y_str = f"{mid_y:7.2f} ┼"
            else:
                y_str = f"{' ':7s} │"

            row_chars = []
            for c in range(self.char_width):
                mask = self.grid[r][c]
                color = self.color_grid[r][c]
                ch = chr(0x2800 | mask) if mask != 0 else " "
                
                # If axis zero crosses here and character is blank, put faint axis marker
                if ch == " ":
                    is_y_axis = (self.x_min <= 0 <= self.x_max) and (
                        c == int((-self.x_min / (self.x_max - self.x_min)) * (self.char_width - 1))
                    )
                    is_x_axis = (self.y_min <= 0 <= self.y_max) and (
                        r == int((self.y_max / (self.y_max - self.y_min)) * (self.char_height - 1))
                    )
                    if is_x_axis and is_y_axis:
                        ch = "┼"
                    elif is_x_axis:
                        ch = "─"
                    elif is_y_axis:
                        ch = "│"

                if color and mask != 0:
                    row_chars.append(f"[{color}]{ch}[/{color}]")
                else:
                    row_chars.append(ch)

            lines.append(y_str + "".join(row_chars))

        # Bottom x-axis line
        axis_line = " " * y_label_width + "└" + "─" * self.char_width
        lines.append(axis_line)

        # X tick labels
        x_min_str = f"{self.x_min:.2f}"
        x_max_str = f"{self.x_max:.2f}"
        mid_x = (self.x_min + self.x_max) / 2.0
        x_mid_str = f"{mid_x:.2f}"

        spacing1 = (self.char_width // 2) - len(x_min_str)
        spacing2 = (self.char_width - (self.char_width // 2)) - len(x_max_str) - len(x_mid_str)
        
        spacing1 = max(1, spacing1)
        spacing2 = max(1, spacing2)

        x_ticks = " " * (y_label_width + 1) + x_min_str + " " * spacing1 + x_mid_str + " " * spacing2 + x_max_str
        lines.append(x_ticks)

        return lines


def plot_functions(
    curves: List[Tuple[Callable[[float], float], str, str]],  # (func, label, color)
    x_min: float = -5.0,
    x_max: float = 5.0,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    width: int = 70,
    height: int = 20
) -> str:
    """
    Plot multiple functions on a single terminal Braille canvas with a legend.
    curves: list of tuples (func, label_text, color_name)
    """
    # If y_min or y_max is not specified, auto-scale from samples
    if y_min is None or y_max is None:
        samples_y: List[float] = []
        for func, _, _ in curves:
            for i in range(100):
                x = x_min + i * (x_max - x_min) / 99.0
                try:
                    y = func(x)
                    if not (math.isnan(y) or math.isinf(y)) and abs(y) < 1e5:
                        samples_y.append(y)
                except Exception:
                    pass

        if samples_y:
            auto_ymin = min(samples_y)
            auto_ymax = max(samples_y)
            # Add 10% padding
            pad = max(0.5, (auto_ymax - auto_ymin) * 0.1)
            y_min = y_min if y_min is not None else (auto_ymin - pad)
            y_max = y_max if y_max is not None else (auto_ymax + pad)
        else:
            y_min = -5.0
            y_max = 5.0

    if y_min >= y_max:
        y_max = y_min + 1.0

    canvas = PlotCanvas(width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

    for func, _, color in curves:
        canvas.add_curve(func, color=color)

    lines = canvas.render_lines()

    # Add legend at the top
    legend_parts = []
    for _, label, color in curves:
        legend_parts.append(f"[{color}]── {label}[/{color}]")
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
    height: int = 20
) -> str:
    """Plot an AST expression and its derivative."""
    from .simplifier import simplify
    
    f_func = lambda x: expr.evaluate({var: x})
    curves = [(f_func, f"f({var}) = {expr.to_infix()}", "cyan")]

    if include_derivative:
        d_expr = simplify(expr.differentiate(var))
        df_func = lambda x: d_expr.evaluate({var: x})
        curves.append((df_func, f"f'({var}) = {d_expr.to_infix()}", "yellow"))

    return plot_functions(curves, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, width=width, height=height)


def render_braille_plot(
    expr: Node,
    var: str = "x",
    d_expr: Optional[Node] = None,
    d2_expr: Optional[Node] = None,
    x_min: float = -5.0,
    x_max: float = 5.0,
    width: int = 70,
    height: int = 20
) -> str:
    """Convenient helper for plotting up to 3 functions."""
    curves = [(lambda x: expr.evaluate({var: x}), f"f({var}) = {expr}", "cyan")]
    if d_expr is not None:
        curves.append((lambda x: d_expr.evaluate({var: x}), f"f'({var}) = {d_expr}", "yellow"))
    if d2_expr is not None:
        curves.append((lambda x: d2_expr.evaluate({var: x}), f"f''({var}) = {d2_expr}", "magenta"))
        
    return plot_functions(curves, x_min=x_min, x_max=x_max, width=width, height=height)
