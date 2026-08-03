from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static, Tree as TextualTree
from textual.reactive import reactive
import plotext as plt

from parser import parse_expr, ParseError
from math_ast import Node

class GraphWidget(Static):
    def plot(self, ast_node: Node, var_name: str = "x"):
        plt.clf()
        # Generate x values
        # we'll plot from -10 to 10
        x_vals = [i/10 for i in range(-100, 101)]
        y_vals = []
        for x in x_vals:
            env = {var_name: x}
            val = ast_node.evaluate(env)
            # handle inf, nan, etc.
            if isinstance(val, complex):
                val = float('nan')
            y_vals.append(val)
        
        # Determine terminal size, roughly
        w, h = self.size.width or 80, self.size.height or 24
        
        plt.plotsize(max(10, w - 2), max(10, h - 2))
        plt.plot(x_vals, y_vals, marker="dot", color="blue")
        plt.title(f"y = {ast_node}")
        plt.theme('dark')
        ansi = plt.build()
        self.update(ansi)


class CalculusApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #input-container {
        height: 3;
        margin: 1;
    }
    #main-content {
        layout: horizontal;
        height: 1fr;
    }
    .pane {
        width: 1fr;
        height: 1fr;
        border: solid green;
        padding: 1;
    }
    #tree-pane {
        width: 1fr;
    }
    #steps-pane {
        width: 1.5fr;
    }
    #graph-pane {
        width: 2fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="input-container"):
            yield Input(placeholder="Enter a mathematical expression (e.g., x^2 * sin(x))", id="expr-input")
        
        with Horizontal(id="main-content"):
            with Vertical(id="tree-pane", classes="pane"):
                yield Static("[b]AST Visualizer[/b]")
                yield TextualTree("AST")
            
            with Vertical(id="steps-pane", classes="pane"):
                yield Static("[b]Derivation Steps[/b]")
                yield Static("", id="steps-output")
                
            with Vertical(id="graph-pane", classes="pane"):
                yield Static("[b]Graph[/b]")
                yield GraphWidget("", id="graph-output")
        
        yield Footer()

    def populate_tree(self, node: Node, tree_widget: TextualTree):
        tree_widget.clear()
        
        from math_ast import (
            ConstNode, VarNode, AddNode, SubNode, 
            MulNode, DivNode, PowNode, SinNode, CosNode
        )
        
        def _build(ast_node, textual_node):
            if isinstance(ast_node, ConstNode):
                textual_node.add(f"[cyan]Const[/cyan]: {ast_node.value}")
            elif isinstance(ast_node, VarNode):
                textual_node.add(f"[green]Var[/green]: {ast_node.name}")
            elif isinstance(ast_node, AddNode):
                n = textual_node.add("[yellow]+[/yellow]")
                _build(ast_node.left, n)
                _build(ast_node.right, n)
            elif isinstance(ast_node, SubNode):
                n = textual_node.add("[yellow]-[/yellow]")
                _build(ast_node.left, n)
                _build(ast_node.right, n)
            elif isinstance(ast_node, MulNode):
                n = textual_node.add("[yellow]*[/yellow]")
                _build(ast_node.left, n)
                _build(ast_node.right, n)
            elif isinstance(ast_node, DivNode):
                n = textual_node.add("[yellow]/[/yellow]")
                _build(ast_node.left, n)
                _build(ast_node.right, n)
            elif isinstance(ast_node, PowNode):
                n = textual_node.add("[yellow]^[/yellow]")
                _build(ast_node.left, n)
                _build(ast_node.right, n)
            elif isinstance(ast_node, SinNode):
                n = textual_node.add("[magenta]sin[/magenta]")
                _build(ast_node.inner, n)
            elif isinstance(ast_node, CosNode):
                n = textual_node.add("[magenta]cos[/magenta]")
                _build(ast_node.inner, n)
                
        # Start at the root of the Textual Tree
        _build(node, tree_widget.root)
        tree_widget.root.expand_all()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        expr_str = event.value
        try:
            ast = parse_expr(expr_str)
            
            # 1. Update AST Tree
            tree_widget = self.query_one(TextualTree)
            self.populate_tree(ast, tree_widget)
            
            # 2. Compute Derivative and Steps
            steps = []
            steps.append(f"[b]1. Original Expression:[/b]\n   {ast}\n")
            
            unsimplified_deriv = ast.differentiate("x")
            steps.append(f"[b]2. Raw Derivative:[/b]\n   {unsimplified_deriv}\n")
            
            simplified_deriv = unsimplified_deriv.simplify()
            steps.append(f"[b]3. Simplified Derivative:[/b]\n   {simplified_deriv}\n")
            
            steps_out = self.query_one("#steps-output", Static)
            steps_out.update("\n".join(steps))
            
            # 3. Update Graph (Plot original function)
            graph_out = self.query_one("#graph-output", GraphWidget)
            graph_out.plot(ast, "x")
            
        except ParseError as e:
            self.query_one("#steps-output", Static).update(f"[red]Parse Error:[/red] {e}")
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            self.query_one("#steps-output", Static).update(f"[red]Error:[/red]\n{err}")

if __name__ == "__main__":
    app = CalculusApp()
    app.run()
