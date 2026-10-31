from pathlib import Path
import json,copy
from assess import assess
s=Path(__file__).resolve().parent;req=json.loads((s/'request.json').read_text());diag={'iterations':2,'substeps':1,'rejected':0,'error':0.};points=[dict(control=0.,state=req['initial'],strain=[0.]*6,u=0.,diagnostics=dict(iterations=0,substeps=0,rejected=0,error=0.))];calls=[]
for i,h in enumerate(req['common_controls_hex'],1):
 control=float.fromhex(h);old=points[-1];delta=control-old['control'];de=[delta/36000000.,-delta/72000000.,-delta/72000000.,0.,0.,0.];state=[100000.+2*control/3,100000.-control/3,100000.-control/3,0.,0.,0.];strain=[a+b for a,b in zip(old['strain'],de)]
 point=dict(control=control,state=state,strain=strain,u=100000.-state[1],diagnostics=diag);calls.append(dict(step=i,iteration=0,role='trial',de=de,parent=old['state'],ok=True,state=state,diagnostics=diag));points.append(point)
run={'ok':True,'points':points};doc={'schema':'control-trace-diagnostic-v1','catalogue_hash':'synthetic','streams':[{'id':sid,'baseline':copy.deepcopy(run),'traced':copy.deepcopy(run),'calls':copy.deepcopy(calls)}for sid in ('backend-sine','common-literal')]};assert assess(doc,req)['diagnostic_fidelity_passed']
mutations={
 'logging-state-drift':lambda x:x['streams'][0]['traced']['points'][1]['state'].__setitem__(0,0.),
 'call-state-drift':lambda x:x['streams'][0]['calls'][0]['state'].__setitem__(0,0.),
 'parent-drift':lambda x:x['streams'][0]['calls'][0]['parent'].__setitem__(0,0.),
 'missing-step':lambda x:x['streams'][0]['calls'].pop(),
 'nonzero-volume':lambda x:x['streams'][0]['calls'][0]['de'].__setitem__(1,1.),
 'wrong-control':lambda x:x['streams'][1]['traced']['points'][1].update(control=0.),
 'wrong-role':lambda x:x['streams'][0]['calls'][0].update(role='pert'),
 'wrong-iteration':lambda x:x['streams'][0]['calls'][0].update(iteration=1),
 'wrong-settings-diagnostics':lambda x:x['streams'][0]['calls'][0]['diagnostics'].update(iterations=99),
}
rejected=[]
# JSON serialization breaks aliases deliberately; each corruption is independent.
for name,mutate in mutations.items():
 x=json.loads(json.dumps(doc));mutate(x)
 try:assess(x,req)
 except Exception:rejected.append(name)
 else:raise RuntimeError('false pass '+name)
(s/'preflight-results.json').write_text(json.dumps({'passed':True,'synthetic_streams':2,'synthetic_points_per_stream':65,'rejected':rejected,'candidate_calls':0},indent=2)+'\n');print('preflight',len(rejected),'corruptions rejected')
