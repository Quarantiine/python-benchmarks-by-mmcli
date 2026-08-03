"""Real-time ASCII/Unicode Terminal Function Graph Plotter for f(x) and f'(x)."""

import math
from typing import List, Optional, Tuple

from core.ast import Node


def render_ascii_plot(
    f_node: Node,
    df_node: Optional[Node] = None,
    var_name: str = "x",
    x_min: float = -5.0,
    x_max: float = 5.0,
    width: int = 65,
    height: int = 21,
) -> str:
    """Render a text grid plotting f(x) (using '*') and optionally f'(x) (using '#')."""
    if x_min >= x_max:
        x_min, x_max = -5.0, 5.0

    x_step = (x_max - x_min) / (width - 1)

    # Sample values
    x_vals = [x_min + i * x_step for i in range(width)]
    f_vals = []
    df_vals = []

    for x in x_vals:
        try:
            val = f_node.evaluate({var_name: x})
            f_vals.append(
                val
                if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val)
                else None
            )
        except Exception:
            f_vals.append(None)

        if df_node:
            try:
                val_df = df_node.evaluate({var_name: x})
                df_vals.append(
                    val_df
                    if isinstance(val_df, (int, float))
                    and not math.isnan(val_df)
                    and not math.isinf(val_df)
                    else None
                )
            except Exception:
                df_vals.append(None)

    # Filter out valid values to determine y range
    valid_y = [v for v in f_vals if v is not None]
    if df_node:
        valid_y.extend([v for v in df_vals if v is not None])

    if not valid_y:
        y_min, y_max = -5.0, 5.0
    else:
        y_min, y_max = min(valid_y), max(valid_y)
        if y_min == y_max:
            y_min -= 1.0
            y_max += 1.0

    # Add 10% margin on y
    y_margin = (y_max - y_min) * 0.08
    y_min -= y_margin
    y_max += y_margin

    y_step = (y_max - y_min) / (height - 1)

    # Initialize grid canvas with space
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Draw Y axis if within x bounds
    y_axis_col = None
    if x_min <= 0 <= x_max:
        y_axis_col = int(round((0 - x_min) / x_step))
        if 0 <= y_axis_col < width:
            for r in range(height):
                grid[r][y_axis_col] = "│"

    # Draw X axis if within y bounds
    x_axis_row = None
    if y_min <= 0 <= y_max:
        x_axis_row = int(round((y_max - 0) / y_step))
        if 0 <= x_axis_row < height:
            for c in range(width):
                grid[x_axis_row][c] = (
                    "┼" if y_axis_col is not None and c == y_axis_col else "─"
                )

    # Plot f(x) with '*'
    for c, y_val in enumerate(f_vals):
        if y_val is not None and y_min <= y_val <= y_max:
            r = int(round((y_max - y_val) / y_step))
            if 0 <= r < height:
                grid[r][c] = "*"

    # Plot f'(x) with '#'
    if df_node:
        for c, y_val in enumerate(df_vals):
            if y_val is not None and y_min <= y_val <= y_max:
                r = int(round((y_max - y_val) / y_step))
                if 0 <= r < height:
                    if grid[r][c] == "*":
                        grid[r][c] = "@"  # Overlap point
                    else:
                        grid[r][c] = "#"

    # Build output string
    lines = []
    lines.append(f"┌─ Terminal Graph Plotter ───────────────────────────────────────────┐")
    lines.append(f"│  f({var_name})  = {str(f_node)}")
    if df_node:
        lines.append(f"│  f'({var_name}) = {str(df_node)}")
    lines.append(f"├────────────────────────────────────────────────────────────────────┤")

    # Render grid rows with Y axis labels
    for r in range(height):
        # Calculate Y value for row label
        cur_y = y_max - r * y_step
        r_label = f"{cur_y:6.2f} │ "
        r_content = "".join(grid[r])
        lines.append(r_label + r_content)

    # X axis footer label
    x_label_start = f"{x_min:6.2f}"
    x_label_mid = f"0.00" if x_min <= 0 <= x_max else f"{(x_min+x_max)/2:6.2f}"
    x_label_end = f"{x_max:6.2f}"
    padding = " " * ((width - len(x_label_start) - len(x_label_end) - len(x_label_mid)) // 2)
    lines.append("       └" + "─" * width)
    lines.append("        " + x_label_start + padding + x_label_mid + padding + x_label_end)
    lines.append(f"├────────────────────────────────────────────────────────────────────┤")
    lines.append(f"│ Legend: [*] f({var_name})   [#] f'({var_name})   [@] Overlap               │")
    lines.append(f"└────────────────────────────────────────────────────────────────────┘")

    return "\n".join(lines)
