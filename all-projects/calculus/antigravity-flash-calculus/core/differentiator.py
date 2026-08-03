"""Symbolic differentiator with step-by-step rule derivation recording."""

from typing import List, Tuple

from .ast import (
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
from .simplifier import simplify


class DerivationStep:
    """Represents a single step in a step-by-step calculus derivation breakdown."""

    def __init__(
        self,
        rule_name: str,
        expression: str,
        explanation: str,
        result: str,
        simplified_result: str,
    ):
        self.rule_name = rule_name
        self.expression = expression
        self.explanation = explanation
        self.result = result
        self.simplified_result = simplified_result

    def __repr__(self):
        return f"[{self.rule_name}] d/dx({self.expression}) = {self.simplified_result}"


def differentiate_with_steps(
    node: Node, var: str = "x"
) -> Tuple[Node, Node, List[DerivationStep]]:
    """Differentiate an AST node and record step-by-step derivations.

    Returns:
        (raw_derivative_ast, simplified_derivative_ast, steps_list)
    """
    steps: List[DerivationStep] = []

    def _diff(n: Node) -> Node:
        expr_str = str(n)

        if isinstance(n, Constant):
            res = Constant(0)
            simp = res
            steps.append(
                DerivationStep(
                    rule_name="Constant Rule",
                    expression=expr_str,
                    explanation=f"Derivative of constant {n.value} is 0",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, Variable):
            if n.name == var:
                res = Constant(1)
                simp = res
                steps.append(
                    DerivationStep(
                        rule_name="Variable Rule",
                        expression=expr_str,
                        explanation=f"Derivative of variable '{var}' with respect to '{var}' is 1",
                        result=str(res),
                        simplified_result=str(simp),
                    )
                )
                return res
            else:
                res = Constant(0)
                simp = res
                steps.append(
                    DerivationStep(
                        rule_name="Independent Variable Rule",
                        expression=expr_str,
                        explanation=f"Derivative of independent variable '{n.name}' with respect to '{var}' is 0",
                        result=str(res),
                        simplified_result=str(simp),
                    )
                )
                return res

        if isinstance(n, AddNode):
            left_d = _diff(n.left)
            right_d = _diff(n.right)
            res = AddNode(left_d, right_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Sum Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(f + g) = f' + g'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, SubNode):
            left_d = _diff(n.left)
            right_d = _diff(n.right)
            res = SubNode(left_d, right_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Difference Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(f - g) = f' - g'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, MulNode):
            left_d = _diff(n.left)
            right_d = _diff(n.right)
            res = AddNode(MulNode(left_d, n.right), MulNode(n.left, right_d))
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Product Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(u * v) = u' * v + u * v'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, DivNode):
            left_d = _diff(n.left)
            right_d = _diff(n.right)
            num = SubNode(MulNode(left_d, n.right), MulNode(n.left, right_d))
            den = PowNode(n.right, Constant(2))
            res = DivNode(num, den)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Quotient Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(u / v) = (u' * v - u * v') / (v^2)",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, PowNode):
            if isinstance(n.right, Constant):
                c = n.right.value
                u_d = _diff(n.left)
                res = MulNode(
                    MulNode(Constant(c), PowNode(n.left, Constant(c - 1))), u_d
                )
                simp = simplify(res)
                steps.append(
                    DerivationStep(
                        rule_name="Power & Chain Rule",
                        expression=expr_str,
                        explanation=f"d/d{var}(u^{c}) = {c} * u^{{{c-1}}} * u'",
                        result=str(res),
                        simplified_result=str(simp),
                    )
                )
                return res
            else:
                # General power rule using exp(v * ln(u))
                u_d = _diff(n.left)
                v_d = _diff(n.right)
                term1 = MulNode(v_d, LnNode(n.left))
                term2 = MulNode(n.right, DivNode(u_d, n.left))
                res = MulNode(PowNode(n.left, n.right), AddNode(term1, term2))
                simp = simplify(res)
                steps.append(
                    DerivationStep(
                        rule_name="Generalized Power Rule",
                        expression=expr_str,
                        explanation=f"d/d{var}(u^v) = u^v * (v' * ln(u) + v * u' / u)",
                        result=str(res),
                        simplified_result=str(simp),
                    )
                )
                return res

        if isinstance(n, NegNode):
            child_d = _diff(n.child)
            res = NegNode(child_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Negation Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(-u) = -u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, SinNode):
            u_d = _diff(n.child)
            res = MulNode(CosNode(n.child), u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Trig Rule (Sin)",
                    expression=expr_str,
                    explanation=f"d/d{var}(sin(u)) = cos(u) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, CosNode):
            u_d = _diff(n.child)
            res = MulNode(NegNode(SinNode(n.child)), u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Trig Rule (Cos)",
                    expression=expr_str,
                    explanation=f"d/d{var}(cos(u)) = -sin(u) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, TanNode):
            u_d = _diff(n.child)
            sec_sq = DivNode(Constant(1), PowNode(CosNode(n.child), Constant(2)))
            res = MulNode(sec_sq, u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Trig Rule (Tan)",
                    expression=expr_str,
                    explanation=f"d/d{var}(tan(u)) = (1 / cos(u)^2) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, ExpNode):
            u_d = _diff(n.child)
            res = MulNode(ExpNode(n.child), u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Exponential Rule (Exp)",
                    expression=expr_str,
                    explanation=f"d/d{var}(exp(u)) = exp(u) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, LnNode):
            u_d = _diff(n.child)
            res = MulNode(DivNode(Constant(1), n.child), u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Logarithm Rule (Ln)",
                    expression=expr_str,
                    explanation=f"d/d{var}(ln(u)) = (1 / u) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        if isinstance(n, SqrtNode):
            u_d = _diff(n.child)
            denom = MulNode(Constant(2), SqrtNode(n.child))
            res = MulNode(DivNode(Constant(1), denom), u_d)
            simp = simplify(res)
            steps.append(
                DerivationStep(
                    rule_name="Square Root Rule",
                    expression=expr_str,
                    explanation=f"d/d{var}(sqrt(u)) = (1 / (2 * sqrt(u))) * u'",
                    result=str(res),
                    simplified_result=str(simp),
                )
            )
            return res

        # Fallback to direct node differentiate method
        raw_res = n.differentiate(var)
        simp_res = simplify(raw_res)
        return raw_res

    raw_derivative = _diff(node)
    final_simplified = simplify(raw_derivative)

    return raw_derivative, final_simplified, steps
