"""ASCII/Unicode box-drawing AST tree visualizer."""

from core.ast import (
    AddNode,
    Constant,
    CosNode,
    DivNode,
    ExpNode,
    LnNode,
    MulNode,
    NegNode,
    Node,
    PowNode,
    SinNode,
    SqrtNode,
    SubNode,
    TanNode,
    Variable,
)


def render_ast_tree(node: Node, prefix: str = "", is_last: bool = True) -> str:
    """Render an AST node and its sub-children as a box-drawing tree string."""
    lines = []

    # Get label for current node
    node_name = node.__class__.__name__
    if isinstance(node, Constant):
        label = f"Constant ({node.value})"
    elif isinstance(node, Variable):
        label = f"Variable ({node.name})"
    elif isinstance(node, AddNode):
        label = "AddNode (+)"
    elif isinstance(node, SubNode):
        label = "SubNode (-)"
    elif isinstance(node, MulNode):
        label = "MulNode (*)"
    elif isinstance(node, DivNode):
        label = "DivNode (/)"
    elif isinstance(node, PowNode):
        label = "PowNode (^)"
    elif isinstance(node, NegNode):
        label = "NegNode (-)"
    elif isinstance(node, SinNode):
        label = "SinNode (sin)"
    elif isinstance(node, CosNode):
        label = "CosNode (cos)"
    elif isinstance(node, TanNode):
        label = "TanNode (tan)"
    elif isinstance(node, ExpNode):
        label = "ExpNode (exp)"
    elif isinstance(node, LnNode):
        label = "LnNode (ln)"
    elif isinstance(node, SqrtNode):
        label = "SqrtNode (sqrt)"
    else:
        label = f"{node_name} ({str(node)})"

    # Branch symbol
    connector = "└── " if is_last else "├── "
    if not prefix:  # Root node
        lines.append(label)
        child_prefix = ""
    else:
        lines.append(prefix + connector + label)
        child_prefix = prefix + ("    " if is_last else "│   ")

    # Get children
    children = []
    if isinstance(node, (AddNode, SubNode, MulNode, DivNode, PowNode)):
        children = [node.left, node.right]
    elif isinstance(
        node,
        (
            NegNode,
            SinNode,
            CosNode,
            TanNode,
            ExpNode,
            LnNode,
            SqrtNode,
        ),
    ):
        children = [node.child]

    for i, child in enumerate(children):
        is_child_last = i == len(children) - 1
        lines.append(render_ast_tree(child, child_prefix, is_child_last))

    return "\n".join(lines)
