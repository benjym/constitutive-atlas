"""Restricted tensor expressions: one AST for checking, interpretation and C++.

No eval, exec, attribute access, indexing, strings or arbitrary function calls.
Dimensions use (mass, length, time, temperature) SI exponents, including fractional powers.
"""
from __future__ import annotations
import ast
import math
import re
from dataclasses import dataclass
from fractions import Fraction

ZERO = (Fraction(0),) * 4
PRESSURE = (Fraction(1), Fraction(-1), Fraction(-2), Fraction(0))
TIME = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
DIMS = {"1": ZERO, "Pa": PRESSURE, "s": TIME,
        "K": (Fraction(0), Fraction(0), Fraction(0), Fraction(1))}


def dimensions(unit):
    if isinstance(unit, str) and unit in DIMS:
        return DIMS[unit]
    if isinstance(unit, dict) and set(unit) == {'si'}:
        values = unit['si']
        if isinstance(values, list) and len(values) == 4:
            def valid_exponent(v):
                return (type(v) in (int,float) and math.isfinite(v)) or (
                    isinstance(v,str) and re.fullmatch(r'-?[0-9]{1,3}/[1-9][0-9]?',v) is not None)
            if all(valid_exponent(v) for v in values):
                result = tuple(Fraction(str(v)) for v in values)
                if all(abs(v) <= 16 and v.denominator <= 16 for v in result):
                    return result
    raise ValidationError('unit must be 1, Pa, s, K or four bounded rational SI exponents')


@dataclass(frozen=True)
class Type:
    shape: str = "scalar"
    dim: tuple = ZERO

    def __post_init__(self):
        # Existing callers using the v0.1 mass/length/time tuple remain valid.
        if len(self.dim) == 3:
            object.__setattr__(self, 'dim', tuple(self.dim) + (Fraction(0),))


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Sym:
    v: tuple

    def __add__(self, other):
        return Sym(tuple(a + b for a, b in zip(self.v, other.v)))

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return Sym(tuple(-a for a in self.v))

    def __mul__(self, value):
        return Sym(tuple(a * value for a in self.v))

    __rmul__ = __mul__

    def __truediv__(self, value):
        return self * (1 / value)


I = Sym((1., 1., 1., 0., 0., 0.))


def trace(a):
    return sum(a.v[:3])


def dev(a):
    return a - I * (trace(a) / 3)


def dot(a, b):
    return sum(x * y for x, y in zip(a.v, b.v))


def cube_trace(a):
    x, y, z, xy, yz, xz = a.v
    xy, yz, xz = (v / math.sqrt(2) for v in (xy, yz, xz))
    return x**3 + y**3 + z**3 + 3*((x+y)*xy**2+(y+z)*yz**2+(x+z)*xz**2) + 6*xy*yz*xz


def tensor_square(a):
    """Mandel representation of the Cartesian matrix product A @ A."""
    x,y,z,u,v,w=a.v
    r=math.sqrt(2)
    return Sym((x*x+(u*u+w*w)/2, y*y+(u*u+v*v)/2,
                z*z+(v*v+w*w)/2, (x+y)*u+v*w/r,
                (y+z)*v+u*w/r, (x+z)*w+u*v/r))


FUNCTIONS = {"sym": lambda *values: Sym(tuple(values)), "sqrt": math.sqrt, "exp": math.exp, "log": math.log,
             "sin": math.sin, "cos": math.cos, "abs": abs,
             "min": min, "max": max, "trace": trace, "dev": dev,
             "dot": dot, "norm": lambda a: math.sqrt(dot(a, a)),
             "cube_trace": cube_trace, "tensor_square": tensor_square}


def parse(expression):
    if not isinstance(expression, str) or len(expression) > 10000:
        raise ValidationError("expression must be a string of at most 10000 characters")
    try:
        tree = ast.parse(expression, mode="eval").body
    except (SyntaxError, RecursionError) as exc:
        raise ValidationError(f"invalid expression: {expression}") from exc
    if sum(1 for _ in ast.walk(tree)) > 1000:
        raise ValidationError("expression is too complex")
    return tree


def constant_fraction(node):
    """Exact bounded-expression literals for dimensional powers, e.g. 1/3."""
    if isinstance(node,ast.Constant) and type(node.value) in (int,float) and math.isfinite(node.value):
        return Fraction(str(node.value))
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
        value=constant_fraction(node.operand)
        return -value if isinstance(node.op,ast.USub) else value
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div):
        return constant_fraction(node.left)/constant_fraction(node.right)
    raise ValueError('nonconstant dimensional exponent')


def infer(node, symbols):
    if isinstance(node, ast.Constant):
        if type(node.value) not in (float, int) or not math.isfinite(node.value):
            raise ValidationError("only finite numeric literals are allowed")
        return Type()
    if isinstance(node, ast.Name):
        if node.id not in symbols:
            raise ValidationError(f"undefined symbol: {node.id}")
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return infer(node.operand, symbols)
    if isinstance(node, ast.BinOp):
        a, b = infer(node.left, symbols), infer(node.right, symbols)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            if a != b:
                raise ValidationError(f"addition/subtraction requires equal types: {a}, {b}")
            return a
        if isinstance(node.op, (ast.Mult, ast.Div)):
            if (a.shape == b.shape == "sym") or (isinstance(node.op, ast.Div) and b.shape != "scalar"):
                raise ValidationError("tensor multiplication is explicit: use dot; divisor must be scalar")
            sign = -1 if isinstance(node.op, ast.Div) else 1
            return Type("sym" if "sym" in (a.shape, b.shape) else "scalar",
                        tuple(x + sign*y for x, y in zip(a.dim, b.dim)))
        if isinstance(node.op, ast.Pow):
            if a.shape != "scalar" or b != Type():
                raise ValidationError("power requires scalar base and dimensionless exponent")
            if a.dim == ZERO:
                return Type()
            try:
                exponent = constant_fraction(node.right)
            except (ValueError, TypeError, ZeroDivisionError):
                raise ValidationError("dimensioned power requires a constant exponent")
            return Type(dim=tuple(x*exponent for x in a.dim))
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.Gt, ast.GtE, ast.Lt, ast.LtE)):
        a, b = infer(node.left, symbols), infer(node.comparators[0], symbols)
        if a != b or a.shape != "scalar":
            raise ValidationError("comparison requires equally dimensioned scalars")
        return Type("bool")
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        name = node.func.id
        args = [infer(a, symbols) for a in node.args]
        if name == "select" and len(args) == 3:
            if args[0] != Type("bool") or args[1] != args[2]:
                raise ValidationError("select requires condition and equally typed branches")
            return args[1]
        if name == "sym":
            if len(args)!=6 or any(a.shape!="scalar" or a!=args[0] for a in args):
                raise ValidationError("sym requires six equally dimensioned scalars in Mandel order")
            return Type("sym",args[0].dim)
        arity = 2 if name in ("dot", "min", "max") else 1
        if name not in FUNCTIONS or len(args) != arity:
            raise ValidationError(f"unsupported function or arity: {name}")
        a = args[0]
        if name in ("trace", "dev", "norm", "cube_trace", "dot", "tensor_square"):
            if a.shape != "sym" or (name == "dot" and args[1].shape != "sym"):
                raise ValidationError(f"{name} requires symmetric tensors")
            if name == "dot":
                return Type(dim=tuple(x+y for x,y in zip(a.dim,args[1].dim)))
            return Type("sym" if name in ("dev", "tensor_square") else "scalar", tuple(x*(3 if name == "cube_trace" else 2 if name == "tensor_square" else 1) for x in a.dim))
        if a.shape != "scalar":
            raise ValidationError(f"{name} requires scalar")
        if name in ("min", "max") and a != args[1]:
            raise ValidationError(f"{name} arguments must have matching dimensions")
        if name in ("exp", "log", "sin", "cos") and a.dim != ZERO:
            raise ValidationError(f"{name} requires dimensionless argument")
        return Type(dim=tuple(x/2 for x in a.dim)) if name == "sqrt" else a
    raise ValidationError(f"unsupported syntax: {ast.dump(node)}")


def evaluate(node, symbols):
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        return symbols[node.id]
    if isinstance(node, ast.UnaryOp):
        value = evaluate(node.operand, symbols)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        a, b = evaluate(node.left, symbols), evaluate(node.right, symbols)
        if isinstance(node.op, ast.Add): return a+b
        if isinstance(node.op, ast.Sub): return a-b
        if isinstance(node.op, ast.Mult): return a*b
        if isinstance(node.op, ast.Div): return a/b
        if isinstance(node.op, ast.Pow): return math.pow(a,b)
    if isinstance(node, ast.Compare):
        a,b = evaluate(node.left, symbols),evaluate(node.comparators[0], symbols)
        op = node.ops[0]
        if isinstance(op, ast.Gt): return a>b
        if isinstance(op, ast.GtE): return a>=b
        if isinstance(op, ast.Lt): return a<b
        return a<=b
    if isinstance(node, ast.Call):
        name = node.func.id
        if name == "select":
            return evaluate(node.args[1] if evaluate(node.args[0], symbols) else node.args[2], symbols)
        return FUNCTIONS[name](*(evaluate(a, symbols) for a in node.args))
    raise ValidationError("invalid AST")


def cpp(node):
    if isinstance(node, ast.Constant): return f"T({float(node.value)!r})"
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.UnaryOp): return f"({'-' if isinstance(node.op,ast.USub) else '+'}{cpp(node.operand)})"
    if isinstance(node, ast.BinOp):
        a,b=cpp(node.left),cpp(node.right)
        if isinstance(node.op,ast.Pow): return f"apow({a}, {b})"
        op={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(node.op)]
        return f"({a} {op} {b})"
    if isinstance(node,ast.Compare):
        op={ast.Gt:'>',ast.GtE:'>=',ast.Lt:'<',ast.LtE:'<='}[type(node.ops[0])]
        return f"({cpp(node.left)} {op} {cpp(node.comparators[0])})"
    if isinstance(node,ast.Call):
        name=node.func.id
        if name=='select': return f"({cpp(node.args[0])} ? {cpp(node.args[1])} : {cpp(node.args[2])})"
        name={'tensor_square':'atlas::tensor_square','sym':'make_sym','min':'amin','max':'amax','sqrt':'asqrt','exp':'aexp','log':'alog','sin':'asin','cos':'acos','abs':'aabs'}.get(name,name)
        return f"{name}({', '.join(cpp(a) for a in node.args)})"
    raise ValidationError("invalid AST")
