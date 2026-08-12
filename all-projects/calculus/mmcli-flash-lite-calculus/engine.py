"""
Calculus engine providing recursive algebraic differentiation and algebraic simplification rules.
Supports:
  - Differentiation w.r.t. a variable using Power rule, Product rule, Quotient rule, Chain rule, Sum/Difference rule, and Trig/Exponential/Logarithmic rules.
  - Algebraic simplification rules (constant folding, zero/identity eliminations, power folding, log/exp identities, double negation cancellation).
"""

import math
from typing import Dict, Union, Set, Optional
from ast_nodes import (
    Node, Number, Variable, BinaryOp, UnaryOp,
    Add, Subtract, Multiply, Divide, Power, Negate,
    Sin, Cos, Tan, Log, Exp, Sqrt, Asin, Acos, Atan
)


def _try_simplify_sub_numbers(left: Node, right: Node) -> Node:
    if isinstance(left, Number) and isinstance(right, Number):
        return Number(left.value - right.value)
    return Subtract(left, right)


def integrate(node: Node, var: str = "x") -> Node:
    """Compute symbolic antiderivative of AST node with respect to var."""
    res = _integrate_raw(node, var)
    return simplify(res)


def _integrate_raw(node: Node, var: str) -> Node:
    if isinstance(node, Number):
        return Multiply(node.clone(), Variable(var))

    if isinstance(node, Variable):
        if node.name == var:
            return Divide(Power(Variable(var), Number(2.0)), Number(2.0))
        return Multiply(Variable(node.name), Variable(var))

    if isinstance(node, Add):
        return Add(_integrate_raw(node.left, var), _integrate_raw(node.right, var))

    if isinstance(node, Subtract):
        return Subtract(_integrate_raw(node.left, var), _integrate_raw(node.right, var))

    if isinstance(node, Negate):
        return Negate(_integrate_raw(node.operand, var))

    if isinstance(node, Multiply):
        if isinstance(node.left, Number):
            return Multiply(node.left.clone(), _integrate_raw(node.right, var))
        if isinstance(node.right, Number):
            return Multiply(node.right.clone(), _integrate_raw(node.left, var))
        if var not in node.right.get_variables():
            return Multiply(node.right.clone(), _integrate_raw(node.left, var))
        if var not in node.left.get_variables():
            return Multiply(node.left.clone(), _integrate_raw(node.right, var))

    if isinstance(node, Power):
        base, exponent = node.left, node.right
        if isinstance(base, Variable) and base.name == var and isinstance(exponent, Number):
            n = exponent.value
            if math.isclose(n, -1.0, abs_tol=1e-12):
                return Log(Variable(var))
            new_n = n + 1.0
            if math.isclose(new_n, round(new_n), abs_tol=1e-12):
                new_n = round(new_n)
            return Divide(Power(Variable(var), Number(new_n)), Number(new_n))

    if isinstance(node, Sin):
        if isinstance(node.operand, Variable) and node.operand.name == var:
            return Negate(Cos(Variable(var)))

    if isinstance(node, Cos):
        if isinstance(node.operand, Variable) and node.operand.name == var:
            return Sin(Variable(var))

    if isinstance(node, Exp):
        if isinstance(node.operand, Variable) and node.operand.name == var:
            return Exp(Variable(var))

    if isinstance(node, Log):
        if isinstance(node.operand, Variable) and node.operand.name == var:
            return Subtract(Multiply(Variable(var), Log(Variable(var))), Variable(var))

    raise NotImplementedError(f"Symbolic integration not supported for node: {node}")


def differentiate(node: Node, var: str = 'x') -> Node:
    """
    Recursively compute the symbolic derivative of an AST node with respect to variable `var`.
    Implements:
      - Constant rule: d/dx(c) = 0
      - Variable rule: d/dx(x) = 1, d/dx(y) = 0
      - Sum/Difference rule: d/dx(f ± g) = f' ± g'
      - Product rule: d/dx(f * g) = f' * g + f * g'
      - Quotient rule: d/dx(f / g) = (f' * g - f * g') / (g ^ 2)
      - Power rule:
          - d/dx(x^n) = n * x^(n-1) * x' (where n is constant)
          - General power rule via exp(g * log(f)) for f(x)^g(x)
      - Chain rule for composite functions: d/dx(f(g(x))) = f'(g(x)) * g'(x)
      - Trigonometric & Transcendental rules:
          - d/dx(sin(u)) = cos(u) * u'
          - d/dx(cos(u)) = -sin(u) * u'
          - d/dx(tan(u)) = sec^2(u) * u' = (1 + tan^2(u)) * u' or (1 / cos^2(u)) * u'
          - d/dx(log(u)) = (1 / u) * u'
          - d/dx(exp(u)) = exp(u) * u'
          - d/dx(sqrt(u)) = (1 / (2 * sqrt(u))) * u'
          - d/dx(asin(u)) = (1 / sqrt(1 - u^2)) * u'
          - d/dx(acos(u)) = (-1 / sqrt(1 - u^2)) * u'
          - d/dx(atan(u)) = (1 / (1 + u^2)) * u'
    """
    if isinstance(node, Number):
        return Number(0.0)

    elif isinstance(node, Variable):
        if node.name == var:
            return Number(1.0)
        else:
            return Number(0.0)

    elif isinstance(node, Add):
        return Add(differentiate(node.left, var), differentiate(node.right, var))

    elif isinstance(node, Subtract):
        return Subtract(differentiate(node.left, var), differentiate(node.right, var))

    elif isinstance(node, Multiply):
        # Product rule: (f * g)' = f' * g + f * g'
        f = node.left
        g = node.right
        df = differentiate(f, var)
        dg = differentiate(g, var)
        return Add(Multiply(df, g.clone()), Multiply(f.clone(), dg))

    elif isinstance(node, Divide):
        # Quotient rule: (f / g)' = (f' * g - f * g') / (g ^ 2)
        f = node.left
        g = node.right
        df = differentiate(f, var)
        dg = differentiate(g, var)
        numerator = Subtract(Multiply(df, g.clone()), Multiply(f.clone(), dg))
        denominator = Power(g.clone(), Number(2.0))
        return Divide(numerator, denominator)

    elif isinstance(node, Power):
        base = node.left
        exponent = node.right
        
        base_vars = base.get_variables()
        exp_vars = exponent.get_variables()

        if var not in exp_vars:
            # Power rule: d/dx(f(x)^n) = n * f(x)^(n-1) * f'(x)
            n = exponent
            f = base
            df = differentiate(f, var)
            new_exp = _try_simplify_sub_numbers(n, Number(1.0))
            return Multiply(Multiply(n.clone(), Power(f.clone(), new_exp)), df)
        elif var not in base_vars:
            # Exponential rule: d/dx(a^g(x)) = a^g(x) * ln(a) * g'(x)
            a = base
            g = exponent
            dg = differentiate(g, var)
            return Multiply(Multiply(Power(a.clone(), g.clone()), Log(a.clone())), dg)
        else:
            # General function-to-function power rule: f(x)^g(x) = exp(g(x) * ln(f(x)))
            # d/dx [ f(x)^g(x) ] = f(x)^g(x) * [ g'(x) * ln(f(x)) + g(x) * (f'(x) / f(x)) ]
            f = base
            g = exponent
            df = differentiate(f, var)
            dg = differentiate(g, var)
            term1 = Multiply(dg, Log(f.clone()))
            term2 = Multiply(g.clone(), Divide(df, f.clone()))
            inner_deriv = Add(term1, term2)
            return Multiply(Power(f.clone(), g.clone()), inner_deriv)

    elif isinstance(node, Negate):
        return Negate(differentiate(node.operand, var))

    elif isinstance(node, Sin):
        # d/dx(sin(u)) = cos(u) * u'
        u = node.operand
        du = differentiate(u, var)
        return Multiply(Cos(u.clone()), du)

    elif isinstance(node, Cos):
        # d/dx(cos(u)) = -sin(u) * u'
        u = node.operand
        du = differentiate(u, var)
        return Multiply(Negate(Sin(u.clone())), du)

    elif isinstance(node, Tan):
        # d/dx(tan(u)) = (1 / cos^2(u)) * u' = (1 + tan^2(u)) * u'
        u = node.operand
        du = differentiate(u, var)
        sec_sq = Divide(Number(1.0), Power(Cos(u.clone()), Number(2.0)))
        return Multiply(sec_sq, du)

    elif isinstance(node, Log):
        # d/dx(log(u)) = (1 / u) * u'
        u = node.operand
        du = differentiate(u, var)
        return Multiply(Divide(Number(1.0), u.clone()), du)

    elif isinstance(node, Exp):
        # d/dx(exp(u)) = exp(u) * u'
        u = node.operand
        du = differentiate(u, var)
        return Multiply(Exp(u.clone()), du)

    elif isinstance(node, Sqrt):
        # d/dx(sqrt(u)) = (1 / (2 * sqrt(u))) * u'
        u = node.operand
        du = differentiate(u, var)
        denom = Multiply(Number(2.0), Sqrt(u.clone()))
        return Multiply(Divide(Number(1.0), denom), du)

    elif isinstance(node, Asin):
        # d/dx(asin(u)) = (1 / sqrt(1 - u^2)) * u'
        u = node.operand
        du = differentiate(u, var)
        denom = Sqrt(Subtract(Number(1.0), Power(u.clone(), Number(2.0))))
        return Multiply(Divide(Number(1.0), denom), du)

    elif isinstance(node, Acos):
        # d/dx(acos(u)) = (-1 / sqrt(1 - u^2)) * u'
        u = node.operand
        du = differentiate(u, var)
        numer = Number(-1.0)
        denom = Sqrt(Subtract(Number(1.0), Power(u.clone(), Number(2.0))))
        return Multiply(Divide(numer, denom), du)

    elif isinstance(node, Atan):
        # d/dx(atan(u)) = (1 / (1 + u^2)) * u'
        u = node.operand
        du = differentiate(u, var)
        denom = Add(Number(1.0), Power(u.clone(), Number(2.0)))
        return Multiply(Divide(Number(1.0), denom), du)

    else:
        raise TypeError(f"Differentiate not supported for node type {type(node)}")


def simplify(node: Node) -> Node:
    """
    Recursively simplify an AST node using algebraic simplification rules and constant folding.
    Iterates until fixed point is reached (or up to a max iteration count) to ensure
    nested and cascading simplifications are fully resolved.
    """
    prev_str = ""
    current = node.clone()
    max_iters = 15

    for _ in range(max_iters):
        simplified = _simplify_single_pass(current)
        curr_str = str(simplified)
        if curr_str == prev_str:
            return simplified
        prev_str = curr_str
        current = simplified

    return current


def _is_zero(node: Node) -> bool:
    if isinstance(node, Number):
        return math.isclose(node.value, 0.0, abs_tol=1e-12)
    return False


def _is_one(node: Node) -> bool:
    if isinstance(node, Number):
        return math.isclose(node.value, 1.0, abs_tol=1e-12)
    return False


def _is_minus_one(node: Node) -> bool:
    if isinstance(node, Number):
        return math.isclose(node.value, -1.0, abs_tol=1e-12)
    return False


def _simplify_single_pass(node: Node) -> Node:
    """Perform a single pass of bottom-up algebraic simplification."""
    if isinstance(node, Number) or isinstance(node, Variable):
        return node.clone()

    elif isinstance(node, BinaryOp):
        left_simp = _simplify_single_pass(node.left)
        right_simp = _simplify_single_pass(node.right)

        # 1. Constant folding if both are numbers
        if isinstance(left_simp, Number) and isinstance(right_simp, Number):
            env = {}
            # Evaluate using binary op directly or evaluate method
            try:
                val = BinaryOp(left_simp, right_simp) # dummy
                if isinstance(node, Add):
                    res = left_simp.value + right_simp.value
                elif isinstance(node, Subtract):
                    res = left_simp.value - right_simp.value
                elif isinstance(node, Multiply):
                    res = left_simp.value * right_simp.value
                elif isinstance(node, Divide):
                    if math.isclose(right_simp.value, 0.0, abs_tol=1e-15):
                        return Divide(left_simp, right_simp) # preserve or let raise
                    res = left_simp.value / right_simp.value
                elif isinstance(node, Power):
                    # Guard against complex numbers or domain errors
                    if left_simp.value < 0 and not float(right_simp.value).is_integer():
                        res = left_simp.value ** right_simp.value # may raise or return complex
                    else:
                        res = left_simp.value ** right_simp.value
                else:
                    res = None
                
                if res is not None and isinstance(res, (int, float)) and not math.isnan(res) and not math.isinf(res):
                    return Number(res)
            except Exception:
                pass

        # 2. Specific Binary Op Simplifications
        if isinstance(node, Add):
            # 0 + x => x, x + 0 => x
            if _is_zero(left_simp):
                return right_simp
            if _is_zero(right_simp):
                return left_simp
            # x + (-y) => x - y
            if isinstance(right_simp, Negate):
                return Subtract(left_simp, right_simp.operand)
            if isinstance(left_simp, Negate):
                return Subtract(right_simp, left_simp.operand)
            # x + x => 2 * x (Combining like terms)
            if left_simp == right_simp:
                return Multiply(Number(2.0), left_simp)
            # c1*x + c2*x => (c1+c2)*x
            combined = _try_combine_add_terms(left_simp, right_simp)
            if combined is not None:
                return combined
            return Add(left_simp, right_simp)

        elif isinstance(node, Subtract):
            # x - 0 => x
            if _is_zero(right_simp):
                return left_simp
            # 0 - x => -x
            if _is_zero(left_simp):
                return Negate(right_simp)
            # x - x => 0
            if left_simp == right_simp:
                return Number(0.0)
            # x - (-y) => x + y
            if isinstance(right_simp, Negate):
                return Add(left_simp, right_simp.operand)
            return Subtract(left_simp, right_simp)

        elif isinstance(node, Multiply):
            # 0 * x => 0, x * 0 => 0
            if _is_zero(left_simp) or _is_zero(right_simp):
                return Number(0.0)
            # 1 * x => x, x * 1 => x
            if _is_one(left_simp):
                return right_simp
            if _is_one(right_simp):
                return left_simp
            # -1 * x => -x, x * -1 => -x
            if _is_minus_one(left_simp):
                return Negate(right_simp)
            if _is_minus_one(right_simp):
                return Negate(left_simp)
            # (a * x) * b => (a * b) * x constant coefficient merging
            merged_mult = _try_merge_constants_multiply(left_simp, right_simp)
            if merged_mult is not None:
                return merged_mult
            # x * x => x^2
            if left_simp == right_simp:
                return Power(left_simp, Number(2.0))
            return Multiply(left_simp, right_simp)

        elif isinstance(node, Divide):
            # 0 / x => 0 (x != 0)
            if _is_zero(left_simp) and not _is_zero(right_simp):
                return Number(0.0)
            # x / 1 => x
            if _is_one(right_simp):
                return left_simp
            # x / x => 1 (x != 0)
            if left_simp == right_simp and not _is_zero(left_simp):
                return Number(1.0)
            # -x / -y => x / y or similar
            if isinstance(left_simp, Negate) and isinstance(right_simp, Negate):
                return Divide(left_simp.operand, right_simp.operand)
            return Divide(left_simp, right_simp)

        elif isinstance(node, Power):
            # x ^ 0 => 1
            if _is_zero(right_simp):
                return Number(1.0)
            # x ^ 1 => x
            if _is_one(right_simp):
                return left_simp
            # 0 ^ x => 0 (x > 0)
            if _is_zero(left_simp) and not _is_zero(right_simp):
                return Number(0.0)
            # 1 ^ x => 1
            if _is_one(left_simp):
                return Number(1.0)
            # (x ^ a) ^ b => x ^ (a * b)
            if isinstance(left_simp, Power):
                new_exp = _simplify_single_pass(Multiply(left_simp.right, right_simp))
                return Power(left_simp.left, new_exp)
            # Constant folding for Subtractions/Additions inside exponents like x ^ (3 - 1) => x ^ 2
            if isinstance(right_simp, Number):
                pass
            return Power(left_simp, right_simp)

    elif isinstance(node, UnaryOp):
        op_simp = _simplify_single_pass(node.operand)

        if isinstance(node, Negate):
            # -(-x) => x
            if isinstance(op_simp, Negate):
                return op_simp.operand
            # -0 => 0
            if _is_zero(op_simp):
                return Number(0.0)
            # Constant evaluation for Negate
            if isinstance(op_simp, Number):
                return Number(-op_simp.value)
            return Negate(op_simp)

        elif isinstance(node, Sin):
            if isinstance(op_simp, Number):
                val = op_simp.value
                # sin(0) = 0
                if math.isclose(val % (2 * math.pi), 0.0, abs_tol=1e-10) or math.isclose(val % (2 * math.pi), 2 * math.pi, abs_tol=1e-10):
                    return Number(0.0)
                # sin(pi/2) = 1
                if math.isclose((val - math.pi / 2) % (2 * math.pi), 0.0, abs_tol=1e-10):
                    return Number(1.0)
            return Sin(op_simp)

        elif isinstance(node, Cos):
            if isinstance(op_simp, Number):
                val = op_simp.value
                # cos(0) = 1
                if math.isclose(val % (2 * math.pi), 0.0, abs_tol=1e-10) or math.isclose(val % (2 * math.pi), 2 * math.pi, abs_tol=1e-10):
                    return Number(1.0)
                # cos(pi/2) = 0
                if math.isclose((val - math.pi / 2) % (2 * math.pi), 0.0, abs_tol=1e-10):
                    return Number(0.0)
            return Cos(op_simp)

        elif isinstance(node, Log):
            # ln(1) = 0
            if _is_one(op_simp):
                return Number(0.0)
            # ln(e) = 1
            if isinstance(op_simp, Number) and math.isclose(op_simp.value, math.e, abs_tol=1e-10):
                return Number(1.0)
            # ln(exp(x)) => x
            if isinstance(op_simp, Exp):
                return op_simp.operand
            return Log(op_simp)

        elif isinstance(node, Exp):
            # exp(0) = 1
            if _is_zero(op_simp):
                return Number(1.0)
            # exp(ln(x)) => x
            if isinstance(op_simp, Log):
                return op_simp.operand
            return Exp(op_simp)

        elif isinstance(node, Sqrt):
            # sqrt(0) = 0, sqrt(1) = 1
            if _is_zero(op_simp):
                return Number(0.0)
            if _is_one(op_simp):
                return Number(1.0)
            if isinstance(op_simp, Number) and op_simp.value >= 0:
                root = math.sqrt(op_simp.value)
                if math.isclose(root, round(root), abs_tol=1e-10):
                    return Number(round(root))
            # sqrt(x^2) => x (assuming x >= 0 or general absolute value, here x)
            if isinstance(op_simp, Power) and isinstance(op_simp.right, Number) and math.isclose(op_simp.right.value, 2.0, abs_tol=1e-9):
                return op_simp.left
            return Sqrt(op_simp)

        elif isinstance(node, Asin):
            if isinstance(op_simp, Number):
                if math.isclose(op_simp.value, 0.0, abs_tol=1e-10):
                    return Number(0.0)
                if math.isclose(op_simp.value, 1.0, abs_tol=1e-10):
                    return Number(math.pi / 2)
                if math.isclose(op_simp.value, -1.0, abs_tol=1e-10):
                    return Number(-math.pi / 2)
            return Asin(op_simp)

        elif isinstance(node, Acos):
            if isinstance(op_simp, Number):
                if math.isclose(op_simp.value, 1.0, abs_tol=1e-10):
                    return Number(0.0)
                if math.isclose(op_simp.value, 0.0, abs_tol=1e-10):
                    return Number(math.pi / 2)
                if math.isclose(op_simp.value, -1.0, abs_tol=1e-10):
                    return Number(math.pi)
            return Acos(op_simp)

        elif isinstance(node, Atan):
            if isinstance(op_simp, Number):
                if math.isclose(op_simp.value, 0.0, abs_tol=1e-10):
                    return Number(0.0)
                if math.isclose(op_simp.value, 1.0, abs_tol=1e-10):
                    return Number(math.pi / 4)
            return Atan(op_simp)

        else:
            return node.__class__(op_simp)

    return node.clone()


def _try_combine_add_terms(left: Node, right: Node) -> Optional[Node]:
    """Try combining like terms in addition, e.g., c1*x + c2*x => (c1+c2)*x or x + c*x => (1+c)*x."""
    # Extract coefficient and variable term for left and right
    c1, t1 = _extract_coef_term(left)
    c2, t2 = _extract_coef_term(right)

    if t1 == t2:
        new_coef = c1 + c2
        if math.isclose(new_coef, 0.0, abs_tol=1e-12):
            return Number(0.0)
        if math.isclose(new_coef, 1.0, abs_tol=1e-12):
            return t1
        return Multiply(Number(new_coef), t1)

    return None


def _extract_coef_term(node: Node) -> tuple[float, Node]:
    """Helper to extract (coefficient, base_term) from a product like c * term or term."""
    if isinstance(node, Multiply):
        if isinstance(node.left, Number):
            return node.left.value, node.right
        if isinstance(node.right, Number):
            return node.right.value, node.left
    if isinstance(node, Number):
        return node.value, Number(1.0)
    return 1.0, node


def _try_merge_constants_multiply(left: Node, right: Node) -> Optional[Node]:
    """Merge constants in multiplications like (a * x) * b => (a * b) * x."""
    if isinstance(left, Multiply) and isinstance(left.left, Number) and isinstance(right, Number):
        new_c = left.left.value * right.value
        return Multiply(Number(new_c), left.right)
    if isinstance(right, Multiply) and isinstance(right.left, Number) and isinstance(left, Number):
        new_c = right.left.value * left.value
        return Multiply(Number(new_c), right.right)
    return None