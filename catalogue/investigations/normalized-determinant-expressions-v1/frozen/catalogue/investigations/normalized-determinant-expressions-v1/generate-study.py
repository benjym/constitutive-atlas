"""Generate synthetic v0.3 context fixtures and analytically specified expectations."""
import copy,json,struct,sys
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import formulation_inputs
from atlas.history_compiler import generate as history_header
HERE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
HERE.mkdir(parents=True,exist_ok=True)
def write(p,d):
 assert not p.exists(),p;p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def bits(v):return struct.pack('>d',float(v)).hex()
ZERO=bits(0.);ONE=bits(1.);SEVEN=bits(7.)
base=json.loads((ROOT/'models/barodesy-clay-2017.json').read_text())
base={k:copy.deepcopy(base[k])for k in ('schema_version','status','formulation','initialization')}
base.update(family='synthetic verification',description='Normalized determinant generated context fixture; not a constitutive literature model.',sources=[{'url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/NORMALIZED_DETERMINANT.md','role':'synthetic mathematical specification','locator':'Homogeneous normalized determinant context conformance'}],parameters={'K':{'default':1,'min':1,'max':1,'unit':'Pa'},'r':{'default':1,'min':0,'max':1e308,'unit':'1'}},state=[{'name':n,'shape':shape,'unit':unit,'scale':scale,'initial':([0.]*6 if shape=='sym'else 0.),'semantics':{'role':'persistent','quantity':quantity,'transformation':transform}}for n,shape,unit,scale,quantity,transform in [('sigma','sym','Pa','K','cauchy_stress','symmetric_spatial_tensor'),('A','sym','1','1','synthetic_dimensionless_tensor','symmetric_spatial_tensor'),('b','scalar','1','1','synthetic_probe','scalar_invariant')]],derived=[],domain=[],equations={'sigma':'0*K*I','A':'0*I','b':'0'})
base['initialization']['required_state']=['sigma','A','b']
variants={'direct':'normalized_determinant(A)','predicate':'select(normalized_determinant(A)>0,1,2)','eager':'0*normalized_determinant(A)+1','lazy-then':'select(1>0,1,normalized_determinant(A))','lazy-else':'select(1<0,normalized_determinant(A),1)','trace':'trace(sym(normalized_determinant(A),0,0,0,0,0))'}
contexts=['equation','derived','domain','initial','observable','reset-guard','reset-value','state-scale','observable-scale']
(HERE/'models').mkdir();(HERE/'generated').mkdir();paths=[];metadata=[]
for context in contexts:
 for variant,expr in variants.items():
  m=copy.deepcopy(base);m['id']='ndet-'+context+'-'+variant;m['name']=m['id']
  if context=='equation':m['equations']['b']=expr
  elif context=='derived':m['derived']=[{'name':'probe','expr':expr}];m['equations']['b']='probe'
  elif context=='domain':m['domain']=['select(('+expr+')>=0,1,1)>0']
  elif context=='initial':m['initial_checks']=['select(('+expr+')>=0,1,1)>0']
  elif context=='observable':m['observables']=[{'name':'probe','shape':'scalar','unit':'1','scale':'1','expr':expr}]
  elif context=='reset-guard':m['increment_reset']={'scope':'parent_increment','updates':[{'target':'b','guard':'-('+expr+')','value':'7'}]}
  elif context=='reset-value':m['increment_reset']={'scope':'parent_increment','updates':[{'target':'b','guard':'-1','value':expr}]}
  else:
   scale=expr.replace('A','sym(r,r,r,0,0,0)')
   if context=='state-scale':m['state'][2]['scale']=scale
   else:m['observables']=[{'name':'probe','shape':'scalar','unit':'1','expr':'b','scale':scale}]
  if context in ('observable','observable-scale'):
   m['formulation'].update(time_dependence='physical_time',equation_form='ode',stress={'source':'none'},inputs=formulation_inputs(physical=True))
   m['parameters']['tau']={'default':1,'min':1,'max':1,'unit':'s'}
   m['equations']={'sigma':'0*K*strain_rate','A':'0*strain_rate','b':'0/tau'}
  p=HERE/'models'/(m['id']+'.json');write(p,m);paths.append(p);metadata.append((m['id'],context,variant))
metadata.sort();indexes={name:i for i,(name,_,_)in enumerate(metadata)}
generate(HERE/'generated',paths)
refs=json.loads((ROOT/'docs/reviews/normalized-determinant-reference-v1/cases.json').read_text())['cases']
regular=next(c for c in refs if c['id']=='prior/regular/sphere')
# Context baseline uses identity with zero seeds: determinant1, all directional0.
values=['1','1','1','0','0','0'];seeds=[['0']*38 for _ in range(6)]
cases=[]
def expect(ok,scalar=0.,ds=None,count=13,history=False):
 d={'ok':ok,'input_unchanged':True,'output_count':count if ok or history else 0,'scalar_bits':bits(scalar)if ok or history else None,'derivative_bits':(ds or[ZERO]*38)if ok and not history else[],'all_outputs_finite':True if ok or history else None}
 if history:d.update(generation=8 if ok else 7,epoch=3,events=[0]if ok else[],failed=-1 if ok else 0)
 return d

def add(ident,model,A=values,S=seeds,*,param='1',initial=True,check=False,observe=False,expected,reference_id=None,recovery_of=None,after_rejection=None):
 idx=indexes[model];_,context,variant=metadata[idx]
 c={'id':ident,'model':idx,'model_id':model,'context':context,'variant':variant,'values':copy.deepcopy(A),'seeds':copy.deepcopy(S),'parameter':param,'initial':initial,'check_only':check,'observables_only':observe,'expectation':expected}
 if reference_id:c['reference_id']=reference_id
 if recovery_of:c.update(recovery_of=recovery_of,after_rejection=after_rejection)
 cases.append(c)

def baseline(model,ident,**kw):
 _,ctx,var=metadata[indexes[model]]
 scalar=7 if ctx=='reset-guard'else 0 if ctx in ('domain','initial')else float(F(1,27))if var in ('direct','trace')else 1
 count=1 if ctx in ('observable','observable-scale')else 13
 ds=[]if ctx in ('state-scale','observable-scale')else None
 e=expect(True,scalar,ds,count)
 if ctx in ('state-scale','observable-scale'):e['derivative_bits']=[]
 add(ident,model,observe=ctx=='observable',expected=e,**kw)
 return ident

# Every independent fixture through generated equation and outer trace composition.
for ctx in ['equation','derived','observable','reset-value']:
 for variant in ['direct','trace']:
  model='ndet-'+ctx+'-'+variant;control=baseline(model,model+'/baseline')
  for ref in refs:
   e=ref['expectation'];ds=[bits(float.fromhex(x))for x in e.get('derivatives_hex',[])]
   scalar=e.get('value')if e['ok']else 0.
   add(model+'/'+ref['id'],model,ref['values'],ref['seeds'],observe=ctx=='observable',expected=expect(e['ok'],scalar,ds,1 if ctx=='observable'else 13),reference_id=ref['id'])
   if not e['ok']:baseline(model,'recovery/'+model+'/'+ref['id'],recovery_of=control,after_rejection=model+'/'+ref['id'])
# All context/variant finite trace-zero failure, then same-instance baseline recovery.
for model,ctx,var in metadata:
 control=baseline(model,model+'/ordinary')
 lazy=var.startswith('lazy-')
 if ctx in ('state-scale','observable-scale'):
  e=expect(lazy,1.,count=1 if ctx=='observable-scale'else 13);e['derivative_bits']=[]
  add(model+'/trace-zero',model,param='0',expected=e)
 else:
  scalar=7 if ctx=='reset-guard'else 0 if ctx in ('domain','initial')else float(F(1,27))if var in ('direct','trace')else 1
  add(model+'/trace-zero',model,['1','-1','0','0','0','0'],observe=ctx=='observable',expected=expect(lazy,scalar,count=1 if ctx=='observable'else 13))
 baseline(model,model+'/recovery',**({'recovery_of':control,'after_rejection':model+'/trace-zero'}if not lazy else{}))
 if ctx=='initial':add(model+'/initial-disabled',model,['1','-1','0','0','0','0'],initial=False,expected=expect(True,0.))
 if ctx in ('equation','observable'):
  add(model+'/check-only-skips',model,['1','-1','0','0','0','0'],check=True,observe=ctx=='observable',expected={'ok':True,'input_unchanged':True,'output_count':0,'scalar_bits':None,'derivative_bits':[],'all_outputs_finite':True})
 if ctx=='observable':add(model+'/normal-skips',model,['1','-1','0','0','0','0'],expected=expect(True,0.))
 # Each non-lazy predicate context must reject a poison in every Jet column.
 if var=='predicate' and ctx not in ('state-scale','observable-scale'):
  for col in range(38):
   S=copy.deepcopy(seeds);S[4][col]='NaN';ident=model+'/poison-column-'+str(col)
   add(ident,model,S=S,observe=ctx=='observable',expected=expect(False))
   baseline(model,ident+'/recover',recovery_of=control,after_rejection=ident)
# Deliberate trace-first/determinant composition with cancellation references.
for variant,expr in [('trace-first','normalized_determinant(sym(trace(A),1,1,0,0,0))')]:
 m=copy.deepcopy(base);m['id']='ndet-'+variant;m['name']=m['id'];m['equations']['b']=expr
 p=HERE/'models'/(m['id']+'.json');write(p,m);paths.append(p)
 # Append ID after existing generated sorted IDs; use regenerate and remap below.
 metadata.append((m['id'],'equation',variant))
 # Inputs/seed contraction analytically preserve tiny middle term.
 A=['500','1e-130','-500','0','0','0'];S=copy.deepcopy(seeds)
 for col in range(38):S[0][col]='500';S[1][col]='-1e-130'if col%2 else'1e-130';S[2][col]='-500'
 indexes[m['id']]=len(metadata)-1
 add(m['id']+'/cancellation',m['id'],A,S,expected=expect(True,float(F(float('1e-130'))/(F(float('1e-130'))+2)**3),[bits(float((2-2*F(float('1e-130')))/(F(float('1e-130'))+2)**4*((-1 if col%2 else 1)*F(float('1e-130')))))for col in range(38)]))
# The generator sorts model paths; update all indices to its final order.
metadata.sort();indexes={name:i for i,(name,_,_)in enumerate(metadata)}
for c in cases:c['model']=indexes[c['model_id']]
generate(HERE/'generated',paths)
# Scalar-output histories exercise the same variants, trace-zero rollback and recovery.
programs=[];hc=[]
for var,expr in variants.items():
 p={'schema_version':'experimental-history-0.1','id':'ndet-history-'+var,'sources':[{'url':x['url'],'locator':x['locator']}for x in base['sources']],'fields':{'b':{'shape':'scalar','unit':'1','storage':'state'}},'inputs':{'X':{'shape':'sym','unit':'1'}},'phases':[{'name':'advanced','kind':'advance','base':'parent','bindings':{'A':{'input':'X'}},'writes':{'b':expr}}]}
 programs.append(p)
 for mode in ['good','bad','recover']:
  ok=mode!='bad'or var.startswith('lazy-');scalar=(float(F(1,27))if var in ('direct','trace')else 1.)if ok else 17.25
  hc.append({'id':p['id']+'/'+mode,'program':len(programs)-1,'values':values if mode!='bad'else['1','-1','0','0','0','0'],'expectation':expect(ok,scalar,history=True,count=1)})
write(HERE/'history-programs.json',programs);(HERE/'generated/history.hpp').write_text(history_header(programs))
write(HERE/'cases.json',cases);write(HERE/'history-cases.json',hc)
# C++ stores literal CSV inputs and ordinal requests. NaN poisons reach the actual
# generated expression path, rather than being converted to a parser rejection.
lines=['#pragma once','struct ContextCase {const char* id;int model;const char* context;const char* values;const char* seeds;double param;bool initial,check,observe;};','static const ContextCase context_cases[]={']
for c in cases:
 lines.append('{'+','.join([json.dumps(c['id']),str(c['model']),json.dumps(c['context']),json.dumps(','.join(c['values'])),json.dumps(','.join(v for row in c['seeds']for v in row)),c['parameter'],str(c['initial']).lower(),str(c['check_only']).lower(),str(c['observables_only']).lower()])+'},')
lines+=['};','struct HistoryCase {const char* id;int program;const char* values;};','static const HistoryCase history_cases[]={']
for c in hc:lines.append('{'+json.dumps(c['id'])+','+str(c['program'])+','+json.dumps(','.join(c['values']))+'},')
lines+=['};'];(HERE/'generated/cases.hpp').write_text('\n'.join(lines)+'\n')
write(HERE/'protocol.json',{'version':'normalized-determinant-generated-context-0.1','acceptance':'exact expected status/bits/all38scalar derivatives, complete input immutability, same-instance recovery, full native/Wasm decoded parity; failed model outputs are scratch','model_cases':len(cases),'history_cases':len(hc),'models':len(paths),'reference_cases':len(refs),'material_AD_columns':38,'scope':'generated synthetic v0.3 context conformance; no constitutive integration/admission'})
(HERE/'requests.tsv').write_text(''.join('M\t'+str(i)+'\n'for i in range(len(cases)))+''.join('H\t'+str(i)+'\n'for i in range(len(hc))))
print('generated',len(paths),'models',len(cases),'material cases',len(hc),'history cases')
