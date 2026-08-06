import math
from math_ast import Node, ConstNode, VarNode, AddNode, SubNode, MulNode, DivNode, PowNode

class IntegrationError(Exception):
    pass

def integrate(expr: Node, var: str) -> Node:
    if isinstance(expr, ConstNode):
        if expr.value == 0:
            return ConstNode(0)
        return MulNode(expr, VarNode(var))
    
    if isinstance(expr, VarNode):
        if expr.name == var:
            return MulNode(ConstNode(0.5), PowNode(VarNode(var), ConstNode(2)))
        else:
            return MulNode(expr, VarNode(var))
            
    if isinstance(expr, AddNode):
        return AddNode(integrate(expr.left, var), integrate(expr.right, var))
        
    if isinstance(expr, SubNode):
        return SubNode(integrate(expr.left, var), integrate(expr.right, var))
        
    if isinstance(expr, MulNode):
        # Only support constant multiples for now
        if isinstance(expr.left, ConstNode):
            return MulNode(expr.left, integrate(expr.right, var))
        if isinstance(expr.right, ConstNode):
            return MulNode(expr.right, integrate(expr.left, var))
        raise IntegrationError("Cannot integrate product of variables")
        
    if isinstance(expr, PowNode):
        if isinstance(expr.left, VarNode) and expr.left.name == var and isinstance(expr.right, ConstNode):
            n = expr.right.value
            if n == -1:
                from math_ast import LnNode
                return LnNode(VarNode(var))
            return MulNode(ConstNode(1 / (n + 1)), PowNode(VarNode(var), ConstNode(n + 1)))
        raise IntegrationError("Cannot integrate this power expression")
        
    raise IntegrationError(f"Integration not implemented for {type(expr)}")


def limit(expr: Node, var: str, point: float) -> float:
    for _ in range(10):
        val = expr.evaluate({var: point})
        if not math.isnan(val) and not math.isinf(val):
            return val
            
        if isinstance(expr, DivNode):
            num = expr.left.evaluate({var: point})
            den = expr.right.evaluate({var: point})
            if (num == 0 and den == 0) or (math.isinf(num) and math.isinf(den)):
                # L'Hopital's rule
                expr = DivNode(expr.left.differentiate(var).simplify(), expr.right.differentiate(var).simplify())
                continue
        break
    return float('nan')
