import importlib.util,json,math,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;R=Path('/private/tmp/atlas-control-partition-v1/md-native-v5');load=lambda p:json.loads(p.read_text());r=load(R/'report.json');plan=load(P/'resolution-study-v4/requests.json');source=load(D/'rechecked-source.json');checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
spec=importlib.util.spec_from_file_location('saved_native_branch',P/'resolution-study-v4/check_parity.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for c in plan['cases']:
 pts=r['cases'][c['id']]['points'];grid=c['coordinates']if c['kind']=='chain'else c['controls']if c['kind']=='controls'else[c['target']*i/c['steps']for i in range(c['steps']+1)]
 check(c['id']+'/entire expected grid',len(pts)==len(grid) and all((p['coordinate']==v if c['kind']!='run'else abs(p['coordinate']-v)<=1e-15)for p,v in zip(pts,grid)))
 if c['group']=='restart':
  rec=r['cases'][c['id']]['restart_receipt'];i=c['restart_index']-1;z=r['cases'][c['compare_to']]['points'][i]['state'][:13]
  check('restart exact index and serialized parent',rec['index']==c['restart_index'] and rec['all_persistent_state']==z==pts[i]['state'][:13])
s=r['special'];base=m.branch(s['linearize']['state'],plan['special']['parameters']);check('native AD source branches away from boundaries',base is not None)
for name in ['linearize']+['fd-'+str(j)+'-'+str(sign)for j in range(6)for sign in [-1,1]]:
 x=s[name];diag=x['diagnostics'];check(name+'/single committed partition and source branch',diag['increment_fractions']==[1] and ('partition_committed'not in diag or diag['partition_committed']is True) and m.branch(x['state'],plan['special']['parameters'])==base)
refine=[v for v in source['results']if v['channel'].startswith('refinement-')];check('all86 refinements genuine decreases or predeclared tiny floor',len(refine)==86 and all(v['passed'] and (v['fine_normalized_error']<v['coarse_normalized_error']or max(v['fine_normalized_error'],v['coarse_normalized_error'])<1e-5)for v in refine))
summary={}
for resolution in [2048,4096]:
 ids={c['id']for c in plan['cases']if c.get('resolution')==resolution and c['group']in['axis','interior']};rows=[v for v in source['results']if v['case']in ids and any(v['channel'].startswith(k)for k in ['stress-source-','alpha-source-','void-source-','radial-source-'])];summary[str(resolution)]={'channels':len(rows),'worst_normalized_source_error':max(v['max_normalized_error']for v in rows)}
(D/'native-diagnostics.json').write_text(json.dumps({'compiled_calls':0,'checks':checks,'native_source_branch_signature':base,'source_errors':summary,'refinement_count':len(refine),'cross_backend_parity_observed':False},indent=2)+'\n');print(len(checks),summary)
