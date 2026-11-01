"""Standalone bounded Decimal AST mathematics, never an Atlas production import."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
import ast
from dataclasses import dataclass
from contextlib import contextmanager
from decimal import Decimal,localcontext,InvalidOperation,DivisionByZero,Overflow,ROUND_HALF_EVEN

class Rejected(ValueError):pass
@dataclass(frozen=True)
class Sym:
    v:tuple
    def __post_init__(self):
        if len(self.v)!=6 or any(type(x)is not Decimal or not x.is_finite()for x in self.v):raise Rejected('finite Decimal Mandel tensor required')

def binary(x):
    if type(x)is int:return Decimal.from_float(float(x))
    if type(x)is float:return finite(Decimal.from_float(x))
    raise Rejected('binary64 real required')
def finite(x):
    if type(x)is Decimal:
        if not x.is_finite():raise Rejected('nonfinite scalar')
    elif type(x)is not bool and not isinstance(x,Sym):raise Rejected('invalid value type')
    return x
def scalar(x):
    if type(x)is not Decimal:raise Rejected('scalar required')
    return x
def tensor(x):
    if not isinstance(x,Sym):raise Rejected('tensor required')
    return x

def operation(op,a,b):
    if isinstance(op,(ast.Add,ast.Sub)):
        sign=Decimal(1)if isinstance(op,ast.Add)else Decimal(-1)
        if isinstance(a,Sym)and isinstance(b,Sym):return Sym(tuple(x+sign*y for x,y in zip(a.v,b.v)))
        return scalar(a)+sign*scalar(b)
    if isinstance(op,ast.Mult):
        if isinstance(a,Sym):return Sym(tuple(x*scalar(b)for x in a.v))
        if isinstance(b,Sym):return Sym(tuple(scalar(a)*x for x in b.v))
        return scalar(a)*scalar(b)
    if isinstance(op,ast.Div):
        den=scalar(b)
        if isinstance(a,Sym):return Sym(tuple(x/den for x in a.v))
        return scalar(a)/den
    if isinstance(op,ast.Pow):
        a,b=scalar(a),scalar(b)
        if b==b.to_integral_value():return a**int(b)
        if a<=0:raise Rejected('fractional power positive base required')
        return (b*a.ln()).exp()
    raise Rejected('operator unsupported')

ARITY={'sqrt':1,'log':1,'abs':1,'min':2,'max':2,'select':3,'trace':1,'dev':1,'dot':2,'norm':1,'cube_trace':1}
def parse(text):
    if type(text)is not str or len(text)>4096:raise Rejected('expression size')
    try:root=ast.parse(text,mode='eval').body
    except(SyntaxError,ValueError)as exc:raise Rejected('syntax')from exc
    nodes=list(ast.walk(root))
    if len(nodes)>512:raise Rejected('AST size')
    allowed=(ast.Constant,ast.Name,ast.Load,ast.UnaryOp,ast.UAdd,ast.USub,ast.BinOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Compare,ast.Gt,ast.GtE,ast.Lt,ast.LtE,ast.Call)
    for n in nodes:
        if not isinstance(n,allowed):raise Rejected('AST unsupported')
        if isinstance(n,ast.Constant)and(type(n.value)not in(int,float)):raise Rejected('real literal required')
        if isinstance(n,ast.Call)and(not isinstance(n.func,ast.Name)or n.func.id not in ARITY or len(n.args)!=ARITY[n.func.id]or n.keywords):raise Rejected('call unsupported')
        if isinstance(n,ast.Compare)and(len(n.ops)!=1 or len(n.comparators)!=1):raise Rejected('one comparison required')
    return root

def evaluate(node,env):
    if not __debug__:raise RuntimeError('Unoptimized Python required')
    try:return finite(_eval(node,env))
    except(InvalidOperation,DivisionByZero,Overflow,OverflowError,KeyError)as exc:raise Rejected(str(exc))from exc

def _eval(n,e):
    if isinstance(n,ast.Constant):return binary(n.value)
    if isinstance(n,ast.Name):
        if n.id not in e:raise Rejected('missing symbol '+n.id)
        return finite(e[n.id])
    if isinstance(n,ast.UnaryOp):
        a=evaluate(n.operand,e)
        if type(a)is bool:raise Rejected('boolean unary')
        if isinstance(n.op,ast.UAdd):return a
        if isinstance(a,Sym):return Sym(tuple(-x for x in a.v))
        return -scalar(a)
    if isinstance(n,ast.BinOp):return operation(n.op,evaluate(n.left,e),evaluate(n.right,e))
    if isinstance(n,ast.Compare):
        a,b=scalar(evaluate(n.left,e)),scalar(evaluate(n.comparators[0],e));op=n.ops[0]
        if isinstance(op,ast.Gt):return a>b
        if isinstance(op,ast.GtE):return a>=b
        if isinstance(op,ast.Lt):return a<b
        if isinstance(op,ast.LtE):return a<=b
        raise Rejected('comparison unsupported')
    if isinstance(n,ast.Call):
        name=n.func.id
        if name=='select':
            cond=evaluate(n.args[0],e)
            if type(cond)is not bool:raise Rejected('select condition bool required')
            return evaluate(n.args[1]if cond else n.args[2],e)
        args=[evaluate(x,e)for x in n.args];a=args[0]
        if name=='sqrt':return scalar(a).sqrt()
        if name=='log':return scalar(a).ln()
        if name=='abs':return abs(scalar(a))
        if name in ['min','max']:return (min if name=='min'else max)(scalar(a),scalar(args[1]))
        v=tensor(a).v
        if name=='trace':return sum(v[:3],Decimal(0))
        if name=='dev':
            p=sum(v[:3],Decimal(0))/3
            return Sym(tuple(x-(p if i<3 else 0)for i,x in enumerate(v)))
        if name=='dot':return sum((x*y for x,y in zip(v,tensor(args[1]).v)),Decimal(0))
        if name=='norm':return sum((x*x for x in v),Decimal(0)).sqrt()
        if name=='cube_trace':
            s=Decimal(2).sqrt();M=((v[0],v[3]/s,v[5]/s),(v[3]/s,v[1],v[4]/s),(v[5]/s,v[4]/s,v[2]))
            return sum((M[i][j]*M[j][k]*M[k][i]for i in range(3)for j in range(3)for k in range(3)),Decimal(0))
    raise Rejected('unsupported node')

def infer(n,e):
    if isinstance(n,ast.Constant):binary(n.value);return 'scalar'
    if isinstance(n,ast.Name):
        if n.id not in e:raise Rejected('missing symbol '+n.id)
        x=finite(e[n.id]);return 'sym'if isinstance(x,Sym)else 'bool'if type(x)is bool else 'scalar'
    if isinstance(n,ast.UnaryOp):
        a=infer(n.operand,e)
        if a=='bool':raise Rejected('unary type')
        return a
    if isinstance(n,ast.BinOp):
        a,b=infer(n.left,e),infer(n.right,e)
        if isinstance(n.op,(ast.Add,ast.Sub))and a==b and a in ['scalar','sym']:return a
        if isinstance(n.op,ast.Mult)and a in ['scalar','sym']and b in ['scalar','sym']and 'scalar'in [a,b]:return 'sym'if 'sym'in [a,b]else 'scalar'
        if isinstance(n.op,ast.Div)and a in ['scalar','sym']and b=='scalar':return a
        if isinstance(n.op,ast.Pow)and a==b=='scalar':return 'scalar'
        raise Rejected('binary type')
    if isinstance(n,ast.Compare):
        if infer(n.left,e)!= 'scalar'or infer(n.comparators[0],e)!='scalar':raise Rejected('compare type')
        return 'bool'
    if isinstance(n,ast.Call):
        name=n.func.id;types=[infer(a,e)for a in n.args]
        if name=='select':
            if types[0]!='bool'or types[1]!=types[2]:raise Rejected('select type')
            return types[1]
        expected=['sym','sym']if name=='dot'else ['sym']if name in ['trace','dev','norm','cube_trace']else ['scalar']*ARITY[name]
        if types!=expected:raise Rejected('call type')
        return 'sym'if name=='dev'else 'scalar'
    raise Rejected('unsupported type node')
def expression(text,env):
    node=parse(text);infer(node,env);return evaluate(node,env)
@contextmanager
def context(precision):
    with localcontext()as ctx:
        ctx.prec=precision;ctx.rounding=ROUND_HALF_EVEN
        for signal in [InvalidOperation,DivisionByZero,Overflow]:ctx.traps[signal]=True
        yield ctx

def evaluate_model(model,state,previous,loading,parameters):
    f=model.get('formulation',{})
    if model.get('schema_version')!='0.3'or f.get('equation_form')!='incremental_residual'or f.get('time_dependence')!='strain_path'or f.get('kinematics')!='small_strain_3d'or f.get('tensor_representation')!='mandel':raise Rejected('unsupported formulation')
    if any(model.get(k)for k in ['history','events','increment_reset','observables']):raise Rejected('unsupported model feature')
    fields=model['state'];names=[x['name']for x in fields]
    if len(set(names))!=len(names)or set(state)!=set(names)or set(previous)!=set(names)or set(model['equations'])!=set(names):raise Rejected('state/equation layout')
    if set(parameters)!=set(model['parameters']):raise Rejected('parameter layout')
    env={'I':Sym((Decimal(1),Decimal(1),Decimal(1),Decimal(0),Decimal(0),Decimal(0))),'de':Sym(tuple(loading))}
    for k,v in parameters.items():
        if k in env:raise Rejected('duplicate symbol')
        env[k]=scalar(finite(v))
        definition=model['parameters'][k]
        for bound,cmp in [('min',lambda a,b:a<b),('max',lambda a,b:a>b)]:
            if bound in definition and cmp(v,binary(definition[bound])):raise Rejected('parameter range')
    for field in fields:
        n=field['name'];shape=field['shape']
        if shape not in ['sym','scalar']or n in env or n+'_n'in env:raise Rejected('state symbol/shape')
        wrap=lambda x:Sym(tuple(x))if shape=='sym'else scalar(finite(x))
        env[n]=wrap(state[n]);env[n+'_n']=wrap(previous[n])
    for d in model['derived']:
        if d['name']in env:raise Rejected('duplicate derived')
        env[d['name']]=expression(d['expr'],env)
    for condition in model['domain']:
        if expression(condition,env)is not True:raise Rejected('model domain '+condition)
    out=[]
    for field in fields:
        x=expression(model['equations'][field['name']],env)
        if field['shape']=='sym':out.extend(tensor(x).v)
        else:out.append(scalar(x))
    return out,env
