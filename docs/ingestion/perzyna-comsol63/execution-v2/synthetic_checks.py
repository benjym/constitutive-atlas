"""Pure synthetic assessor mutation checks. These are not material-engine observations."""
import copy,json,math
from study import BASE,SOLVER,MODEL,resolve,topology,assess
cases=json.loads((BASE/'cases.json').read_text())['cases'];catalogue=json.loads((BASE/'expected-catalogue.json').read_text())['sha256']
def manufacture():
 rows=[]
 for src in cases:
  c=resolve(src,rows);s=c['specification'];minimal=not c['ok'] and c.get('parse_failure')
  if minimal:r={'ok':False,'message':'v0.3 requires explicit state; initial literals are examples only' if c['id']=='missing-state' else 'parameter length, bounds or finiteness invalid'}
  else:
   message='' if c['ok'] else 'schedule solve failed in segment budget-exhaustion; last committed sample retained' if c.get('late') else 'invalid segment duration, identity or sample budget' if 'duration' in c['id'] else 'inadmissible initial state or outputs'
   r=dict(ok=c['ok'],schema_version='0.2',units='SI',model=MODEL,catalogue_hash=catalogue,message=message,**{k:s[k] for k in ['start_time','parameters','initial','initial_strain','initial_strain_rate','segments']},solver={**s['solver'],'maximum_depth':40},points=[])
   if c['ok'] or c.get('late'):
    topo=topology(s)[:4] if c.get('late') else topology(s)
    for i,(t,seg,side) in enumerate(topo):
     ref=next(x for x in c['references'] if abs(x['time']-t)<1e-12)
     rate=s['initial_strain_rate'] if seg<0 else [None if side=='right' and control['quantity']=='stress' else control.get('value',0) if control['kind']=='rate' else 0. for control in s['segments'][seg]['controls']]
     if seg>=0 and side=='left' and all(x['quantity']=='stress' and x['kind']=='hold' for x in s['segments'][seg]['controls']):
      from oracle import stress,dev,equivalent
      sigma=stress(s['initial'],s['parameters']);q=equivalent(sigma);Y,A,n=s['parameters'][2:];lam=A*max(q/Y-1,0)**n;rate=[1.5*lam*x/max(q,Y) for x in dev(sigma)]
     point=dict(time=t,segment=seg,side=side,state=list(ref['state']),strain=list(ref['state'][:6]),strain_rate=rate,observables=list(ref['stress']),iterations=1 if side=='left' and seg>=0 else 0,substeps=2 if side=='left' and seg>=0 else 0,rejected=0,temporal_error_norm=0.,nonlinear_residual_norm=0.)
     if c['id']=='refinement-coarse' and i==len(topo)-1:point['state'][0]+=1e-5;point['strain'][0]+=1e-5;point['observables'][0]+=10.
     r['points'].append(point)
  raw=json.dumps(r,allow_nan=True)
  rows.append(dict(id=c['id'],request={k:c[k] for k in ['call','types','args','argv']},calls=[dict(returncode=0 if c['ok'] else 1,stdout=raw,stderr='') for _ in range(2)]))
 return rows
rows=manufacture();positive=assess(cases,rows);mutations=[]
def reject(name,caseid,fn):
 clone=copy.deepcopy(rows);i=next(i for i,r in enumerate(clone) if r['id']==caseid);r=json.loads(clone[i]['calls'][0]['stdout']);fn(r);raw=json.dumps(r,allow_nan=True)
 for call in clone[i]['calls']:call['stdout']=raw
 try:assess(cases,clone)
 except (AssertionError,ValueError,KeyError,TypeError,IndexError):mutations.append({'name':name,'rejected':True})
 else:raise AssertionError('Assessor accepted mutation '+name)
reject('wrong catalogue','public-relaxation',lambda r:r.update(catalogue_hash='0'*64))
reject('wrong solver method','public-relaxation',lambda r:r['solver'].update(method='midpoint-step-doubling'))
reject('wrong parameters','public-relaxation',lambda r:r['parameters'].__setitem__(0,1))
reject('missing state component','public-relaxation',lambda r:r['points'][-1]['state'].pop())
reject('missing stress component','public-relaxation',lambda r:r['points'][-1]['observables'].pop())
reject('nonfinite state','public-relaxation',lambda r:r['points'][-1]['state'].__setitem__(0,float('nan')))
reject('negative accumulated strain','public-relaxation',lambda r:r['points'][-1]['state'].__setitem__(12,-1))
reject('plastic trace','public-relaxation',lambda r:r['points'][-1]['state'].__setitem__(6,1))
reject('state out of budget','public-relaxation',lambda r:r['points'][-1]['state'].__setitem__(0,10))
reject('stress out of budget','public-relaxation',lambda r:r['points'][-1]['observables'].__setitem__(0,1e12))
reject('changed entry state','public-relaxation',lambda r:r['points'][1]['state'].__setitem__(0,.1))
reject('wrong topology','public-relaxation',lambda r:r['points'][-1].update(side='right'))
reject('wrong clock','public-relaxation',lambda r:r['points'][-1].update(time=99))
reject('changed public control','public-rate',lambda r:r['segments'][0]['controls'][0].update(value=99))
reject('wrong solved creep rate','public-creep',lambda r:r['points'][-1]['strain_rate'].__setitem__(0,0))
reject('wrong prescribed rate','public-rate',lambda r:r['points'][-1]['strain_rate'].__setitem__(0,99))
reject('stress entry rate should be null','public-creep',lambda r:r['points'][1]['strain_rate'].__setitem__(0,0))
reject('early failure fabricated point','negative-alpha',lambda r:r['points'].append({}))
reject('parse error extra state','missing-state',lambda r:r.update(state=[]))
reject('late failure erased committed sample','late-budget-rollback',lambda r:r['points'].pop())
reject('late failure leaked candidate','late-budget-rollback',lambda r:r['points'].append(copy.deepcopy(r['points'][-1])))
reject('late failure no consumed budget','late-budget-rollback',lambda r:r['points'][2].update(substeps=0))
reject('late failure no prior trial','late-budget-rollback',lambda r:r['points'][2].update(iterations=0))
reject('late failure rewrote committed state','late-budget-rollback',lambda r:r['points'][3]['state'].__setitem__(0,.1))
# Repeat integrity and request tampering are separate from serialized result mutation.
for name,mutate in [('nonexact repeat',lambda rr:rr[0]['calls'][1].update(stdout='{}')),('wrong request',lambda rr:rr[0]['request']['args'].__setitem__(7,123))]:
 clone=copy.deepcopy(rows);mutate(clone)
 try:assess(cases,clone)
 except (AssertionError,ValueError,KeyError,TypeError,IndexError):mutations.append({'name':name,'rejected':True})
 else:raise AssertionError(name)
report={'identity':'perzyna-be-schedule-v2-synthetic-assessor-checks','synthetic_only':True,'compiled_calls':0,'positive_synthetic_cases':positive['cases'],'negative_mutations_rejected':len(mutations),'mutations':mutations}
(BASE/'synthetic-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
