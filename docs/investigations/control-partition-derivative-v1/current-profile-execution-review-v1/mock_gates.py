"""Pure extracted guard predicates with synthetic values. No assessor mains/artifacts."""
import sys
sys.dont_write_bytecode=True
import ast,copy,json
from pathlib import Path
S=Path('/private/tmp/atlas-control-partition-support-v4/source');passed=[]
def check(name,value):
 assert value,name
 passed.append(name)
t=ast.parse((S/'tools/build_maxwell_laboratory.py').read_text());ns={}
for n in t.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='GATES' for x in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'pure-literal','exec'),ns)
 if isinstance(n,ast.FunctionDef) and n.name=='passed_gates':exec(compile(ast.Module(body=[n],type_ignores=[]),'pure-predicate','exec'),ns)
g={x:True for x in ns['GATES']};check('Maxwell full gates',ns['passed_gates'](g))
for key in g:
 for val in [False,1,'true',None]:
  bad={**g,key:val};check('Maxwell rejects '+key+' '+repr(val),not ns['passed_gates'](bad))
 bad=dict(g);del bad[key];check('Maxwell rejects missing '+key,not ns['passed_gates'](bad))
check('Maxwell rejects extra',not ns['passed_gates']({**g,'fabricated':True}))
# Extract the exact guard expression for independent-review identity; no file I/O.
for filename,needle in [('build_maxwell_laboratory.py','reviewer_run'),('build_controlled_path_web.py','reviewer_run')]:
 tree=ast.parse((S/'tools'/filename).read_text());node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and needle in ast.unparse(n.test) and 'accepted.get' in ast.unparse(n.test))
 expr=compile(ast.Expression(node.test),'original-independent-review-predicate','eval')
 # Remaining hash/path predicates are replaced by explicitly mocked pure adapters.
 import hashlib
 accepted_bytes=b'pure-synthetic';digest=hashlib.sha256(accepted_bytes).hexdigest();binding={'synthetic':'binding'};gates=dict(g) if filename=='build_maxwell_laboratory.py' else {'synthetic':True}
 base={'accepted':{'status':'accepted','binding':binding,'gates':gates,'reviewer_run':'reviewer'},'binding':binding,'gates':gates,'reviewer':{'sha256':digest},'qualification':{'implementation_run':'implementation'},'hashlib':hashlib,'accepted_review_bytes':accepted_bytes,'accepted_bytes':accepted_bytes,'digest':lambda x:hashlib.sha256(x).hexdigest(),'passed_gates':ns['passed_gates']}
 check(filename+' distinct genuine IDs accepts',not eval(expr,base))
 for mode in ['same-run','missing-run','empty-run','wrong-binding','wrong-gates','not-accepted','wrong-review-hash']:
  x=copy.deepcopy({k:v for k,v in base.items() if k not in ('hashlib','digest','passed_gates')});x.update(hashlib=hashlib,digest=base['digest'],passed_gates=ns['passed_gates'])
  if mode=='same-run':x['accepted']['reviewer_run']='implementation'
  elif mode=='missing-run':del x['accepted']['reviewer_run']
  elif mode=='empty-run':x['accepted']['reviewer_run']=' '
  elif mode=='wrong-binding':x['accepted']['binding']={}
  elif mode=='wrong-gates':x['accepted']['gates']={}
  elif mode=='not-accepted':x['accepted']['status']='pending'
  else:x['reviewer']['sha256']='wrong'
  check(filename+' rejects '+mode,eval(expr,x))
print(json.dumps({'identity':'pure-guard-mocks-v1','passed':True,'synthetic_only':True,'checks':len(passed),'check_names':passed,'compiled_calls':0,'collector_calls':0,'assessment_main_calls':0},indent=2))
