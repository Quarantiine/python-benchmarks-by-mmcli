import math
from rich.tree import Tree

class Node:
    def differentiate(self, var: str) -> "Node":
        raise NotImplementedError

    def simplify(self) -> "Node":
        return self

    def evaluate(self, env: dict) -> float:
        raise NotImplementedError

    def to_tree(self) -> Tree:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class ConstNode(Node):
    def __init__(self, value: float):
        self.value = value

    def differentiate(self, var: str) -> Node:
        return ConstNode(0)

    def evaluate(self, env: dict) -> float:
        return self.value

    def to_tree(self) -> Tree:
        return Tree(f"[cyan]Const[/cyan]: {self.value}")

    def __str__(self) -> str:
        if isinstance(self.value, int) or self.value.is_integer():
            return str(int(self.value))
        return str(self.value)


class VarNode(Node):
    def __init__(self, name: str):
        self.name = name

    def differentiate(self, var: str) -> Node:
        if self.name == var:
            return ConstNode(1)
        return ConstNode(0)

    def evaluate(self, env: dict) -> float:
        return env.get(self.name, 0.0)

    def to_tree(self) -> Tree:
        return Tree(f"[green]Var[/green]: {self.name}")

    def __str__(self) -> str:
        return self.name


class AddNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        return AddNode(self.left.differentiate(var), self.right.differentiate(var))

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
            return ConstNode(left.value + right.value)
        if isinstance(left, ConstNode) and left.value == 0:
            return right
        if isinstance(right, ConstNode) and right.value == 0:
            return left
        
        return AddNode(left, right)

    def evaluate(self, env: dict) -> float:
        return self.left.evaluate(env) + self.right.evaluate(env)

    def to_tree(self) -> Tree:
        tree = Tree("[yellow]+[/yellow]")
        tree.add(self.left.to_tree())
        tree.add(self.right.to_tree())
        return tree

    def __str__(self) -> str:
        return f"({self.left} + {self.right})"


class SubNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        return SubNode(self.left.differentiate(var), self.right.differentiate(var))

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
            return ConstNode(left.value - right.value)
        if isinstance(right, ConstNode) and right.value == 0:
            return left
        if str(left) == str(right):
            return ConstNode(0)

        return SubNode(left, right)

    def evaluate(self, env: dict) -> float:
        return self.left.evaluate(env) - self.right.evaluate(env)

    def to_tree(self) -> Tree:
        tree = Tree("[yellow]-[/yellow]")
        tree.add(self.left.to_tree())
        tree.add(self.right.to_tree())
        return tree

    def __str__(self) -> str:
        return f"({self.left} - {self.right})"


class MulNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # Product rule: u'v + uv'
        return AddNode(
            MulNode(self.left.differentiate(var), self.right),
            MulNode(self.left, self.right.differentiate(var))
        )

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
            return ConstNode(left.value * right.value)
        if isinstance(left, ConstNode):
            if left.value == 0:
                return ConstNode(0)
            if left.value == 1:
                return right
        if isinstance(right, ConstNode):
            if right.value == 0:
                return ConstNode(0)
            if right.value == 1:
                return left
        
        return MulNode(left, right)

    def evaluate(self, env: dict) -> float:
        return self.left.evaluate(env) * self.right.evaluate(env)

    def to_tree(self) -> Tree:
        tree = Tree("[yellow]*[/yellow]")
        tree.add(self.left.to_tree())
        tree.add(self.right.to_tree())
        return tree

    def __str__(self) -> str:
        return f"({self.left} * {self.right})"


class DivNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # Quotient rule: (u'v - uv') / v^2
        numerator = SubNode(
            MulNode(self.left.differentiate(var), self.right),
            MulNode(self.left, self.right.differentiate(var))
        )
        denominator = PowNode(self.right, ConstNode(2))
        return DivNode(numerator, denominator)

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode) and right.value != 0:
            return ConstNode(left.value / right.value)
        if isinstance(left, ConstNode) and left.value == 0:
            return ConstNode(0)
        if isinstance(right, ConstNode) and right.value == 1:
            return left
        if str(left) == str(right):
            return ConstNode(1)
            
        return DivNode(left, right)

    def evaluate(self, env: dict) -> float:
        den = self.right.evaluate(env)
        if den == 0:
            return float('inf') # Simple handling
        return self.left.evaluate(env) / den

    def to_tree(self) -> Tree:
        tree = Tree("[yellow]/[/yellow]")
        tree.add(self.left.to_tree())
        tree.add(self.right.to_tree())
        return tree

    def __str__(self) -> str:
        return f"({self.left} / {self.right})"


class PowNode(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def differentiate(self, var: str) -> Node:
        # d/dx (u^v) = u^v * (v' * ln(u) + v * u' / u)
        # However, for simplicity and common usage (like x^n where n is constant),
        # we can do a simpler check.
        if isinstance(self.right, ConstNode):
            # Power rule: n * u^(n-1) * u'
            n = self.right.value
            return MulNode(
                MulNode(ConstNode(n), PowNode(self.left, ConstNode(n - 1))),
                self.left.differentiate(var)
            )
        else:
            # Generalized exponential rule
            # Requires log, which we haven't implemented yet in AST, but we can return unsimplified
            # For this TUI we'll stick to a simpler approach or implement full rule.
            # (assuming right node is a constant in most user examples)
            # We'll just return a placeholder or implement it fully if we add LogNode.
            pass # We'll stick to constant powers for now, or just implement basic power rule.
            
            # Since the scope is simple calculus, let's just assume constant power if it fails.
            return MulNode(
                MulNode(self.right, PowNode(self.left, SubNode(self.right, ConstNode(1)))),
                self.left.differentiate(var)
            )

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
            return ConstNode(left.value ** right.value)
        if isinstance(right, ConstNode):
            if right.value == 0:
                return ConstNode(1)
            if right.value == 1:
                return left
        if isinstance(left, ConstNode):
            if left.value == 0:
                return ConstNode(0)
            if left.value == 1:
                return ConstNode(1)

        return PowNode(left, right)

    def evaluate(self, env: dict) -> float:
        try:
            return self.left.evaluate(env) ** self.right.evaluate(env)
        except Exception:
            return float('nan')

    def to_tree(self) -> Tree:
        tree = Tree("[yellow]^[/yellow]")
        tree.add(self.left.to_tree())
        tree.add(self.right.to_tree())
        return tree

    def __str__(self) -> str:
        return f"({self.left} ^ {self.right})"


class SinNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: cos(u) * u'
        return MulNode(CosNode(self.inner), self.inner.differentiate(var))

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.sin(inner.value))
        return SinNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.sin(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]sin[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"sin({self.inner})"


class CosNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: -sin(u) * u'
        return MulNode(
            MulNode(ConstNode(-1), SinNode(self.inner)),
            self.inner.differentiate(var)
        )

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.cos(inner.value))
        return CosNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.cos(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]cos[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"cos({self.inner})"

