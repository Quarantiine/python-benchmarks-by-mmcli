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
        if isinstance(self.value, complex):
            return str(self.value)
        if isinstance(self.value, (int, float)):
            try:
                if self.value.is_integer():
                    return str(int(self.value))
            except (AttributeError, ValueError, OverflowError):
                pass
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

        if isinstance(right, ConstNode) and right.value == 0:
            if isinstance(left, ConstNode) and left.value == 0:
                return ConstNode(float('nan'))
            return DivNode(left, right)
        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
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
        num = self.left.evaluate(env)
        if den == 0:
            if num == 0:
                return float('nan')
            return float('inf') if num > 0 else float('-inf')
        return num / den

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
        # d/dx (u^v)
        v_prime = self.right.differentiate(var).simplify()
        if isinstance(v_prime, ConstNode) and v_prime.value == 0:
            # Power rule: n * u^(n-1) * u'
            return MulNode(
                MulNode(self.right, PowNode(self.left, SubNode(self.right, ConstNode(1)))),
                self.left.differentiate(var)
            )
        else:
            # General rule: u^v * (v' * ln(u) + v * u' / u)
            return MulNode(
                PowNode(self.left, self.right),
                AddNode(
                    MulNode(v_prime, LnNode(self.left)),
                    MulNode(self.right, DivNode(self.left.differentiate(var), self.left))
                )
            )

    def simplify(self) -> Node:
        left = self.left.simplify()
        right = self.right.simplify()

        if isinstance(left, ConstNode) and isinstance(right, ConstNode):
            try:
                val = left.value ** right.value
                if isinstance(val, complex) and val.imag == 0:
                    val = val.real
                return ConstNode(val)
            except ZeroDivisionError:
                pass
        if isinstance(right, ConstNode):
            if right.value == 0:
                return ConstNode(1)
            if right.value == 1:
                return left
        if isinstance(left, ConstNode):
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


class TanNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: sec^2(u) * u' -> (tan^2(u) + 1) * u'
        return MulNode(
            AddNode(PowNode(TanNode(self.inner), ConstNode(2)), ConstNode(1)),
            self.inner.differentiate(var)
        )

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.tan(inner.value))
        return TanNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.tan(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]tan[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"tan({self.inner})"


class AsinNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: u' / sqrt(1 - u^2)
        return DivNode(
            self.inner.differentiate(var),
            SqrtNode(SubNode(ConstNode(1), PowNode(self.inner, ConstNode(2))))
        )

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.asin(inner.value))
        return AsinNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.asin(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]asin[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"asin({self.inner})"


class AcosNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: -u' / sqrt(1 - u^2)
        return DivNode(
            MulNode(ConstNode(-1), self.inner.differentiate(var)),
            SqrtNode(SubNode(ConstNode(1), PowNode(self.inner, ConstNode(2))))
        )

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.acos(inner.value))
        return AcosNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.acos(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]acos[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"acos({self.inner})"


class ExpNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: exp(u) * u'
        return MulNode(ExpNode(self.inner), self.inner.differentiate(var))

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.exp(inner.value))
        return ExpNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.exp(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]exp[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"exp({self.inner})"


class LnNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: u' / u
        return DivNode(self.inner.differentiate(var), self.inner)

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.log(inner.value))
        return LnNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.log(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]ln[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"ln({self.inner})"


class SqrtNode(Node):
    def __init__(self, inner: Node):
        self.inner = inner

    def differentiate(self, var: str) -> Node:
        # Chain rule: u' / (2 * sqrt(u))
        return DivNode(
            self.inner.differentiate(var),
            MulNode(ConstNode(2), SqrtNode(self.inner))
        )

    def simplify(self) -> Node:
        inner = self.inner.simplify()
        if isinstance(inner, ConstNode):
            return ConstNode(math.sqrt(inner.value))
        return SqrtNode(inner)

    def evaluate(self, env: dict) -> float:
        return math.sqrt(self.inner.evaluate(env))

    def to_tree(self) -> Tree:
        tree = Tree("[magenta]sqrt[/magenta]")
        tree.add(self.inner.to_tree())
        return tree

    def __str__(self) -> str:
        return f"sqrt({self.inner})"
