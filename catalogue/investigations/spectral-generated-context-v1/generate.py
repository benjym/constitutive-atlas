from pathlib import Path
import json,gzip,sys,copy,hashlib,shutil
R=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/Users/bmar5496/code/constitutive-atlas');P=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path('/private/tmp/atlas-spectral-generated-context-v1');P.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R))
from atlas.dsl import cpp,parse,infer,Type,PRESSURE
from atlas.model import load,migrate_formulation,validate
from atlas.compiler import generate
from atlas.history import validate_program
from atlas.history_compiler import generate as history_header
from atlas.symmetric_spectral import SPECTRAL_FUNCTIONS
from atlas.evidence_sources import selected_files
j=lambda x:json.dumps(x,indent=2)+'\n'
def save(name,x):p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(j(x))
refroot=R/'catalogue/investigations/symmetric-spectral-primitive-v1'
reference=json.loads(gzip.decompress((refroot/'reference/reference-p360.json.gz').read_bytes()));original=json.loads(gzip.decompress((refroot/'requests.json.gz').read_bytes()));bycase={c['input']['id']:c for c in reference['cases']};seeds=reference['seeds_mandel_hex']
# Explicit complete Python/schema/model/fixture closure; caches and hidden paths excluded.
for folder,suffixes in [('atlas',{'.py'}),('schemas',{'.json'}),('cpp/include',{'.hpp'}),('models',{'.json'}),('initialization',{'.json'}),('fixtures',{'.json'}),('tests/fixtures',{'.json'})]:
 for src in selected_files(R/folder,suffixes):
  dest=P/'frozen'/src.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
for rel in ['reference/reference-p360.json.gz','requests.json.gz','policy.json','study.py']:
 dest=P/'reference'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(refroot/rel,dest)
for rel in ['catalogue/investigations/symmetric-spectral-primitive-v1/reference/reference-p360.json.gz','catalogue/investigations/symmetric-spectral-primitive-v1/requests.json.gz','catalogue/investigations/symmetric-spectral-primitive-v1/policy.json','catalogue/investigations/symmetric-spectral-primitive-v1/study.py','docs/reviews/spectral-generated-context-design-v1/cases.json']:
 dest=P/'frozen'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,dest)
base=migrate_formulation(load(R/'models/linear-elastic.json'));base['family']='synthetic arithmetic verification';base['description']='Generated spectral integration fixture, not a constitutive model or calibrated material.';base['parameters']={'p_ref':{'default':1.,'min':1.,'max':1e9,'unit':'Pa'}};base['derived']=[];base['domain']=[];base.pop('initial_checks',None);base['state'][0]['initial']=[7.,2.,-3.,0.,0.,0.];base['equations']={'sigma':'0*sigma','e':'0*e'};base['sources']=[{'url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/SYMMETRIC_SPECTRAL.md','locator':'Synthetic integration verification; no material/source equation claim','role':'test specification'}]
physical=migrate_formulation(load(R/'tests/fixtures/time/clock.json'))
def as_physical(m):
 m=copy.deepcopy(m);m['formulation']=copy.deepcopy(physical['formulation']);m['parameters']['tau']={'default':1.,'min':1.,'max':100.,'unit':'s'};m['equations']={f['name']:'0*'+f['name']+'/tau'for f in m['state']};return m
if (P/'models').exists():shutil.rmtree(P/'models')
fixtures={};slots=[]
def fixture(name):m=copy.deepcopy(base);m['id']='synthetic-spectral-'+name.replace('_','-');m['name']='Synthetic spectral '+name;return m
def add(name,m):validate(m);fixtures[name]=m;save('models/'+name+'.json',m)
def slot(mode,**kw):slots.append({'mode':mode,**kw});return len(slots)-1
exprslots={}
for name,(op,shape,vo) in SPECTRAL_FUNCTIONS.items():
 tree=parse(name+'(A)');t=infer(tree,{'A':Type('sym',PRESSURE)});assert t.shape==shape and t.value_only==vo
 exprslots[op]=slot('expression',operation=op,shape=shape,expression=name+'(A)',emitted=cpp(tree),value_only_adapter=vo)
modelslots={}
for name,(op,shape,vo) in SPECTRAL_FUNCTIONS.items():
 if vo:continue
 m=fixture(op)
 if shape=='scalar':
  q=copy.deepcopy(m['state'][1]);q.update(name='q',unit='Pa',scale='p_ref',initial=0.);q['semantics']['quantity']='synthetic scalar output';m['state'].append(q);m['initialization']['required_state'].append('q');m['equations']['q']='q-'+name+'(sigma)'
 if shape=='scalar':
  add(op,m);modelslots[('equation',op)]=slot('equation',model=op,shape=shape,offset=7,negate=True)
 obs=as_physical(m);obs['id']+='-observable';obs['observables']=[{'name':'probe','shape':shape,'unit':'1'if shape=='sym'else'Pa','scale':'1'if shape=='sym'else'p_ref','expr':name+'(sigma)'}]
 add(op+'-observable',obs);modelslots[('observable',op)]=slot('observable',model=op+'-observable',shape=shape)
controls={}
for name in ('lazy','sticky','eager-mask','eager-derived','domain-ordinary','domain-value','initial','check-only','reset','scales','solver'):
 m=fixture(name)
 if name=='lazy':
  m['parameters']['threshold']={'default':4.,'min':-10.,'max':10.,'unit':'Pa'};m['equations']['sigma']='p_ref*select(principal_max_value(sigma)>threshold,projector_max(sigma),I)'
 elif name=='sticky':m['equations']['sigma']='p_ref*select(principal_max(sigma)>=0*p_ref,I,I)+0*p_ref*projector_min(sym(3,2,1,0,0,0))'
 elif name=='eager-mask':m['equations']['sigma']='0*principal_max(sigma)*I'
 elif name=='eager-derived':m['derived']=[{'name':'eager','expr':'projector_max(sigma)'}];m['equations']['sigma']='select(1>0,sigma,p_ref*eager)'
 elif name in ('domain-ordinary','domain-value'):
  func='principal_max'if name=='domain-ordinary'else'principal_max_value';m['domain']=[func+'(sigma)>=0*p_ref']
 elif name=='initial':m['initial_checks']=['principal_max(sigma)>=0*p_ref']
 elif name=='check-only':m['equations']['sigma']='principal_max(sigma)*I'
 elif name=='reset':m['increment_reset']={'scope':'parent_increment','updates':[{'target':'sigma','guard':'-threshold','value':'p_ref*projector_max(sigma)'}]};m['parameters']['threshold']={'default':1.,'min':-1.,'max':1.,'unit':'1'}
 elif name=='scales':
  m=as_physical(m)
  m['parameters']['shape']={'default':2.,'min':1.,'max':3.,'unit':'1'};m['state'][0]['scale']='principal_max(sym(p_ref,shape*p_ref,3*p_ref,0*p_ref,0*p_ref,0*p_ref))';m['observables']=[{'name':'probe','shape':'scalar','unit':'1','scale':'principal_max(sym(1,shape,3,0,0,0))','expr':'e'}]
 elif name=='solver':
  aux=copy.deepcopy(m['state'][1]);aux.update(name='memory',initial=0.);aux['semantics']['quantity']='synthetic reset memory';m['state'].append(aux);m['initialization']['required_state'].append('memory');m['increment_reset']={'scope':'parent_increment','updates':[{'target':'memory','guard':'-1','value':'1'}]};m['derived']=[{'name':'trialA','expr':'sigma_n+p_ref*de'}];m['equations']={'sigma':'sigma-sigma_n+0*p_ref*projector_max(trialA)','e':'e-e_n','memory':'memory-memory_n'}
 add(name,m);controls[name]=slot('control',model=name,shape='sym')
paths=sorted((P/'models').glob('*.json'));generate(P/'generated',paths);indices={p.stem:i for i,p in enumerate(paths)}
for row in slots:
 if 'model'in row:row['model_index']=indices[row['model']]
# Real generated history: first tentative write must disappear if second phase fails.
h={'schema_version':'experimental-history-0.1','id':'synthetic-spectral-history','sources':[{'url':'https://github.com/benjym/constitutive-atlas/blob/main/docs/SYMMETRIC_SPECTRAL.md','locator':'Synthetic two-phase history rollback fixture'}],'fields':{'count':{'shape':'scalar','unit':'1','storage':'state'},'tensor':{'shape':'sym','unit':'1','storage':'state'}},'inputs':{'A':{'shape':'sym','unit':'1'}},'phases':[{'name':'tentative','kind':'advance','base':'parent','bindings':{'oldcount':{'snapshot':'parent','field':'count'}},'writes':{'count':'oldcount+1'}},{'name':'project','kind':'advance','base':'tentative','bindings':{'A':{'input':'A'}},'writes':{'tensor':'projector_max(A)'}}]}
validate_program(h);save('history.json',h);(P/'generated/history.hpp').write_text(history_header([h]));hslot=slot('history',shape='sym')
requests=[]
def request(identifier,which,case='hydro',kind='jet',expectation='constant',ok=True,**kw):
 row={'id':identifier,'slot':which,'kind':kind,'case':case,'values':bycase[case]['input']['mandel_hex'],'seeds':seeds,'expected_ok':ok,'expectation':expectation,'threshold':4.,'initial':False,'check_only':False,'reset':False,'scale':False,'observe_scale':False,'solver_fail':False,**kw};requests.append(row);return row
# Full existing request table for actual emitted AST adapters, including invalid/recovery calls.
for old in original:
 row=request('expr/'+old['id'],exprslots[old['operation']],old.get('case','distinct'),old['kind'],'spectral',old['expected_status']=='ok',operation=old['operation']);row['values']=old['values'];row['seeds']=old['seeds'];row['primitive_expected_status']=old['expected_status']
subset=set(json.loads((R/'docs/reviews/spectral-generated-context-design-v1/cases.json').read_text())['case_ids'])
for old in original:
 if old.get('case')not in subset or old['operation'].endswith('_value')or old['id'].startswith('nonfinite'):continue
 for mode in ('equation','observable'):
  if(mode,old['operation'])not in modelslots:continue
  request(mode+'/'+old['id'],modelslots[(mode,old['operation'])],old['case'],old['kind'],'spectral',old['expected_status']=='ok',operation=old['operation'])
for kind in ('double','jet'):
 request('lazy/unselected/'+kind,controls['lazy'],kind=kind,constant=[1,1,1,0,0,0])
 request('lazy/selected/'+kind,controls['lazy'],kind=kind,ok=False,threshold=2.)
 request('lazy/complement/'+kind,controls['lazy'],'lower-repeat',kind,'spectral',True,operation='projector_max',threshold=2.)
 for mode in ('sticky','eager-mask','eager-derived','domain-ordinary'):request(mode+'/'+kind,controls[mode],kind=kind,ok=False)
 request('domain-value/'+kind,controls['domain-value'],kind=kind,constant=[0]*6)
 request('initial/off/'+kind,controls['initial'],kind=kind,constant=[0]*6)
 request('initial/on/'+kind,controls['initial'],kind=kind,ok=False,initial=True)
 request('check-only/skip/'+kind,controls['check-only'],kind=kind,expectation='none',check_only=True)
 request('check-only/equation/'+kind,controls['check-only'],kind=kind,ok=False)
 request('reset/inactive/'+kind,controls['reset'],kind=kind,expectation='identity',reset=True,threshold=-1.)
 request('reset/selected/'+kind,controls['reset'],kind=kind,ok=False,reset=True,threshold=1.)
 request('reset/valid/'+kind,controls['reset'],'distinct',kind,'spectral',operation='projector_max',reset=True,threshold=1.)
for observe in (False,True):
 for parameter,ok in ((2.,True),(3.,False),(2.,True)):
  count=sum(x['slot']==controls['scales']for x in requests)
  request('scale/'+str(observe)+'/'+str(count),controls['scales'],kind='double',ok=ok,scale=True,observe_scale=observe,threshold=parameter,constant=[3.]if observe else[3.]*6+[1.])
# All38 generated Jet columns: invalid executed operand, followed by independent valid recovery.
for col in range(38):
 a=request('model-nonfinite/'+str(col),modelslots[('observable','projector_max')],'distinct','jet','spectral',False,operation='projector_max');a['seeds']=copy.deepcopy(seeds);a['seeds'][col][col%6]='nan'if col%2 else'inf'
 request('model-recovery/'+str(col),modelslots[('observable','projector_max')],'distinct','jet','spectral',True,operation='projector_max')
for case in ('distinct','hydro','distinct'):
 count=sum(x['slot']==hslot for x in requests)
 request('history/'+str(count),hslot,case,'double','spectral',case!='hydro',operation='projector_max',history=True)
for fail in (True,False):request('solver/'+str(fail),controls['solver'],'distinct','double','constant',not fail,solver=True,solver_fail=fail,constant=[7.,2.,-3.,0.,0.,0.,.7,0. if fail else 1.])
save('slots.json',slots);(P/'requests.json.gz').write_bytes(gzip.compress(j(requests).encode(),mtime=0));save('policy.json',{'identity':'spectral-generated-context-v1','compiled_observations_before_freeze':0,'scope':'Full emitted expression table plus actual generated model/history/solver contexts; synthetic arithmetic, no constitutive admission','spectral_bounds':'Exact unchanged primitive policy copied at reference/policy.json','columns':38,'scratch_output':'May mutate on false; caller must discard. Inputs and accepted solver/history state are immutable on failure.','solver':{'max_depth':0,'max_iterations':45,'max_substeps':20000,'residual_tolerance':2e-10,'rate_tolerance':1e-6,'max_backtracks':11},'reference_primitive_requests':len(original),'requests':len(requests)})
# Templated functions contain only production-emitted expression text or real generated dispatch.
lines=['#pragma once','#include "models.hpp"','#include "history.hpp"','#include "atlas/solver.hpp"','namespace context_study {','using namespace atlas;','template<class T> bool call(int slot,const Sym<T>& A,double threshold,bool initial,bool check_only,bool reset,bool scale,bool observe_scale,std::vector<T>&out){','bool atlas_eval_ok=true; const auto I=identity<T>(); switch(slot){']
for i,row in enumerate(slots):
 if row['mode']=='history':continue
 lines.append(f'case {i}: {{')
 if row['mode']=='expression':lines+=['auto result='+row['emitted']+';','out.assign(result.v.begin(),result.v.end());'if row['shape']=='sym'else'out={result};','return atlas_eval_ok;']
 else:
  index=row['model_index'];m=fixtures[row['model']];n=sum(6 if f['shape']=='sym'else 1 for f in m['state']);lines +=[f'std::vector<T> z({n}); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);','std::vector<double> p; for(const auto&param:models()['+str(index)+'].parameters) p.push_back(param.value);']
  if row['model']in('lazy','reset','scales'):lines +=['for(size_t j=0;j<p.size();++j)if(models()['+str(index)+'].parameters[j].name=="threshold"||models()['+str(index)+'].parameters[j].name=="shape")p[j]=threshold;']
  if row['mode']=='control':
   lines+=['if(scale){const auto values=observe_scale?model_observable_scales('+str(index)+',p):model_scales('+str(index)+',p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}',f'if(reset){{std::vector<T> tmp;bool ok=prepare_model_increment({index},z,Sym<T>{{}},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}}',f'std::vector<T> tmp;bool ok=evaluate_model({index},z,z,Sym<T>{{}},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;']
  else:
   observe=row['mode']=='observable';lines +=[f'std::vector<T> tmp;bool ok=evaluate_model({index},z,z,Sym<T>{{}},p,tmp,false,0.,false,{str(observe).lower()});if(ok){{']
   if observe:lines+=['out=tmp;']
   else:lines+=['out={-tmp[7]};']
   lines+=['}return ok;']
 lines.append('}')
lines+=['default:return false;}}','}'];(P/'generated/contexts.hpp').write_text('\n'.join(lines)+'\n')
save('wire.json',{'fields':['id','slot','kind','threshold','initial','check_only','reset','scale','observe_scale','solver_fail','six values','38x6 seeds'],'history_slot':hslot,'solver_slot':controls['solver'],'solver_model':indices['solver']})
print(json.dumps({'models':len(fixtures),'slots':len(slots),'requests':len(requests),'frozen_files':len(list((P/'frozen').rglob('*'))),'compiled_observations':0}))
