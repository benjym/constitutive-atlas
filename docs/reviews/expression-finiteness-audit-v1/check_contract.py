"""Independent bounded executed-node oracle; no repository imports or binaries."""
import ast
import hashlib
import json
import math
from pathlib import Path

class Rejected(ValueError):
    pass

def finite(value):
    if type(value) is bool:
        return value
    if type(value) in (int, float):
        try:
            result = float(value)
        except (OverflowError, ValueError):
            raise Rejected('scalar conversion')
        if math.isfinite(result):
            return result
    if type(value) is tuple and len(value) == 6:
        if all(type(v) in (int, float) and math.isfinite(v) for v in value):
            return value
    raise Rejected('executed node nonfinite or malformed')

def evaluate(node, env):
    def visit(n):
        if isinstance(n, ast.Constant):
            result = n.value
        elif isinstance(n, ast.Name):
            result = env[n.id]
        elif isinstance(n, ast.UnaryOp):
            operand = visit(n.operand)
            result = -operand if isinstance(n.op, ast.USub) else +operand
        elif isinstance(n, ast.BinOp):
            a, b = visit(n.left), visit(n.right)
            if isinstance(n.op, ast.Add): result = a+b
            elif isinstance(n.op, ast.Sub): result = a-b
            elif isinstance(n.op, ast.Mult): result = a*b
            elif isinstance(n.op, ast.Div): result = a/b
            elif isinstance(n.op, ast.Pow): result = math.pow(a,b)
            else: raise Rejected('unsupported operation')
        elif isinstance(n, ast.Compare):
            a, b = visit(n.left), visit(n.comparators[0])
            op = n.ops[0]
            result = (a < b if isinstance(op, ast.Lt) else a <= b if isinstance(op, ast.LtE)
                      else a > b if isinstance(op, ast.Gt) else a >= b)
        elif isinstance(n, ast.Call):
            name = n.func.id
            if name == 'select':
                result = visit(n.args[1] if visit(n.args[0]) else n.args[2])
            else:
                args = [visit(a) for a in n.args]
                if name == 'sym': result = tuple(args)
                elif name == 'norm': result = math.sqrt(sum(v*v for v in args[0]))
                elif name == 'dot': result = sum(a*b for a,b in zip(*args))
                elif name == 'trace': result = sum(args[0][:3])
                else:
                    fn = {'min': min, 'max': max, 'abs': abs, 'sqrt': math.sqrt,
                          'exp': math.exp, 'log': math.log, 'sin': math.sin,
                          'cos': math.cos, 'log1p': math.log1p}[name]
                    result = fn(*args)
        else:
            raise Rejected('unsupported AST')
        return finite(result)
    return visit(node)

ENV = {'h': 1e308, 't': 1e-308, 'z': 0.0,
       'a': (1e308, -1e308, 0.0, 0.0, 0.0, 0.0),
       'bad': (1.0, 2.0, 3.0, 0.0, math.inf, 0.0),
       'nan': math.nan, 'inf': math.inf,
       'sub': float.fromhex('0x0.0000000000001p-1022')}
# Boolean expected status is finite-node contract, not source-equation accuracy.
CASES = [
 ('overflow-product-predicate', 'select(h*h > 0, 1, 2)', False),
 ('overflow-sum-predicate', 'select(h+h > 0, 1, 2)', False),
 ('overflow-division-predicate', 'select(h/t > 0, 1, 2)', False),
 ('overflow-power-predicate', 'select(h**2 > 0, 1, 2)', False),
 ('overflow-norm-predicate', 'select(norm(a) > 0, 1, 2)', False),
 ('overflow-dot-predicate', 'select(dot(a,a) > 0, 1, 2)', False),
 ('exp-negative-overflow', 'exp(-h*h)', False),
 ('reciprocal-overflow-product', '1/(h*h)', False),
 ('min-invalid-first', 'min(h*h, 1)', False),
 ('min-invalid-second', 'min(1, h*h)', False),
 ('max-invalid-first', 'max(-h*h, 1)', False),
 ('max-invalid-second', 'max(1, -h*h)', False),
 ('sqrt-invalid-min', 'min(1, sqrt(-1))', False),
 ('exp-invalid-min', 'min(1, exp(1000))', False),
 ('log-invalid-max', 'max(1, log(0))', False),
 ('division-zero-min', 'min(1, 1/z)', False),
 ('invalid-tensor-unused-shear', 'trace(bad)', False),
 ('nan-name-predicate', 'select(nan < 0, 1, 2)', False),
 ('inf-name-predicate', 'select(inf > 0, 1, 2)', False),
 ('lazy-unselected-true', 'select(1 > 0, 7, exp(1000))', True),
 ('lazy-unselected-false', 'select(1 < 0, 1/z, 7)', True),
 ('lazy-nested', 'select(1 > 0, select(2 > 0, 7, h*h), 1/z)', True),
 ('selected-invalid', 'select(1 > 0, h*h, 7)', False),
 ('finite-min', 'min(1, 2)', True),
 ('finite-max', 'max(1, 2)', True),
 ('underflow-permitted', 't*t', True),
 ('subnormal-permitted', 'sub', True),
 ('negative-zero-permitted', '-z', True),
 ('finite-bool', '1 < 2', True),
 ('finite-tensor', 'sym(1,2,3,4,5,6)', True),
 ('finite-transcendentals', 'sin(1)+cos(1)+log1p(1)+sqrt(4)+abs(-1)', True),
]

def main():
    rows=[]
    for identifier, expression, expected in CASES:
        try:
            result=evaluate(ast.parse(expression, mode='eval').body, ENV)
            accepted=True
        except (Rejected, ArithmeticError, ValueError):
            accepted=False
        assert accepted == expected, (identifier, accepted, expected)
        rows.append({'id': identifier, 'expression': expression, 'expected_accepted': expected,
                     'observed_accepted': accepted})
    malformed=[(1,2,3), (1,2,3,4,5,6,7), (1,2,3,4,5,True),
               (1,2,3,4,5,'6'), (1,2,3,4,5,math.nan), 10**10000, complex(1,0), '1', None]
    for value in malformed:
        try: finite(value)
        except (Rejected, ArithmeticError, ValueError): pass
        else: raise AssertionError('malformed value accepted')
    print(json.dumps({'version':'expression-finiteness-contract-oracle-v1',
        'expression_checks':len(rows), 'malformed_value_checks':len(malformed),
        'compiled':False, 'production_runtime_executed':False, 'rows':rows},indent=2))

if __name__=='__main__': main()
