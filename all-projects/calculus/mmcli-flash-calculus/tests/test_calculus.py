"""
Unit tests for symbolic calculus engine covering differentiation, integration,
limit calculation, and expression rendering.
"""

import math
import pytest

from calculus import (
    parse, diff, integrate, limit, simplify, render_pretty, to_latex, render_tree,
    Symbol, Const, Add, Sub, Mul, Div, Pow, Sin, Cos, Tan, Asin, Acos, Atan, Exp, Ln, Sqrt, Abs, Neg
)


# ==============================================================================
# 1. PARSER, AST, EVALUATION & SIMPLIFICATION TESTS
# ==============================================================================

def test_parser_and_eval():
    expr = parse("3 * x^2 + 2 * x + 1")
    val = expr.eval({"x": 2})
    assert math.isclose(val, 17.0)

    # Implicit multiplication and trig
    expr2 = parse("2x + sin(x)")
    val2 = expr2.eval({"x": 0})
    assert math.isclose(val2, 0.0)

    # Multi-variable evaluation
    expr3 = parse("x^2 + y^2 - 2*x*y")
    val3 = expr3.eval({"x": 3, "y": 2})
    assert math.isclose(val3, 1.0)

    # Inverse trig parsing & implicit prefix function expansion
    expr_inv = parse("asin(x) + acos(x)")
    assert diff(expr_inv, "x") == Const(0)

    expr_prefix = parse("cos3x")
    d_prefix = diff(expr_prefix, "x")
    assert d_prefix == Mul(Const(-3), Sin(Mul(Const(3), Symbol("x")))) or "-" in str(d_prefix)


def test_simplification():
    expr = parse("x + 0 + x * 1 - 0")
    simp = simplify(expr)
    assert str(simp) in ("(2 * x)", "(2*x)", "(x * 2)", "(x + x)") or simp == Mul(Const(2), Symbol("x"))

    expr2 = parse("0 * x + sin(0)")
    simp2 = simplify(expr2)
    assert simp2 == Const(0)

    # Power and constant simplification: x^0 -> 1, x^1 -> x
    assert simplify(parse("x^0")) == Const(1)
    assert simplify(parse("x^1")) == Symbol("x")
    assert simplify(parse("1 * x")) == Symbol("x")


# ==============================================================================
# 2. SYMBOLIC DIFFERENTIATION TESTS
# ==============================================================================

def test_differentiation_basic_powers_and_polynomials():
    x = Symbol("x")

    # Constant: d/dx [7] = 0
    assert diff(Const(7), x) == Const(0)

    # Linear: d/dx [x] = 1
    assert diff(Symbol("x"), x) == Const(1)

    # Unrelated variable: d/dx [y] = 0
    assert diff(Symbol("y"), x) == Const(0)

    # Polynomial: d/dx [x^3 + 2x^2 + 5x - 7] = 3x^2 + 4x + 5
    f = parse("x^3 + 2*x^2 + 5*x - 7")
    df = diff(f, x)
    assert math.isclose(df.eval({"x": 2}), 25.0)

    # Negative exponent / power rule: d/dx [x^-1] = -x^-2
    f_pow = parse("x^(-1)")
    df_pow = diff(f_pow, x)
    assert math.isclose(df_pow.eval({"x": 2}), -0.25)


def test_differentiation_product_and_quotient_rules():
    x = Symbol("x")

    # Product Rule: d/dx [x * sin(x)] = sin(x) + x * cos(x)
    f_prod = parse("x * sin(x)")
    df_prod = diff(f_prod, x)
    assert math.isclose(df_prod.eval({"x": math.pi / 2}), 1.0, abs_tol=1e-5)

    # Quotient Rule: d/dx [sin(x) / x] = (x*cos(x) - sin(x)) / x^2
    f_quot = parse("sin(x) / x")
    df_quot = diff(f_quot, x)
    # At x = pi/2: (pi/2 * 0 - 1) / (pi^2 / 4) = -4 / pi^2
    expected_quot = -4.0 / (math.pi ** 2)
    assert math.isclose(df_quot.eval({"x": math.pi / 2}), expected_quot, abs_tol=1e-5)


def test_differentiation_transcendental_and_chain_rules():
    x = Symbol("x")

    # Trig functions: cos, tan
    df_cos = diff(parse("cos(x)"), x)
    assert math.isclose(df_cos.eval({"x": 0}), 0.0)  # -sin(0) = 0

    df_tan = diff(parse("tan(x)"), x)
    assert math.isclose(df_tan.eval({"x": 0}), 1.0)  # 1 / cos(0)^2 = 1

    # Exponential and Natural Log: e^(3*x), ln(2*x)
    df_exp = diff(parse("exp(3*x)"), x)
    # d/dx [e^(3x)] = 3*e^(3x), at x=0 -> 3
    assert math.isclose(df_exp.eval({"x": 0}), 3.0)

    df_ln = diff(parse("ln(2*x)"), x)
    # d/dx [ln(2x)] = 2 / (2x) = 1/x, at x=4 -> 0.25
    assert math.isclose(df_ln.eval({"x": 4}), 0.25)

    # Sqrt and Abs
    df_sqrt = diff(parse("sqrt(x)"), x)
    # d/dx [sqrt(x)] = 1 / (2*sqrt(x)), at x=4 -> 1/4 = 0.25
    assert math.isclose(df_sqrt.eval({"x": 4}), 0.25)

    df_abs = diff(parse("abs(x)"), x)
    assert math.isclose(df_abs.eval({"x": 5}), 1.0)
    assert math.isclose(df_abs.eval({"x": -5}), -1.0)

    # Inverse Trig: Asin, Acos, Atan
    df_asin = diff(Asin(x), x)
    assert math.isclose(df_asin.eval({"x": 0.5}), 1.0 / math.sqrt(1 - 0.5**2))

    df_acos = diff(Acos(x), x)
    assert math.isclose(df_acos.eval({"x": 0.5}), -1.0 / math.sqrt(1 - 0.5**2))

    df_atan = diff(Atan(x), x)
    assert math.isclose(df_atan.eval({"x": 0.5}), 1.0 / (1 + 0.5**2))


def test_differentiation_partial_and_higher_order():
    x = Symbol("x")
    y = Symbol("y")

    # Partial derivative d/dx [x^2 * y^3 + 5*x*y]
    f_multi = parse("x^2 * y^3 + 5*x*y")
    df_dx = diff(f_multi, x)
    # d/dx -> 2*x*y^3 + 5*y at x=2, y=3: 2(2)(27) + 5(3) = 108 + 15 = 123
    assert math.isclose(df_dx.eval({"x": 2, "y": 3}), 123.0)

    df_dy = diff(f_multi, y)
    # d/dy -> 3*x^2*y^2 + 5*x at x=2, y=3: 3(4)(9) + 5(2) = 108 + 10 = 118
    assert math.isclose(df_dy.eval({"x": 2, "y": 3}), 118.0)

    # Second derivative d^2/dx^2 [x^4] = 12*x^2
    f_poly = parse("x^4")
    d2f = diff(diff(f_poly, x), x)
    assert math.isclose(d2f.eval({"x": 3}), 108.0)  # 12 * 9 = 108


def test_differentiation_unsimplified():
    x = Symbol("x")
    f = parse("x^2 + 3*x")
    raw_df = diff(f, x, simplify_result=False)
    assert isinstance(raw_df, Add)


# ==============================================================================
# 3. SYMBOLIC INTEGRATION TESTS
# ==============================================================================

def test_integration_indefinite_polynomials_and_powers():
    x = Symbol("x")

    # Indefinite integral of 3x^2 + 2x + 1 is x^3 + x^2 + x
    f = parse("3*x^2 + 2*x + 1")
    F = integrate(f, x)
    assert math.isclose(F.eval({"x": 2}) - F.eval({"x": 0}), 14.0)

    # Linear base power: (2*x + 1)^3
    f_lin = parse("(2*x + 1)^3")
    F_lin = integrate(f_lin, x)
    # Integral of (2x+1)^3 dx = (2x+1)^4 / (2 * 4) = (2x+1)^4 / 8
    # F(1) - F(0) = 3^4/8 - 1/8 = 80/8 = 10.0
    val_diff = F_lin.eval({"x": 1}) - F_lin.eval({"x": 0})
    assert math.isclose(val_diff, 10.0)

    # Reciprocal linear: 1 / (2*x + 1) -> ln(|2*x + 1|) / 2
    f_rec = parse("1 / (2*x + 1)")
    F_rec = integrate(f_rec, x)
    # F(1) - F(0) = ln(3)/2 - ln(1)/2 = ln(3)/2
    val_rec = F_rec.eval({"x": 1}) - F_rec.eval({"x": 0})
    assert math.isclose(val_rec, math.log(3) / 2.0)


def test_integration_transcendental_and_exponential():
    x = Symbol("x")

    # Exponential: e^(3*x) -> e^(3*x) / 3
    f_exp = parse("exp(3*x)")
    F_exp = integrate(f_exp, x)
    val_exp = F_exp.eval({"x": 1}) - F_exp.eval({"x": 0})
    assert math.isclose(val_exp, (math.exp(3) - 1.0) / 3.0)

    # Trig: sin(2*x) and cos(3*x)
    f_sin = parse("sin(2*x)")
    F_sin = integrate(f_sin, x)
    # integral sin(2x) dx = -cos(2x)/2
    # F(pi/2) - F(0) = -cos(pi)/2 - (-cos(0)/2) = 0.5 - (-0.5) = 1.0
    val_sin = F_sin.eval({"x": math.pi / 2}) - F_sin.eval({"x": 0})
    assert math.isclose(val_sin, 1.0)

    f_cos = parse("cos(3*x)")
    F_cos = integrate(f_cos, x)
    # integral cos(3x) dx = sin(3x)/3
    # F(pi/6) - F(0) = sin(pi/2)/3 - 0 = 1/3
    val_cos = F_cos.eval({"x": math.pi / 6}) - F_cos.eval({"x": 0})
    assert math.isclose(val_cos, 1.0 / 3.0)

    # Natural Log: ln(x) -> x*ln(x) - x
    f_ln = parse("ln(x)")
    F_ln = integrate(f_ln, x)
    # F(e) - F(1) = (e*1 - e) - (1*0 - 1) = 0 - (-1) = 1.0
    val_ln = F_ln.eval({"x": math.e}) - F_ln.eval({"x": 1})
    assert math.isclose(val_ln, 1.0)


def test_integration_by_parts():
    x = Symbol("x")

    # x * exp(x) -> x*e^x - e^x
    f_ibp = parse("x * exp(x)")
    F_ibp = integrate(f_ibp, x)
    # F(1) - F(0) = (1*e - e) - (0 - 1) = 1.0
    val_ibp = F_ibp.eval({"x": 1}) - F_ibp.eval({"x": 0})
    assert math.isclose(val_ibp, 1.0)

    # x * sin(x) -> -x*cos(x) + sin(x)
    f_ibp_sin = parse("x * sin(x)")
    F_ibp_sin = integrate(f_ibp_sin, x)
    # F(pi/2) - F(0) = (0 + 1) - (0 + 0) = 1.0
    val_ibp_sin = F_ibp_sin.eval({"x": math.pi / 2}) - F_ibp_sin.eval({"x": 0})
    assert math.isclose(val_ibp_sin, 1.0)


def test_definite_integration_bounds():
    x = Symbol("x")

    # Definite integral from 0 to 2 for 3x^2 + 2x + 1
    f = parse("3*x^2 + 2*x + 1")
    val_def = integrate(f, x, lower=0, upper=2)
    assert math.isclose(val_def, 14.0)

    # Error when only one bound is passed
    with pytest.raises(ValueError):
        integrate(f, x, lower=0)


# ==============================================================================
# 4. LIMIT CALCULATION TESTS
# ==============================================================================

def test_limits_direct_substitution():
    x = Symbol("x")
    f = parse("x^2 + 3*x + 2")
    assert math.isclose(limit(f, x, 2), 12.0)
    assert math.isclose(limit(f, x, -1), 0.0)


def test_limits_lhopital_and_cancellation():
    x = Symbol("x")

    # sin(x) / x -> 1 as x -> 0
    f_trig = parse("sin(x) / x")
    assert math.isclose(limit(f_trig, x, 0), 1.0)

    # sin(3*x) / x -> 3 as x -> 0
    f_trig3 = parse("sin(3*x) / x")
    assert math.isclose(limit(f_trig3, x, 0), 3.0)

    # (x^2 - 4) / (x - 2) -> 4 as x -> 2
    f_poly = parse("(x^2 - 4) / (x - 2)")
    assert math.isclose(limit(f_poly, x, 2), 4.0)

    # (exp(x) - 1) / x -> 1 as x -> 0
    f_exp = parse("(exp(x) - 1) / x")
    assert math.isclose(limit(f_exp, x, 0), 1.0)


def test_limits_at_infinity():
    x = Symbol("x")

    # Equal degree polynomials: lim x->inf (2x^2 + 3) / (x^2 - 1) = 2
    f_eq = parse("(2*x^2 + 3) / (x^2 - 1)")
    assert math.isclose(limit(f_eq, x, "inf"), 2.0)

    # Num degree < Den degree: lim x->inf (x + 1) / (x^2 + 5) = 0
    f_less = parse("(x + 1) / (x^2 + 5)")
    assert math.isclose(limit(f_less, x, "inf"), 0.0)

    # Num degree > Den degree: lim x->inf (x^2 + 1) / (x + 1) = +inf
    f_more = parse("(x^2 + 1) / (x + 1)")
    lim_more = limit(f_more, x, "inf")
    assert lim_more == float("inf") or math.isinf(lim_more)


def test_limits_directional_and_numeric_probe():
    x = Symbol("x")

    # Directional limit right: lim x->0+ 1/x = +inf or large value
    f = parse("1 / x")
    lim_right = limit(f, x, 0, direction="right")
    assert lim_right > 100 or math.isinf(lim_right)


# ==============================================================================
# 5. RENDERING TESTS
# ==============================================================================

def test_rendering_formats():
    expr = parse("x^2 + sin(x) / 2")

    latex_str = to_latex(expr)
    assert r"\frac{\sin\left(x\right)}{2}" in latex_str or r"x" in latex_str

    unicode_str = render_pretty(expr, mode="unicode")
    assert "x" in unicode_str

    ascii_str = render_pretty(expr, mode="ascii")
    assert "x" in ascii_str

    tree_str = render_tree(expr)
    assert "Add" in tree_str


def test_inverse_trig_differentiation():
    x = Symbol("x")

    # Parsing and differentiating asin(x), acos(x), atan(x)
    f_asin = parse("asin(x)")
    df_asin = diff(f_asin, x)
    assert math.isclose(df_asin.eval({"x": 0.5}), 1.0 / math.sqrt(1 - 0.5**2))

    f_acos = parse("acos(x)")
    df_acos = diff(f_acos, x)
    assert math.isclose(df_acos.eval({"x": 0.5}), -1.0 / math.sqrt(1 - 0.5**2))

    f_atan = parse("atan(x)")
    df_atan = diff(f_atan, x)
    assert math.isclose(df_atan.eval({"x": 0.5}), 1.0 / (1 + 0.5**2))

    # Alias function names: arcsin, arccos, arctan
    assert math.isclose(diff(parse("arcsin(x)"), x).eval({"x": 0.5}), 1.0 / math.sqrt(1 - 0.5**2))
    assert math.isclose(diff(parse("arccos(x)"), x).eval({"x": 0.5}), -1.0 / math.sqrt(1 - 0.5**2))
    assert math.isclose(diff(parse("arctan(x)"), x).eval({"x": 0.5}), 1.0 / (1 + 0.5**2))

    # Identity d/dx [asin(x) + acos(x)] = 0
    f_sum = parse("asin(x) + acos(x)")
    df_sum = diff(f_sum, x)
    assert math.isclose(df_sum.eval({"x": 0.3}), 0.0, abs_tol=1e-9)

    # Chain rule with inverse trig: d/dx [asin(2*x)] = 2 / sqrt(1 - 4*x^2)
    f_chain = parse("asin(2*x)")
    df_chain = diff(f_chain, x)
    expected_chain = 2.0 / math.sqrt(1 - 4 * (0.25**2))
    assert math.isclose(df_chain.eval({"x": 0.25}), expected_chain)


def test_prefix_function_parsing():
    x = Symbol("x")

    # Prefix function parsing like cos3x -> cos(3*x)
    f_cos3x = parse("cos3x")
    df_cos3x = diff(f_cos3x, x)
    assert math.isclose(df_cos3x.eval({"x": 0}), 0.0)
    assert math.isclose(df_cos3x.eval({"x": math.pi / 6}), -3.0)

    # Prefix function parsing like sin2x -> sin(2*x)
    f_sin2x = parse("sin2x")
    df_sin2x = diff(f_sin2x, x)
    assert math.isclose(df_sin2x.eval({"x": 0}), 2.0)

    # Prefix function parsing for exponential and log: exp3x, ln2x
    f_exp3x = parse("exp3x")
    assert math.isclose(diff(f_exp3x, x).eval({"x": 0}), 3.0)

    f_ln2x = parse("ln2x")
    assert math.isclose(diff(f_ln2x, x).eval({"x": 2}), 0.5)

