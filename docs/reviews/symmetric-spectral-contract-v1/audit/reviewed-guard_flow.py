"""Candidate value-only dependency analysis; not production DSL validation."""
import ast
VALUE_ONLY={'principal_min_value','principal_max_value','principal_mid_value'}
NUMERIC={'principal_min','principal_max','principal_mid','principal_upper_sum','principal_lower_sum','projector_min','projector_max','sym','sqrt','exp','log','log1p','sin','cos','abs','min','max','trace','dev','dot','norm','cube_trace','tensor_square','expm','determinant','normalized_determinant'}
def dependencies(expression, aliases=None):
    aliases={} if aliases is None else aliases
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value) in (float,int):return frozenset()
        if isinstance(n,ast.Name):return aliases.get(n.id,frozenset())
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):return walk(n.operand)
        if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow)):return walk(n.left)|walk(n.right)
        if isinstance(n,ast.Compare) and len(n.ops)==1 and isinstance(n.ops[0],(ast.Gt,ast.GtE,ast.Lt,ast.LtE)):
            walk(n.left);walk(n.comparators[0]);return frozenset()
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and not n.keywords:
            name=n.func.id
            args=[walk(a) for a in n.args]
            if name=='select' and len(args)==3:return args[1]|args[2]
            if name in VALUE_ONLY and len(args)==1:return args[0]|{name}
            if name in NUMERIC:return frozenset().union(*args)
        raise ValueError('unsupported candidate qualifier syntax')
    return walk(ast.parse(expression,mode='eval').body)
def require_numeric_sink(expression,aliases=None):
    leaked=dependencies(expression,aliases)
    if leaked:raise ValueError('value-only dependency reaches numeric output: '+','.join(sorted(leaked)))
