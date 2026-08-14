"""
Calculus Engine Textual Interactive TUI Application
===================================================
A modern, rich terminal user interface for interactive calculus exploration,
symbolic differentiation, step-by-step breakdown, AST inspection, and live plotting.
"""

from __future__ import annotations
import math
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Input, Button, Label, Static,
    TabbedContent, TabPane, Select
)
from textual.binding import Binding
from textual.reactive import reactive

from engine import parse_expr, ParseError, Node
from .widgets import (
    MathOverviewWidget,
    ASTTreeWidget,
    DerivationStepsWidget,
    GraphPlotWidget,
    CalculusAnalysisWidget
)


PRESETS = [
    ("Quotient & Chain: sin(x^2) / (x + 1)", "sin(x^2) / (x + 1)"),
    ("General Power: x^x", "x^x"),
    ("Damped Oscillator: exp(-x/2) * cos(3*x)", "exp(-x/2) * cos(3*x)"),
    ("Cubic Polynomial: x^3 - 3*x^2 + 2", "x^3 - 3*x^2 + 2"),
    ("Rational Function: (x^2 - 1) / (x^2 + 1)", "(x^2 - 1) / (x^2 + 1)"),
    ("Composite Trig: tan(sin(x))", "tan(sin(x))"),
    ("Logarithmic Chain: ln(x^2 + 2*x + 2)", "ln(x^2 + 2*x + 2)"),
    ("Gaussian Bell: exp(-x^2)", "exp(-x^2)"),
]


class CalculusTUIApp(App):
    """Textual interactive calculus application."""

    CSS = """
    Screen {
        background: #0f172a;
        color: #e2e8f0;
    }

    Header {
        background: #1e293b;
        color: #38bdf8;
        text-style: bold;
    }

    Footer {
        background: #1e293b;
        color: #94a3b8;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
    }

    #sidebar {
        width: 32;
        background: #1e293b;
        border-right: solid #334155;
        padding: 1;
    }

    #content-area {
        width: 1fr;
        padding: 1;
    }

    .section-title {
        text-style: bold;
        color: #f59e0b;
        margin-top: 1;
        margin-bottom: 0;
    }

    .field-label {
        color: #94a3b8;
        margin-top: 1;
    }

    Input {
        background: #0f172a;
        border: tall #38bdf8;
        color: #f8fafc;
        margin-bottom: 1;
    }

    Input:focus {
        border: tall #f59e0b;
    }

    #expr-input {
        width: 1fr;
        margin-right: 1;
    }

    .action-btn {
        margin-top: 1;
        width: 100%;
        background: #2563eb;
        color: white;
    }

    .action-btn:hover {
        background: #1d4ed8;
    }

    .zoom-btn {
        width: 50%;
        background: #475569;
    }

    #zoom-container {
        layout: horizontal;
        margin-top: 1;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1;
        height: 1fr;
    }

    #status-bar {
        height: 1;
        color: #22c55e;
        margin-bottom: 1;
    }

    .error-text {
        color: #ef4444;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("o", "show_tab('overview')", "Overview", show=True),
        Binding("t", "show_tab('ast')", "AST Tree", show=True),
        Binding("s", "show_tab('steps')", "Steps", show=True),
        Binding("p", "show_tab('plot')", "Plot", show=True),
        Binding("a", "show_tab('analysis')", "Analysis", show=True),
        Binding("ctrl+r", "refresh_all", "Refresh", show=True),
    ]

    current_expr_str = reactive("sin(x^2) / (x + 1)")
    current_var = reactive("x")
    current_x0 = reactive(1.0)
    current_order = reactive(1)
    current_xmin = reactive(-5.0)
    current_xmax = reactive(5.0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            # Sidebar
            with VerticalScroll(id="sidebar"):
                yield Label("⚡ CALCULUS CONTROLS", classes="section-title")
                
                yield Label("Preset Expressions:", classes="field-label")
                yield Select([(label, expr) for label, expr in PRESETS], prompt="Select a preset...", id="preset-select")
                
                yield Label("Target Variable:", classes="field-label")
                yield Input(value="x", id="var-input")

                yield Label("Derivative Order:", classes="field-label")
                yield Input(value="1", id="order-input")

                yield Label("Eval Point (x₀):", classes="field-label")
                yield Input(value="1.0", id="x0-input")

                yield Label("Plot Range (x_min, x_max):", classes="field-label")
                with Horizontal():
                    yield Input(value="-5.0", id="xmin-input")
                    yield Input(value="5.0", id="xmax-input")

                with Horizontal(id="zoom-container"):
                    yield Button("Zoom In (+)", id="btn-zoom-in", classes="zoom-btn")
                    yield Button("Zoom Out (-)", id="btn-zoom-out", classes="zoom-btn")

                yield Button("Recalculate", id="btn-recalc", classes="action-btn")

            # Main content area
            with Vertical(id="content-area"):
                with Horizontal():
                    yield Input(value=self.current_expr_str, placeholder="Enter math formula, e.g. sin(x^2)/(x+1)", id="expr-input")
                    yield Button("Differentiate", id="btn-diff", variant="primary")

                yield Static("Status: Ready", id="status-bar")

                with TabbedContent(initial="overview", id="tabs"):
                    with TabPane("Overview (O)", id="overview"):
                        yield MathOverviewWidget(id="overview-widget")
                    with TabPane("AST Tree (T)", id="ast"):
                        yield ASTTreeWidget(id="ast-widget")
                    with TabPane("Derivation Steps (S)", id="steps"):
                        yield DerivationStepsWidget(id="steps-widget")
                    with TabPane("Graph Plot (P)", id="plot"):
                        yield GraphPlotWidget(id="plot-widget")
                    with TabPane("Calculus Analysis (A)", id="analysis"):
                        yield CalculusAnalysisWidget(id="analysis-widget")

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Antigravity 3.7 Symbolic Calculus Engine"
        self.sub_title = "AST & Recursive Differentiation TUI"
        self._update_all_widgets()

    def action_show_tab(self, tab_id: str) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = tab_id

    def action_refresh_all(self) -> None:
        self._update_all_widgets()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._read_inputs_and_update()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id in ("btn-diff", "btn-recalc"):
            self._read_inputs_and_update()
        elif btn_id == "btn-zoom-in":
            span = (self.current_xmax - self.current_xmin) * 0.25
            self.current_xmin += span
            self.current_xmax -= span
            self.query_one("#xmin-input", Input).value = f"{self.current_xmin:.2f}"
            self.query_one("#xmax-input", Input).value = f"{self.current_xmax:.2f}"
            self._update_all_widgets()
        elif btn_id == "btn-zoom-out":
            span = (self.current_xmax - self.current_xmin) * 0.33
            self.current_xmin -= span
            self.current_xmax += span
            self.query_one("#xmin-input", Input).value = f"{self.current_xmin:.2f}"
            self.query_one("#xmax-input", Input).value = f"{self.current_xmax:.2f}"
            self._update_all_widgets()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value != Select.BLANK:
            self.query_one("#expr-input", Input).value = str(event.value)
            self._read_inputs_and_update()

    def _read_inputs_and_update(self) -> None:
        expr_input = self.query_one("#expr-input", Input)
        var_input = self.query_one("#var-input", Input)
        order_input = self.query_one("#order-input", Input)
        x0_input = self.query_one("#x0-input", Input)
        xmin_input = self.query_one("#xmin-input", Input)
        xmax_input = self.query_one("#xmax-input", Input)

        self.current_expr_str = expr_input.value.strip() or "x"
        self.current_var = var_input.value.strip() or "x"

        try:
            self.current_order = max(1, int(order_input.value.strip()))
        except ValueError:
            self.current_order = 1

        try:
            self.current_x0 = float(x0_input.value.strip())
        except ValueError:
            self.current_x0 = 1.0

        try:
            self.current_xmin = float(xmin_input.value.strip())
            self.current_xmax = float(xmax_input.value.strip())
            if self.current_xmin >= self.current_xmax:
                self.current_xmax = self.current_xmin + 1.0
        except ValueError:
            self.current_xmin = -5.0
            self.current_xmax = 5.0

        self._update_all_widgets()

    def _update_all_widgets(self) -> None:
        status_bar = self.query_one("#status-bar", Static)
        try:
            expr = parse_expr(self.current_expr_str)
            status_bar.update(f"[bold green]✓ Expression Parsed Successfully: {expr.to_infix()}[/bold green]")
        except ParseError as e:
            status_bar.update(f"[bold red]✗ Syntax Error: {e.message}[/bold red]")
            return
        except Exception as e:
            status_bar.update(f"[bold red]✗ Error: {e}[/bold red]")
            return

        # Update all 5 widgets
        overview_widget = self.query_one("#overview-widget", MathOverviewWidget)
        overview_widget.update_expression(
            expr,
            var=self.current_var,
            x0=self.current_x0,
            order=self.current_order
        )

        ast_widget = self.query_one("#ast-widget", ASTTreeWidget)
        ast_widget.update_tree(expr)

        steps_widget = self.query_one("#steps-widget", DerivationStepsWidget)
        steps_widget.update_steps(
            expr,
            var=self.current_var,
            order=self.current_order
        )

        plot_widget = self.query_one("#plot-widget", GraphPlotWidget)
        plot_widget.update_plot(
            expr,
            var=self.current_var,
            x0=self.current_x0,
            x_min=self.current_xmin,
            x_max=self.current_xmax,
            width=68,
            height=15
        )

        analysis_widget = self.query_one("#analysis-widget", CalculusAnalysisWidget)
        analysis_widget.update_analysis(
            expr,
            var=self.current_var,
            x0=self.current_x0,
            x_min=self.current_xmin,
            x_max=self.current_xmax
        )


def run_tui() -> None:
    app = CalculusTUIApp()
    app.run()
