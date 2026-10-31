from pathlib import Path
import json,copy,struct,hashlib,shutil
from atlas.compiler import generate
from atlas.history_compiler import generate as history_generate
r=Path('/Users/bmar5496/code/constitutive-atlas');s=r/'catalogue/investigations/trace-generated-context-v1';s.mkdir();(s/'models').mkdir();(s/'generated').mkdir()
write=lambda p,x:p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
bits=lambda x:struct.pack('>d',float(x)).hex()
base=json.loads((r/'tests/fixtures/log1p/direct.json').read_text());physical=json.loads((r/'tests/fixtures/log1p/time-observable.json').read_text())
expressions={'predicate':'select(trace(A)>0,1,2)','eager':'0*trace(A)+1','lazy-then':'select(1>0,1,trace(A))','lazy-else':'select(1<0,trace(A),1)','dev-predicate':'select(norm(dev(A))>0,1,2)','direct':'trace(A)'}
models=[];metadata=[]
for context in ['equation','derived','domain','initial','observable','reset-guard','reset-value']:
 for variant,expr in expressions.items():
  m=copy.deepcopy(physical if context=='observable' else base);m['id']='trace-'+context+'-'+variant;m['name']=m['id'];m['description']='Synthetic generated expression conformance; not constitutive literature.'
  m['derived']=[];m['domain']=[]
  m['equations']={'sigma':'0*K*strain_rate','A':'0*strain_rate'}if context=='observable'else{'sigma':'0*K*I','A':'0*I'}
  m.pop('observables',None)
  if context=='equation':m['equations']['sigma']='K*('+expr+')*I'
  elif context=='derived':m['derived']=[{'name':'probe','expr':expr}]
  elif context=='domain':m['domain']=['('+expr+')>=0']
  elif context=='initial':m['initial_checks']=['('+expr+')>=0']
  elif context=='observable':m['observables']=[{'name':'stress','shape':'sym','unit':'Pa','scale':'K','expr':'K*('+expr+')*I'}]
  elif context=='reset-guard':m['increment_reset']={'scope':'parent_increment','updates':[{'target':'A','guard':'-1*('+expr+')','value':'I'}]}
  else:m['increment_reset']={'scope':'parent_increment','updates':[{'target':'A','guard':'-1','value':'('+expr+')*I'}]}
  models.append(m);metadata.append((m['id'],context,variant))
# Legal parameter-only trace scales, a masked invalid expression, lazy scale,
# and dev overflow. Defaults are valid; actual alternate params can fail.
for context in ['state-scale','observable-scale']:
 for variant in ['trace','lazy-then','lazy-else','dev']:
  m=copy.deepcopy(physical if context=='observable-scale' else base);m['id']='trace-'+context+'-'+variant;m['name']=m['id'];m['parameters']['r']={'default':1,'min':-1,'max':1e308,'unit':'1'}
  a='sym(r,r,r,0,0,0)'
  expr={'trace':f'select(trace({a})>0,1,2)','lazy-then':f'select(1>0,1,trace({a}))','lazy-else':f'select(1<0,trace({a}),1)','dev':'select(norm(dev(sym(r,-r,-r,0,0,0)))>0,1,2)'}[variant]
  if context=='state-scale':m['state'][0]['scale']='K*('+expr+')';m['equations']={'sigma':'0*K*I','A':'0*I'}
  else:m['observables'][0]['scale']='K*('+expr+')'
  models.append(m);metadata.append((m['id'],context,variant))
paths=[]
for m in models:
 p=s/'models'/(m['id']+'.json');write(p,m);paths.append(p)
generate(s/'generated',paths)
metadata.sort();index={name:i for i,(name,_,_)in enumerate(metadata)}
model_byid={m['id']:m for m in models}
fixtures=[];expected=[]
M=float.fromhex('0x1.fffffffffffffp1023');good=[3.,0.,0.,0.,0.,0.];bad=[M,M,M,0.,0.,0.];devbad=[M,-M,-M,0.,0.,0.]
def add(name,model,A,ok,values,*,initial=True,check=False,observe=False,seed=0,column=0,component=0,param=1.,derivatives=None):
 kind=metadata[index[model]][1]
 fixtures.append({'id':name,'model':index[model],'kind':kind,'A':A,'initial':initial,'check':check,'observe':observe,'seed':seed,'column':column,'component':component,'param':param})
 expected.append({'id':name,'ok':ok,'input_unchanged':True,'values_bits':[bits(x)if x!='nan'else'nan'for x in values]if ok else [],'derivative_bits':derivatives or []})
def output(context,scalar):
 if context in ['equation','observable']:return [scalar]*3+[0.]*3+([]if context=='observable'else[0.]*6)
 if context.startswith('reset'):return [0.]*6+[scalar]*3+[0.]*3
 return [0.]*12
for name,context,variant in metadata:
 if 'scale'in context:
  size=6 if context=='observable-scale'else 12
  add(name+'/good',name,good,True,[1.]*size)
  selected=variant not in ['lazy-then','lazy-else']
  add(name+'/extreme',name,good,True,['nan']*size if selected else[1.]*size,param=1e308)
  add(name+'/recover',name,good,True,[1.]*size)
  continue
 scalar={'predicate':1.,'eager':1.,'lazy-then':1.,'lazy-else':1.,'dev-predicate':1.,'direct':3.}[variant]
 # Guard variant's sign deliberately fires for every ordinary positive scalar.
 if context=='reset-guard':scalar=1.
 kw={'observe':context=='observable'}
 add(name+'/good',name,good,True,output(context,scalar),**kw)
 skip=variant in ['lazy-then','lazy-else']
 add(name+'/overflow',name,devbad if variant=='dev-predicate'else bad,skip,output(context,1.)if skip else[],**kw)
 add(name+'/recover',name,good,True,output(context,scalar),**kw)
 if context=='initial':add(name+'/disabled',name,bad,True,[0.]*12,initial=False)
 if context in ['equation','observable']:add(name+'/check-only',name,bad,True,[],check=True,**kw)
 if context=='observable':add(name+'/normal-skips-observable',name,bad,True,[0.]*12)
 if variant=='direct' and context in ['equation','observable','reset-value']:
  ds=[bits((-1e-130 if j%2 else 1e-130))for j in range(38)]
  derivative=[[x]*3+['0000000000000000']*3+([]if context=='observable'else['0000000000000000']*6)for x in ds]
  if context=='reset-value':derivative=[['0000000000000000']*6+[x]*3+['0000000000000000']*3 for x in ds]
  add(name+'/cancellation',name,[500.,1e-130,-500.,0.,0.,0.],True,output(context,1e-130),seed=4,derivatives=derivative,**kw)
  derivative=[[bits(M)]*3+['0000000000000000']*3+([]if context=='observable'else['0000000000000000']*6)for j in range(38)]
  if context=='reset-value':derivative=[['0000000000000000']*6+[bits(M)]*3+['0000000000000000']*3 for j in range(38)]
  add(name+'/intermediate-overflow',name,[M,M,-M,0.,0.,0.],True,output(context,M),seed=5,derivatives=derivative,**kw)
 if variant=='predicate':
  for component in range(6):
   for column in range(38):
    for seed in [1,2,3]:
     ident=f'{name}/bad-seed-{component}-{column}-{seed}'
     add(ident,name,good,False,[],seed=seed,component=component,column=column,**kw)
     add(ident+'/recover',name,good,True,output(context,1. if context!='reset-guard'else 1.),**kw)
 if variant in ['predicate','dev-predicate']:
  for column in range(38):
   seed=6 if variant=='predicate'else 7;ident=f'{name}/finite-seed-overflow-{column}'
   add(ident,name,good,False,[],seed=seed,column=column,**kw)
   add(ident+'/recover',name,good,True,output(context,1.),**kw)
write(s/'cases.json',fixtures);write(s/'expected.json',expected)
# Input-only fixtures: expected results stay exclusively in independent JSON.
lines=['#pragma once','struct TraceCase { const char* id; int model; const char* kind; double a[6]; bool initial,check,observe; int seed,column,component; double param; };','static const TraceCase trace_cases[]={']
for f in fixtures:
 lines.append('{'+json.dumps(f['id'])+','+str(f['model'])+','+json.dumps(f['kind'])+',{'+','.join(float(x).hex()for x in f['A'])+'},'+','.join(str(f[k]).lower()for k in ['initial','check','observe'])+','+','.join(str(f[k])for k in ['seed','column','component'])+','+float(f['param']).hex()+'},')
lines+=['};'];(s/'generated/cases.hpp').write_text('\n'.join(lines)+'\n')
# Four actual generated history contexts and late failure after prepare.
programs=[];history_expected=[]
for context in ['guard','write','check','late','lazy','dev']:
 p=json.loads((r/'tests/fixtures/log1p-history/log1p.json').read_text());p['id']='trace-history-'+context;p['inputs']={'X':p['inputs']['X']};phase=p['phases'][0];phase['bindings']={'X':{'input':'X'}};phase['writes']={'A':'I'}
 if context=='guard':phase['guard']='select(trace(X)>0,-1,-2)'
 elif context=='write':phase['writes']={'A':'select(trace(X)>0,I,2*I)'}
 elif context=='check':phase['writes']={'A':'X'};phase['checks']=['select(trace(A)>0,1,2)>0']
 elif context=='lazy':phase['writes']={'A':'select(1>0,I,trace(X)*I)'}
 elif context=='dev':phase['writes']={'A':'select(norm(dev(X))>0,I,2*I)'}
 else:p['phases']=[{'name':'prepared','kind':'prepare','base':'parent','bindings':{},'writes':{'A':'I'}},{'name':'advanced','kind':'advance','base':'prepared','bindings':{'X':{'input':'X'}},'writes':{'A':'select(trace(X)>0,I,2*I)'}}]
 programs.append(p)
 for mode in ['good','bad','recover']:
  ok=mode!='bad'or context=='lazy';values=(good if context=='check'else[1.,1.,1.,0.,0.,0.])if ok else[.1,.2,.3,.4,.5,.6]
  history_expected.append({'id':p['id']+'/'+mode,'ok':ok,'values_bits':[bits(v)for v in values],'generation':8 if ok else 7,'epoch':4 if ok and context=='late'else 3,'events':([0,1]if context=='late'else[0])if ok else[],'failed':-1 if ok else(1 if context=='late'else 0),'parent_unchanged':True})
write(s/'history-programs.json',programs);write(s/'history-expected.json',history_expected);(s/'generated/history.hpp').write_text(history_generate(programs))
shutil.copyfile('/private/tmp/atlas-make-trace-context-study.py',s/'generate-study.py')
print('Models',len(models),'material observations',len(expected),'history observations',len(history_expected))
