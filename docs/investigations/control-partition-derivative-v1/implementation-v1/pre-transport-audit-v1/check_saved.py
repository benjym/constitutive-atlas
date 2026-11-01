"""Check saved standalone capability evidence; no backend execution/import."""
from pathlib import Path
import argparse,hashlib,json,math
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('reports',nargs='+');p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output);assert not out.exists(),'preserve prior evidence';policy=json.loads((D/'cases.json').read_text());checks=[];parsed=[]
 def add(name,passed):checks.append({'name':name,'passed':bool(passed)})
 def finite(z,size):return isinstance(z,list) and len(z)==size and all(type(x)in(int,float) and math.isfinite(x)for x in z)
 def state(name,z,w):
  valid=finite(z,7) and finite(w,7);add(name+'/shape',valid)
  if valid:add(name+'/value',all(abs(x-y)<=(1e-6 if i<6 else 1e-12)for i,(x,y)in enumerate(zip(z,w))))
 for file in a.reports:
  report=json.loads(Path(file).read_text());identity=report.get('identity',{});backend=identity.get('backend',file);prefix=str(backend);calls=report.get('calls',[])
  for key,n in [('manifest_sha256','manifest.json'),('source_freeze_sha256','source-freeze.json'),('cases_sha256','cases.json')]:add(prefix+'/identity/'+key,identity.get(key)==sha(D/n))
  add(prefix+'/identity/artifact',isinstance(identity.get('artifact_sha256'),str) and len(identity['artifact_sha256'])==64)
  add(prefix+'/backend-label',backend in ['native','wasm'])
  artifact=Path(identity.get('artifact_path',''))
  add(prefix+'/artifact-exact-bytes',artifact.is_file() and sha(artifact)==identity.get('artifact_sha256'))
  if backend=='wasm':
   payload=Path(identity.get('wasm_path',''));add(prefix+'/wasm-payload-exact-bytes',payload.is_file() and sha(payload)==identity.get('wasm_sha256'))
  add(prefix+'/repeat-count',len(calls)==2)
  if len(calls)!=2:continue
  add(prefix+'/repeat-bytes',calls[0].get('stdout')==calls[1].get('stdout'))
  for repeat,call in enumerate(calls):
   q=prefix+'/'+str(repeat);add(q+'/returncode',call.get('returncode')==0)
   try:r=json.loads(call.get('stdout',''),parse_constant=lambda v:(_ for _ in()).throw(ValueError(v)))
   except Exception:add(q+'/valid-json',False);continue
   add(q+'/raw-json-equals-saved-response',r==call.get('response'))
   add(q+'/fixture-identity',r.get('identity')==policy['identity'].replace('cases','fixture'))
   add(q+'/aggregate-verdict',r.get('passed') is True)
   rows=r.get('cases',[]);by={x.get('id'):x for x in rows};add(q+'/exact-case-coverage',len(rows)==len(by)==25 and [x.get('id')for x in rows]==[x['id']for x in policy['cases']])
   if repeat==0:parsed.append((backend,r))
   for c in policy['cases']:
    x=by.get(c['id'],{});name=q+'/'+c['id'];add(name+'/verdict',x.get('passed') is True)
    if c['kind']=='helper':
     for key in ['ok','evaluator_calls','selected_h']:add(name+'/'+key,x.get(key)==c[key])
     probes=x.get('probes',[]);add(name+'/probe-record-count',len(probes)==c['probe_records'])
     add(name+'/full-base-state',finite(x.get('base',{}).get('state'),7))
     add(name+'/full-parent',x.get('parent')==c['parent'])
     add(name+'/full-input',x.get('total')==c['total'] and x.get('direction')==c['direction'] and x.get('initial_h')==c['initial_h'])
     for k,v in enumerate(probes):
      add(name+'/h-'+str(k),v.get('h')==math.ldexp(c['initial_h'],-k))
      add(name+'/actual-total-'+str(k),finite(v.get('increment'),6) and v.get('increment')==[u+math.ldexp(c['initial_h'],-k)*d for u,d in zip(c['total'],c['direction'])])
      if v.get('representable'):
       z=v.get('advance',{}).get('state');exception=c['id']=='nonfinite-probe-reset' and k in [1,2,3]
       valid=finite(z,7)
       if exception:valid=isinstance(z,list) and (len(z)==7 and z[1] is None if k==1 else len(z)==1 if k==2 else z==[])
       add(name+'/probe-state-finiteness-'+str(k),valid)
      if v.get('representable'):add(name+'/probe-response-'+str(k),isinstance(v.get('advance',{}).get('ok'),bool) and isinstance(v.get('advance',{}).get('state'),list))
     if c['ok']:
      add(name+'/slope',type(x.get('value'))in(int,float) and math.isfinite(x['value']) and abs(x['value']-c['value'])<=c['value_atol'])
      pair=probes[-2:];valid=len(pair)==2 and all(v.get('comparable') is True and v.get('finite_slope') is True and v.get('advance',{}).get('ok') is True for v in pair);add(name+'/accepted-consecutive-comparable-pair',valid)
      if valid:
       u,v=pair;add(name+'/converged-pair',u['h']==2*v['h'] and abs(u['slope']-v['slope'])<=1e-3*max(abs(u['slope']),abs(v['slope']),1) and x['value']==v['slope'])
     if c['id'] in ['jump-recovery','protocol3-direction']:add(name+'/unmatched-probe-not-used',bool(probes) and probes[0].get('comparable') is False and probes[0].get('finite_slope') is False)
     if c['id'] in ['failed-probe-reset','nonfinite-probe-reset','overflow-slope-reset']:add(name+'/invalid-second-clears-candidate',len(probes)==c['probe_records'] and not(probes[1].get('comparable') and probes[1].get('finite_slope')) and probes[-1]['h']==c['selected_h'])
     if c['id']=='nonfinite-probe-reset':add(name+'/all-malformed-cleared',len(probes)==6 and all(probes[k].get('finite_slope') is False for k in [1,2,3]))
     if c['id']=='unrepresentable':add(name+'/no-evaluator-call',len(probes)==1 and probes[0].get('representable') is False);add(name+'/empty-base-fail-before-observer',x.get('empty_base')==c['empty_base'])
     if c['id']=='recovery-after-exhaustion':add(name+'/prior-exhaustion',x.get('unavailable_calls')==11)
    elif c['kind']=='partition':
     add(name+'/base-and-probe-receipt',all(isinstance(x.get(k),dict) for k in ['base','probe']) and x.get('base_total')==c['base_total'] and x.get('probe_total')==c['probe_total'])
    elif c['kind']=='elastic':
     for key in ['parameters','settings','protocol','axial','reference','current_axial']:add(name+'/input-'+key,x.get(key)==c[key])
     z=x.get('advance',{});add(name+'/success',z.get('ok') is True);state(name,z.get('state'),c['state']);de=x.get('increment');add(name+'/control',finite(de,6) and de[0]==.001 and abs(de[1]-c['lateral'])<=c['lateral_atol'] and abs(de[2]-c['lateral'])<=c['lateral_atol']);state(name+'/parent',x.get('parent'),[100000.]*3+[0.]*3+[.7])
     for label in ['affine_base','affine_probe']:
      adv=x.get(label,{});diag=adv.get('diagnostics',{});f=diag.get('increment_fractions',[]);inc=diag.get('accepted_increments',[]);expected=2 if c['id']=='analytic-rate-control' else 1
      add(name+'/'+label+'/actual-partition',adv.get('ok') is True and len(f)==len(inc)==expected and all(finite(v,6)for v in inc) and all(type(v)in(int,float) and v>0 and math.isfinite(v)for v in f) and abs(sum(f)-1)<=1e-12)
    elif c['kind']=='recovery':
     for key in ['parameters','settings','protocol','axial','reference','current_axial']:add(name+'/input-'+key,x.get(key)==c[key])
     add(name+'/initial-input',x.get('initial')==c['initial'])
     bad=x.get('failure',{});good=x.get('recovery',{});add(name+'/rejected',bad.get('ok') is False);add(name+'/full-parent-rollback',bad.get('state')==x.get('invalid_parent') and finite(bad.get('state'),7));add(name+'/recovery-success',good.get('ok') is True);state(name+'/recovery',good.get('state'),[130000.,100000.,100000.,0.,0.,0.,.69915])
 add('report-count',len(a.reports) in [1,2])
 if len(a.reports)==2:
  add('parity/backends',{x[0]for x in parsed}=={'native','wasm'} and len(parsed)==2)
  if len(parsed)==2:
   def compare(x,y,path=''):
    if isinstance(x,dict)and isinstance(y,dict):
     add('parity'+path+'/keys',x.keys()==y.keys())
     for k in x.keys()&y.keys():compare(x[k],y[k],path+'/'+k)
    elif isinstance(x,list)and isinstance(y,list):
     add('parity'+path+'/length',len(x)==len(y))
     for i,(u,v)in enumerate(zip(x,y)):compare(u,v,path+'/'+str(i))
    elif type(x)in(int,float)and type(y)in(int,float):
     exact=any(k in path.split('/')for k in ['h','initial_h','selected_h','increment','base_total','probe_total','direction','increment_fractions','accepted_increments','evaluator_calls','substeps','partition_retries','partition_defect','discarded_increment_fractions','discarded_increments','settings','parameters'])
     tol=0 if exact else 1e-12 if '/state/6' in path or '/parent/6' in path or path.endswith('/error') else 1e-6
     add('parity'+path,math.isfinite(x)and math.isfinite(y)and abs(x-y)<=tol)
    else:add('parity'+path,x==y)
   compare(parsed[0][1],parsed[1][1])
 result={'identity':'control-partition-saved-checks-v1','passed':all(x['passed']for x in checks),'failures':sum(not x['passed']for x in checks),'reports':{str(Path(f).resolve()):sha(f)for f in a.reports},'checks':checks};out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'failures':result['failures']}));raise SystemExit(0 if result['passed']else 1)
if __name__=='__main__':main()
