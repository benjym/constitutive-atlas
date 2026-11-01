"""Prospective corrected-assessor tests, no compiled execution."""
import copy,hashlib,json,pathlib,sys
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parents[3];EX=OUT.parent/'execution-v1';sys.path.insert(0,str(EX));import study,oracle
cases=json.loads((EX/'cases.json').read_text())['cases'];ch=json.loads((EX/'expected-catalogue.json').read_text())['sha256'];rows=[]
def meta(c,parent):
 return dict(ok=c['ok'],message='',schema_version='0.2',catalogue_hash=ch,model=study.MODEL,parameters=list(map(float,c['args'][1].split(','))),initial=parent,strain_rate=list(map(float,c['args'][3].split(','))),start_time=c['args'][4],duration=c['args'][5],solver=dict(method='midpoint-step-doubling',relative_tolerance=c['args'][6],absolute_scale_fraction=c['args'][7],minimum_step=c['args'][8],maximum_step=c['args'][9],maximum_substeps=c['args'][10],maximum_depth=40))
for c in cases:
 if not c['ok'] and c['id'] in ('zero-viscosity','negative-yield','missing-state'):
  r=dict(ok=False,message='v0.3 requires explicit state; initial literals are examples only' if c['id']=='missing-state' else 'parameter length, bounds or finiteness invalid')
 elif c['kind']=='direct':
  parent=list(map(float,c['args'][2].split(',')));r=meta(c,parent);r.update(state=copy.deepcopy(c['expected'] if c['ok'] else parent),time=c['time'] if c['ok'] else c['args'][4],substeps=1 if c.get('late') else 0)
  if not c['ok']:r['message']='physical-time integration failed; state and clock rolled back' if c.get('late') else 'invalid physical time or solver settings' if 'duration' in c['id'] else 'invalid parameters or inadmissible initial state'
 else:
  spec=c['specification'];r=dict(ok=True,message='',schema_version='0.2',catalogue_hash=ch,model=study.MODEL,units='SI',parameters=oracle.P,initial=c['initial'],start_time=spec['start_time'],initial_strain=spec['initial_strain'],initial_strain_rate=spec['initial_strain_rate'],solver={**spec['solver'],'maximum_depth':40},segments=spec['segments'],points=[])
  topology=[(0.,-1,'left')];t=0.
  for i,seg in enumerate(spec['segments']):
   topology.append((t,i,'right'));topology.extend((t+seg['duration']*j/seg['samples'],i,'left') for j in range(1,seg['samples']+1));t+=seg['duration']
  for t,i,side in topology:
   ref=next(x for x in c['references'] if x['time']==t);z=copy.deepcopy(ref['state']);sig=copy.deepcopy(ref['stress']);rate=oracle.ZERO if i<0 else [(None if side=='right' else 0.) if control['quantity']=='stress' else control.get('value',0.) for control in spec['segments'][i]['controls']]
   if c['id']=='refinement-coarse':z[12]+=1e-5 if t else 0;sig[0]+=1.
   r['points'].append(dict(time=t,segment=i,side=side,state=z,strain=z[:6],strain_rate=rate,observables=sig))
 row=dict(id=c['id'],calls=[dict(stdout=json.dumps(r),returncode=0 if c['ok'] else 1)]*2)
 if c['ok'] and c['kind']=='direct':row['observation']=json.dumps(dict(ok=True,values=c['expected_stress']))
 rows.append(row)
study.assess(cases,rows)
def test(name,ident,fn):
 rr=copy.deepcopy(rows);row=next(r for r in rr if r['id']==ident);r=json.loads(row['calls'][0]['stdout']);fn(r);row['calls']=[dict(stdout=json.dumps(r),returncode=row['calls'][0]['returncode'])]*2
 try:study.assess(cases,rr);return dict(id=name,rejected=False)
 except (AssertionError,KeyError,IndexError):return dict(id=name,rejected=True)
tests=[test('direct-negative-alpha','zero-hold',lambda r:r['state'].__setitem__(12,-1e-8)),test('schedule-duplicate-point','public-creep',lambda r:r['points'].append(copy.deepcopy(r['points'][1]))),test('schedule-reverse-order','public-creep',lambda r:r['points'].reverse()),test('invalid-arbitrary-parent','negative-alpha',lambda r:r.update(state=[123.]*13,time=-999.)),test('incorrect-control-rate','public-rate',lambda r:r['points'][2]['strain_rate'].__setitem__(0,9.)),test('incorrect-segment','public-rate',lambda r:r['points'][1].update(segment=9)),test('wrong-failure-message','zero-duration',lambda r:r.update(message='other'))]
freeze=json.loads((EX/'freeze-v3.json').read_text());bindings=[dict(path=n,sha256=h,matched=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h) for n,h in freeze['files'].items()]
result=dict(compiled_execution=False,synthetic_baseline_passed=True,mutation_checks=tests,all_mutations_rejected=all(t['rejected'] for t in tests),freeze_files=len(bindings),all_bindings_matched=all(t['matched'] for t in bindings))
(OUT/'check-results-v2.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'input-binding-v2.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',freeze='execution-v1/freeze-v3.json',freeze_sha256=hashlib.sha256((EX/'freeze-v3.json').read_bytes()).hexdigest(),files=bindings),indent=2)+'\n');print(json.dumps(result,indent=2))
