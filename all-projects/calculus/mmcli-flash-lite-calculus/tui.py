"""
Terminal User Interface (TUI), ASCII/Unicode equation tree rendering,
step-by-step derivation breakdowns, expression evaluation, and interactive TUI loop.
"""

import sys
import math
from calculus.parser import parse_expression
from calculus.engine import differentiate, simplify
from calculus.ast_nodes import (
    Node, Number, Variable, BinaryOp, UnaryOp,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan
)


def evaluate_expression(node: Node, var_map: dict) -> float:
    """
    Recursively evaluate an AST node given a dictionary of variable bindings.
    """
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, Variable):
        if node.name in var_map:
            return var_map[node.name]
        raise ValueError(f"Undefined variable '{node.name}' during evaluation.")
    elif isinstance(node, Negate):
        return -evaluate_expression(node.operand, var_map)
    elif isinstance(node, Add):
        return evaluate_expression(node.left, var_map) + evaluate_expression(node.right, var_map)
    elif isinstance(node, Subtract):
        return evaluate_expression(node.left, var_map) - evaluate_expression(node.right, var_map)
    elif isinstance(node, Multiply):
        return evaluate_expression(node.left, var_map) * evaluate_expression(node.right, var_map)
    elif isinstance(node, Divide):
        denom = evaluate_expression(node.right, var_map)
        if denom == 0:
            raise ZeroDivisionError("Division by zero in evaluation.")
        return evaluate_expression(node.left, var_map) / denom
    elif isinstance(node, Power):
        return evaluate_expression(node.left, var_map) ** evaluate_expression(node.right, var_map)
    elif isinstance(node, Sin):
        return math.sin(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Cos):
        return math.cos(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Tan):
        return math.tan(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Log):
        val = evaluate_expression(node.operand, var_map)
        if val <= 0:
            raise ValueError("Logarithm argument must be positive.")
        return math.log(val)
    elif isinstance(node, Exp):
        return math.exp(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Sqrt):
        val = evaluate_expression(node.operand, var_map)
        if val < 0:
            raise ValueError("Square root argument cannot be negative.")
        return math.sqrt(val)
    elif isinstance(node, Asin):
        return math.asin(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Acos):
        return math.acos(evaluate_expression(node.operand, var_map))
    elif isinstance(node, Atan):
        return math.atan(evaluate_expression(node.operand, var_map))
    else:
        raise TypeError(f"Unknown node type for evaluation: {type(node)}")


def render_tree(node: Node, prefix: str = "", is_tail: bool = True) -> str:
    """
    Render an AST node as an ASCII/Unicode tree structure.
    """
    lines = []
    
    # Format node label representation
    label = ""
    if isinstance(node, Number):
        label = f"Number({node.value})"
    elif isinstance(node, Variable):
        label = f"Variable({node.name})"
    elif isinstance(node, Add):
        label = "+"
    elif isinstance(node, Subtract):
        label = "-"
    elif isinstance(node, Multiply):
        label = "*"
    elif isinstance(node, Divide):
        label = "/"
    elif isinstance(node, Power):
        label = "^"
    elif isinstance(node, Negate):
        label = "Negate (-)"
    elif isinstance(node, Sin):
        label = "sin"
    elif isinstance(node, Cos):
        label = "cos"
    elif isinstance(node, Tan):
        label = "tan"
    elif isinstance(node, Log):
        label = "log"
    elif isinstance(node, Exp):
        label = "exp"
    elif isinstance(node, Sqrt):
        label = "sqrt"
    elif isinstance(node, Asin):
        label = "asin"
    elif isinstance(node, Acos):
        label = "acos"
    elif isinstance(node, Atan):
        label = "atan"
    else:
        label = str(node)

    connector = "└── " if is_tail else "├── "
    lines.append(prefix + connector + label)

    # Collect children
    children = []
    if isinstance(node, BinaryOp):
        children = [node.left, node.right]
    elif isinstance(node, UnaryOp):
        children = [node.operand]

    extension = "    " if is_tail else "│   "
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        lines.append(render_tree(child, prefix + extension, is_last))

    return "\n".join(lines) if prefix == "" else "\n".join([lines[0]] + lines[1:])


def render_derivation_steps(node: Node, var: str = "x") -> list:
    """
    Generate step-by-step derivation breakdown showing rule applications
    (Product rule, Chain rule, Quotient rule, Sum/Difference, Power rule, etc.).
    Returns a list of tuples: (step_number, description, tree_or_expression_str)
    """
    steps = []
    
    def explain_node_diff(n: Node, step_idx: int) -> int:
        if isinstance(n, Number):
            desc = f"Constant Rule: d/d{var}({n}) = 0"
            deriv = differentiate(n, var)
            steps.append((step_idx, desc, render_tree(deriv)))
            return step_idx + 1
        elif isinstance(n, Variable):
            if n.name == var:
                desc = f"Power/Linear Rule: d/d{var}({var}) = 1"
            else:
                desc = f"Constant Variable Rule: d/d{var}({n.name}) = 0 (treating as constant)"
            deriv = differentiate(n, var)
            steps.append((step_idx, desc, render_tree(deriv)))
            return step_idx + 1
        elif isinstance(n, Add):
            desc = f"Sum Rule: d/d{var}({n.left} + {n.right}) = d/d{var}({n.left}) + d/d{var}({n.right})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.left, step_idx + 1)
            step_idx = explain_node_diff(n.right, step_idx)
            return step_idx
        elif isinstance(n, Subtract):
            desc = f"Difference Rule: d/d{var}({n.left} - {n.right}) = d/d{var}({n.left}) - d/d{var}({n.right})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.left, step_idx + 1)
            step_idx = explain_node_diff(n.right, step_idx)
            return step_idx
        elif isinstance(n, Multiply):
            desc = f"Product Rule: d/d{var}(f * g) = f' * g + f * g' for ({n.left}) * ({n.right})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.left, step_idx + 1)
            step_idx = explain_node_diff(n.right, step_idx)
            return step_idx
        elif isinstance(n, Divide):
            desc = f"Quotient Rule: d/d{var}(f / g) = (f' * g - f * g') / g^2 for ({n.left}) / ({n.right})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.left, step_idx + 1)
            step_idx = explain_node_diff(n.right, step_idx)
            return step_idx
        elif isinstance(n, Power):
            desc = f"Power / General Exponential Rule for ({n.left}) ^ ({n.right})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.left, step_idx + 1)
            return step_idx
        elif isinstance(n, Sin):
            desc = f"Chain Rule (Sin): d/d{var}(sin({n.operand})) = cos({n.operand}) * d/d{var}({n.operand})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.operand, step_idx + 1)
            return step_idx
        elif isinstance(n, Cos):
            desc = f"Chain Rule (Cos): d/d{var}(cos({n.operand})) = -sin({n.operand}) * d/d{var}({n.operand})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.operand, step_idx + 1)
            return step_idx
        elif isinstance(n, Exp):
            desc = f"Chain Rule (Exp): d/d{var}(exp({n.operand})) = exp({n.operand}) * d/d{var}({n.operand})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.operand, step_idx + 1)
            return step_idx
        elif isinstance(n, Log):
            desc = f"Chain Rule (Log): d/d{var}(log({n.operand})) = (1 / {n.operand}) * d/d{var}({n.operand})"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            step_idx = explain_node_diff(n.operand, step_idx + 1)
            return step_idx
        else:
            desc = f"Differentiation rule for {type(n).__name__}"
            steps.append((step_idx, desc, render_tree(differentiate(n, var))))
            return step_idx + 1

    explain_node_diff(node, 1)
    return steps


def run_tui():
    """
    Run an interactive terminal user interface loop with colorful headers,
    menu options, expression tree rendering, step-by-step differentiation, and evaluation.
    """
    print("=" * 70)
    print("  MINOVATIVE MIND CLI - FLASH LITE CALCULUS ENGINE & TUI")
    print("=" * 70)
    print("Welcome to the interactive symbolic calculus terminal user interface!")
    print("Type 'help' for available commands or enter an expression directly.\n")

    current_expression = "x^3 + sin(x)"
    var_map = {"x": 2.0, "y": 1.0}

    while True:
        try:
            prompt = f"\n[Calculus TUI] (expr: {current_expression}) > "
            user_input = input(prompt).strip()
            
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("exit", "quit", "q"):
                print("Exiting TUI. Have a wonderful day!")
                break

            elif cmd == "help":
                print("\n--- Interactive TUI Commands ---")
                print("  expr <math>       : Set current active expression (e.g. expr x^2 * cos(x))")
                print("  tree              : Render AST tree of current expression")
                print("  diff [var]        : Differentiate current expression with respect to var (default x)")
                print("  steps [var]       : Show step-by-step derivation breakdown")
                print("  simplify          : Simplify current expression")
                print("  eval [var=val...] : Evaluate expression with variable bindings (e.g. eval x=3)")
                print("  help              : Show this help message")
                print("  quit / exit       : Exit TUI")
                print("\nOr simply type any expression (e.g. 'sin(x) + x^2') to analyze it.")

            elif cmd == "expr":
                if not arg:
                    print(f"Current expression: {current_expression}")
                else:
                    try:
                        parse_expression(arg)
                        current_expression = arg
                        print(f"Expression updated to: {current_expression}")
                    except Exception as e:
                        print(f"Invalid expression: {e}")

            elif cmd == "tree":
                expr = parse_expression(current_expression)
                print(f"\nEquation Tree for '{current_expression}':\n")
                print(render_tree(expr))

            elif cmd == "diff":
                var = arg if arg else "x"
                expr = parse_expression(current_expression)
                deriv = differentiate(expr, var)
                simplified = simplify(deriv)
                print(f"\nd/d{var}({current_expression}) = {simplified}")

            elif cmd == "steps":
                var = arg if arg else "x"
                expr = parse_expression(current_expression)
                print(f"\n=== Step-by-Step Derivation Breakdown for d/d{var}({current_expression}) ===")
                steps = render_derivation_steps(expr, var)
                for step_num, desc, tree_str in steps:
                    print(f"\n[Step {step_num}] {desc}")
                    print(tree_str)
                print(f"\nFinal Derivative: {simplify(differentiate(expr, var))}")

            elif cmd == "simplify":
                expr = parse_expression(current_expression)
                simplified = simplify(expr)
                print(f"\nSimplified: {simplified}")

            elif cmd == "eval":
                expr = parse_expression(current_expression)
                if arg:
                    for assignment in arg.split():
                        if "=" in assignment:
                            k, v = assignment.split("=", 1)
                            var_map[k.strip()] = float(v.strip())
                try:
                    val = evaluate_expression(expr, var_map)
                    print(f"\nExpression: {current_expression}")
                    print(f"Variables: {var_map}")
                    print(f"Result: {val}")
                except Exception as e:
                    print(f"Evaluation error: {e}")

            else:
                # Treat as direct expression entry
                try:
                    expr = parse_expression(user_input)
                    current_expression = user_input
                    print(f"\nParsed Expression successfully: {expr}")
                    print(f"Simplified: {simplify(expr)}")
                    print(f"Derivative (dx): {simplify(differentiate(expr, 'x'))}")
                    print("\nEquation Tree:")
                    print(render_tree(expr))
                except Exception as e:
                    print(f"Unknown command or invalid expression: {e}. Type 'help' for options.")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting TUI. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
