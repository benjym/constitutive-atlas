"""Independent saved-output audit; no Atlas/compiler/solver or integration imports."""
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];FROZEN=ROOT/'docs/reviews/gis2024-v03-research-freeze-v1';sys.path.insert(0,str(ROOT))
from tools.reference_gis2024_coupled import coupled_rates

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def vector(x,n):return type(x)is list and len(x)==n and all(type(v)in(int,float)and math.isfinite(v)for v in x)
def csv(v):return ','.join(format(x,'.17g')for x in v)
def request(row,state,strain):return {'model':row['model'],'parameters':row['parameters'],'settings':row['settings'],'initial':state[:],'strain':strain[:]}
def audit(data,directory,model,rows,probes,policy,reference,catalogue=None):
 require(data.get('transport_error')is None,'transport error');require(data['backend']in ['native','wasm'],'backend identity')
 catalogue=[model] if catalogue is None else catalogue
 require(sum(m['id']==model['id'] for m in catalogue)==1 and model in catalogue,'candidate membership')
 cat=digest(catalogue);receipts={};used=[];contexts={}
 for file in sorted((directory/'receipts').glob('*.json')):
  r=load(file);require(type(r['index'])is int and r['index']not in receipts,'receipt index');receipts[r['index']]=r
 def raw(index,line,answer,context):
  require(index in receipts and index not in used,'missing/reused receipt');used.append(index);r=receipts[index]
  require(r['line']==line and json.loads(r['stdout'])==answer,'raw receipt binding');require(r['context']==context,'receipt context')
  require(type(r['pid'])is int and r['pid']>0,'process identity')
  if context in contexts:require(contexts[context]==r['pid'],'context process changed')
  else:contexts[context]=r['pid']
 def descriptor(d):
  require(d['descriptor']['models']==catalogue and d['descriptor']['sha256']==cat,'runtime catalogue identity')
  raw(d['receipt'],'D',d['descriptor'],d['context'])
 require(len(data['descriptors'])==21,'descriptor coverage')
 for d in data['descriptors']:descriptor(d)
 require({d['context']for d in data['descriptors']}=={'main'}|{'fresh:'+r['id']for r in rows},'context coverage')
 require(all(pid!=contexts['main']for name,pid in contexts.items()if name!='main'),'fresh process identity')
 def call(item,expected,context,success=True,rollback=False,late=False,malformed=False):
  require(item['request']==expected and item['context']==context,'request chain/context')
  a=item['response'];line='\t'.join(['I',expected['model'],csv(expected['parameters']),csv(expected['initial']),csv(expected['strain']),csv(expected['settings'])]);raw(item['receipt'],line,a,context)
  require(a.get('ok')is success,'unexpected outcome')
  if malformed:return a
  require(a.get('catalogue_hash')==cat,'catalogue echo')
  for name,n in [('model',None),('parameters',len(model['parameters'])),('initial',14),('strain',6)]:
   require(a.get(name)==expected[name],'request echo '+name)
   if n:require(vector(a[name],n),'finite echo '+name)
  settings={'version':'incremental-settings-0.1','norm':'scaled_component_max',**dict(zip(['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'],expected['settings']))}
  require(a.get('integration_settings')==settings,'settings echo');require(vector(a.get('state'),14),'state layout/finite')
  diag=a.get('diagnostics',{});require(all(type(diag.get(k))is int and diag[k]>=0 for k in ['substeps','rejected','iterations']),'diagnostic counters')
  if rollback:require(a['state']==expected['initial'],'full-state rollback')
  if late:require(diag['substeps']>0,'late failure has no accepted work')
  if success:
   fs=diag.get('increment_fractions');require(type(fs)is list and len(fs)==diag['substeps']and len(fs)>0 and all(type(x)in(int,float)and math.isfinite(x)and 0<x<=1 for x in fs)and abs(math.fsum(fs)-1)<=1e-12,'increment coverage')
   params=dict(zip(model['parameters'],expected['parameters']));z=a['state']
   coupled_rates({'sigma':z[:6],'e':z[6],'h':z[7:13],'Omega':z[13]},[0.]*6,{k:v for k,v in params.items()if k!='p_scale'})
  return a
 ref={c['input']['id']:c for c in reference['cases']}
 for case in ref.values():
  for name,budget in policy['reference_budget'].items():require(0<=case['fine_difference'][name]<=budget/4,'reference adequacy')
 require(len(data['rows'])==len(rows)==20,'trajectory coverage');seen={};summaries=[];worst_volume=0.
 channels=[('stress',0,6),('e',6,7),('h',7,13),('Omega',13,14)]
 def errors(a,b):return {k:max(abs(x-y)for x,y in zip(a[lo:hi],b[lo:hi]))for k,lo,hi in channels}
 for group,row in zip(data['rows'],rows):
  require(group['id']==row['id']and group['id']not in seen,'trajectory order/identity');seen[group['id']]=group
  require(len(group['calls'])==len(row['increments']),'caller coverage');state=row['initial'][:];cumulative=0.;endpoint=[];indices=[];bound=policy['endpoint_normalized_bounds'][str(row['tolerance'])];params=dict(zip(model['parameters'],row['parameters']));scales={'stress':params['p_scale'],'e':1.,'h':params['R'],'Omega':1.}
  for j,(item,strain)in enumerate(zip(group['calls'],row['increments']),1):
   a=call(item,request(row,state,strain),'main');indices.append(item['receipt']);state=a['state'][:];cumulative+=math.fsum(strain[:3]);v=abs(state[6]-((1+row['initial'][6])*math.exp(-cumulative)-1));worst_volume=max(worst_volume,v);require(v<=max(1e-10,bound*.01),'volume closure')
   if j in row['original_endpoint_indices']:
    segment=row['original_endpoint_indices'].index(j)+1;target=ref[row['case']]['grids'][-1]['trajectory'][segment]['state'];err=errors(state,target)
    require(all(err[k]<=scales[k]*bound+policy['reference_budget'][k]for k in err),'endpoint accuracy');endpoint.append(err)
  require(indices==sorted(indices),'call ordering')
  suffix=group['calls'][row['partitions']:];checkpoint=group['calls'][row['partitions']-1]['response']['state'][:]
  for name,context in [('restart_same','main'),('restart_fresh','fresh:'+row['id'])]:
   require(len(group[name])==len(suffix),'restart coverage');state=checkpoint[:];restart_indices=[]
   for item,original,strain in zip(group[name],suffix,row['increments'][row['partitions']:]):
    a=call(item,request(row,state,strain),context);require(a['state']==original['response']['state'],'own-state restart equality');state=a['state'][:];restart_indices.append(item['receipt'])
   require(restart_indices==sorted(restart_indices)and min(restart_indices)>max(indices),'restart ordering')
  summaries.append({'id':row['id'],'case':row['case'],'tolerance':row['tolerance'],'partitions':row['partitions'],'maximum':{k:max(e[k]for e in endpoint)for k in scales}})
 for case in ref:
  selected=[next(s for s in summaries if(s['case'],s['tolerance'],s['partitions'])==(case,t,1))for t in [1e-4,1e-6,1e-8]]
  for name in ['stress','h','Omega']:
   a,b,c=[s['maximum'][name]for s in selected];floor=2*policy['reference_budget'][name];require(b<=.65*a+floor and c<=.35*a+floor and c<=.65*b+floor,'temporal refinement')
  partitions=[]
  for t in [1e-4,1e-8]:
   a=next(g for g,r in zip(data['rows'],rows)if(r['case'],r['tolerance'],r['partitions'])==(case,t,1));b=next(g for g,r in zip(data['rows'],rows)if(r['case'],r['tolerance'],r['partitions'])==(case,t,7));errs=[errors(a['calls'][i]['response']['state'],b['calls'][(i+1)*7-1]['response']['state'])for i in range(3)];partitions.append({k:max(e[k]for e in errs)for k in ['stress','h','Omega']})
  require(all(partitions[1][k]<=.35*partitions[0][k]+2*policy['reference_budget'][k]for k in partitions[0]),'caller partition refinement')
 good=call(data['control'],probes['control'],'main');require(len(data['probes'])==9,'probe coverage')
 previous=data['control']['receipt']
 for observed,p in zip(data['probes'],probes['probes']):
  require(observed['id']==p['id'],'probe identity');zero=p['id']=='zero-increment';malformed=p['id'].startswith('incomplete-');a=call(observed['call'],p['request'],'main',success=zero,rollback=not malformed,late=p['id']=='late-budget',malformed=malformed)
  if zero:require(a['state']==p['request']['initial'],'zero identity')
  recovery=call(observed['recovery'],probes['control'],'main');require(recovery['state']==good['state'],'persistent recovery')
  require(previous<observed['call']['receipt']<observed['recovery']['receipt'],'probe/recovery ordering');previous=observed['recovery']['receipt']
 require(set(used)==set(receipts)==set(range(len(receipts))),'raw receipt completeness')
 return {'backend_qualification_pass':True,'backend':data['backend'],'trajectories':20,'base_updates':204,'same_and_fresh_restart_updates':272,'probes':9,'persistent_recoveries':9,'raw_receipts':len(receipts),'maximum_volume_error':worst_volume,'rows':summaries,'scientific_admission':False}
def assess(directory):
 return audit(load(directory/'result.json'),directory,load(FROZEN/'model.json'),load(FROZEN/'trajectory-requests.json.gz'),load(FROZEN/'probes.json'),load(FROZEN/'policy.json'),load(ROOT/load(FROZEN/'policy.json')['reference']))
