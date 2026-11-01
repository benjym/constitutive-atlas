"""Read-only prospective reviewer checks; uses no compiled engine."""
import copy,hashlib,importlib.util,json,math,pathlib,sys
OUT=pathlib.Path(__file__).resolve().parent; ROOT=OUT.parents[3]; EX=OUT.parent/'execution-v1';sys.path.insert(0,str(EX))
import study,oracle
cases=json.loads((EX/'cases.json').read_text())['cases'];rows=[]
for c in cases:
 r={'ok':c['ok']}
 if not c['ok']:
  if c.get('late'):r.update(state=oracle.Z,time=3.,substeps=1)
 elif c['kind']=='direct':
  r.update(state=c['expected'],time=c['time'])
 else:
  points=[dict(time=x['time'],state=list(x['state']),observables=list(x['stress']),strain=list(x['state'][:6])) for x in c['references']]
  if c['id']=='refinement-coarse':
   for pt in points:pt['state'][12]+=1e-5;pt['observables'][0]+=1.
  r.update(model=study.MODEL,units='SI',parameters=oracle.P,initial=c['initial'],points=points)
 row=dict(id=c['id'],calls=[dict(stdout=json.dumps(r))]*2)
 if c['ok'] and c['kind']=='direct':row['observation']=json.dumps(dict(ok=True,values=c['expected_stress']))
 rows.append(row)
study.assess(cases,rows)
def mutation(name,fn):
 rr=copy.deepcopy(rows);fn(rr)
 try:study.assess(cases,rr);return dict(id=name,accepted_by_v1_assessor=True)
 except AssertionError:return dict(id=name,accepted_by_v1_assessor=False)
def edit(rr,ident,fn):
 row=next(x for x in rr if x['id']==ident);r=json.loads(row['calls'][0]['stdout']);fn(r);row['calls']=[dict(stdout=json.dumps(r))]*2
mutations=[mutation('direct-negative-alpha',lambda rr:edit(rr,'zero-hold',lambda r:r['state'].__setitem__(12,-1e-8))),mutation('schedule-duplicate-point',lambda rr:edit(rr,'public-creep',lambda r:r['points'].append(copy.deepcopy(r['points'][1])))),mutation('schedule-reversed-time-order',lambda rr:edit(rr,'public-creep',lambda r:r['points'].reverse())),mutation('invalid-failure-arbitrary-state',lambda rr:edit(rr,'negative-alpha',lambda r:r.update(state=[123.]*13,time=-999.)))]
f=json.loads((EX/'freeze-v1.json').read_text());fchecks=[dict(path=n,sha256=h,matched=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h) for n,h in f['files'].items()]
s=json.loads((OUT.parent/'source-v1/source-receipts.json').read_text());schecks=[dict(private_path=x['private_path'],sha256=x['sha256'],matched=hashlib.sha256(pathlib.Path(x['private_path']).read_bytes()).hexdigest()==x['sha256']) for x in s['receipts']]
# Independent pointwise Mandel contractions and flow identities, direct scalar arithmetic.
errors=[]
for j in range(1,101):
 v=[math.sin(j*(i+1))*.03 for i in range(6)];m=sum(v[:3])/3;d=[x-(m if i<3 else 0) for i,x in enumerate(v)];s=[2*1e7*x for x in d];q=math.sqrt(1.5*sum(x*x for x in s));lam=max(q-1e5,0)/2e7;flow=[1.5*lam*x/max(q,1e5) for x in s];errors.append(max(abs(sum(flow[:3])),abs(math.sqrt(2*sum(x*x for x in flow)/3)-lam),abs(sum(a*b for a,b in zip(s,flow))-q*lam)))
result=dict(compiled_execution=False,baseline_synthetic_assessment_passed=True,assessor_mutations=mutations,freeze_files=len(fchecks),freeze_all_matched=all(x['matched'] for x in fchecks),source_receipts=len(schecks),source_all_matched=all(x['matched'] for x in schecks),pointwise_identity_cases=100,max_absolute_identity_residual=max(errors))
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'input-binding.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',independence='Separate agent; did not author source packet, candidate, production or study.',model=study.MODEL,model_sha256=hashlib.sha256((ROOT/'models/research/bingham'/f'{study.MODEL}.json').read_bytes()).hexdigest(),freeze_manifest_sha256=hashlib.sha256((EX/'freeze-v1.json').read_bytes()).hexdigest(),frozen_inputs=fchecks,private_source_receipts=schecks),indent=2)+'\n');print(json.dumps(result,indent=2))
