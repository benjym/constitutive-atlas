"""Prospective BE-schedule-only study. No constitutive kernel or runtime modification."""
import argparse,copy,hashlib,json,math,pathlib,subprocess,sys
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[3];sys.path.insert(0,str(BASE));sys.path.insert(0,str(ROOT))
from oracle import P,Z,ZERO,stress,relaxation
MODEL='perzyna-comsol63-mises-perfect-zero-spin-ode'
SOLVER=dict(method='backward-euler-step-doubling',relative_tolerance=1e-9,absolute_scale_fraction=1e-12,minimum_step=1e-12,maximum_step=5/12288,maximum_substeps=1000000,nonlinear_tolerance=1e-10,maximum_iterations=40)
csv=lambda xs:','.join(format(x,'.17g') for x in xs)
parse=lambda x:[float(v) for v in x.split(',')] if x else []
def encode(c):
 s=c['specification'];wire=[]
 for seg in s['segments']:
  wire.extend([seg['duration'],seg['samples']])
  for control in seg['controls']:wire.extend([int(control['quantity']=='stress'),{'hold':0,'rate':1,'target':2}[control['kind']],control.get('value',0)])
 a=s['solver'];args=[MODEL,csv(s['parameters']),csv(s['initial']),csv(s['initial_strain']),csv(s['initial_strain_rate']),csv(wire),','.join(x['id'] for x in s['segments']),s['start_time'],a['relative_tolerance'],a['absolute_scale_fraction'],a['minimum_step'],a['maximum_step'],a['maximum_substeps'],a['nonlinear_tolerance'],a['maximum_iterations']]
 argv=['--mode','schedule']
 for key,v in zip(['--model','--parameters','--initial','--initial-strain','--initial-strain-rate','--segments','--segment-ids','--start-time','--rtol','--atol','--min-time-step','--max-time-step','--max-substeps','--nonlinear-tolerance','--max-iterations'],args):argv +=[key,str(v)]
 c.update(call='atlas_run_schedule',types=['string']*7+['number']*8,args=args,argv=argv,kind='schedule');return c

def resolve(c,prior):
 c=copy.deepcopy(c)
 if c.get('restart_from'):
  parent=json.loads(next(r for r in prior if r['id']==c['restart_from'])['calls'][0]['stdout'])['points'][-1]
  z=parent['state'];t=parent['time'];s=c['specification'];assert t==s['start_time']
  s.update(initial=z,initial_strain=parent['strain'],initial_strain_rate=parent['strain_rate'],start_time=t);c['initial']=z
  end=t+s['segments'][0]['duration'];target=relaxation(z,end-t)
  c['references']=[dict(time=t,state=z,stress=stress(z)),dict(time=end,state=target,stress=stress(target))];encode(c)
 return c

def compare(actual,expected,kind,coarse=False):
 assert len(actual)==len(expected)
 worst=0.
 for x,y in zip(actual,expected):
  assert type(x) in (int,float) and math.isfinite(x)
  floor=((1000. if coarse else 3.) if kind=='stress' else (.001 if coarse else 3e-7));bound=max(floor,2e-5*abs(y));err=abs(x-y)
  assert err<=bound,(kind,err,bound,x,y);worst=max(worst,err)
 return worst

def topology(spec):
 result=[(spec['start_time'],-1,'left')];entry=spec['start_time']
 for i,seg in enumerate(spec['segments']):
  end=entry+seg['duration'];result.append((entry,i,'right'))
  result.extend(((end if j==seg['samples'] else entry+seg['duration']*(j/seg['samples'])),i,'left') for j in range(1,seg['samples']+1));entry=end
 return result

def assess(cases,rows):
 assert [c['id'] for c in cases]==[r['id'] for r in rows];errors={};count=0;expected_hash=json.loads((BASE/'expected-catalogue.json').read_text())['sha256']
 def finite(v,n):assert isinstance(v,list) and len(v)==n and all(type(x) in (int,float) and math.isfinite(x) for x in v)
 def domain(z):finite(z,13);assert z[12]>=0 and abs(math.fsum(z[6:9]))<=1e-10
 for index,(src,row) in enumerate(zip(cases,rows)):
  c=resolve(src,rows[:index]);spec=c['specification'];request=row['request']
  assert set(request)=={'call','types','args','argv'} and request['call']==c['call'] and request['types']==c['types']
  assert len(request['args'])==15 and request['args'][0]==c['args'][0] and request['args'][6]==c['args'][6]
  for j in range(1,6):assert parse(request['args'][j])==parse(c['args'][j]),(c['id'],'request CSV',j)
  assert request['args'][7:]==c['args'][7:]
  assert len(request['argv'])==len(c['argv']) and request['argv'][::2]==c['argv'][::2]
  for flag,actual,expected in zip(c['argv'][::2],request['argv'][1::2],c['argv'][1::2]):
   if flag in ['--parameters','--initial','--initial-strain','--initial-strain-rate','--segments']:assert parse(actual)==parse(expected)
   elif flag in ['--mode','--model','--segment-ids']:assert actual==expected
   else:assert float(actual)==float(expected)
  assert len(row['calls'])==2 and row['calls'][0]['stdout']==row['calls'][1]['stdout'],c['id']
  assert all(call['returncode']==(0 if c['ok'] else 1) and isinstance(call['stderr'],str) for call in row['calls'])
  r=json.loads(row['calls'][0]['stdout']);assert r['ok'] is c['ok'],(c['id'],r)
  if not c['ok'] and c.get('parse_failure'):
   message='v0.3 requires explicit state; initial literals are examples only' if c['id']=='missing-state' else 'parameter length, bounds or finiteness invalid'
   assert r==dict(ok=False,message=message);continue
  assert set(r)=={'ok','schema_version','units','model','catalogue_hash','message','start_time','parameters','initial','initial_strain','initial_strain_rate','solver','segments','points'}
  assert r['schema_version']=='0.2' and r['units']=='SI' and r['catalogue_hash']==expected_hash and r['model']==MODEL
  for k in ['start_time','parameters','initial','initial_strain','initial_strain_rate','segments']:assert r[k]==spec[k],(c['id'],k)
  assert r['solver']=={**spec['solver'],'maximum_depth':40}
  if not c['ok'] and not c.get('late'):
   message='invalid segment duration, identity or sample budget' if 'duration' in c['id'] else 'inadmissible initial state or outputs'
   assert r['message']==message and r['points']==[],(c['id'],r);continue
  assert r['message']==('schedule solve failed in segment budget-exhaustion; last committed sample retained' if c.get('late') else '')
  topo=topology(spec)
  if c.get('late'):topo=topo[:4]
  assert len(r['points'])==len(topo),(c['id'],len(r['points']),len(topo))
  ee=pe=0.;previous=None;coarse=c['id']=='refinement-coarse'
  for point,(time,segment,side) in zip(r['points'],topo):
   assert set(point)=={'time','segment','side','state','strain','strain_rate','observables','iterations','substeps','rejected','temporal_error_norm','nonlinear_residual_norm'}
   assert type(point['time']) in (int,float) and math.isfinite(point['time']) and type(point['segment']) is int
   assert isinstance(point['strain_rate'],list) and len(point['strain_rate'])==6
   assert point['time']==time and point['segment']==segment and point['side']==side,(c['id'],point['time'],time)
   domain(point['state']);finite(point['strain'],6);finite(point['observables'],6);assert point['strain']==point['state'][:6]
   for k in ['iterations','substeps','rejected']:assert type(point[k]) is int and point[k]>=0
   for k in ['temporal_error_norm','nonlinear_residual_norm']:assert type(point[k]) in (int,float) and math.isfinite(point[k]) and point[k]>=0
   if previous is None:
    assert point['state']==spec['initial'] and point['strain']==spec['initial_strain'] and point['strain_rate']==spec['initial_strain_rate']
   else:
    assert point['state'][12]>=previous['state'][12]
    if side=='right':assert point['state']==previous['state'] and point['strain']==previous['strain']
   if segment>=0:
    for j,ctrl in enumerate(spec['segments'][segment]['controls']):
     value=point['strain_rate'][j]
     if side=='right' and ctrl['quantity']=='stress':assert value is None
     else:
      assert type(value) in (int,float) and math.isfinite(value)
      if ctrl['quantity']=='strain':
       expected_rate=ctrl.get('value',0) if ctrl['kind']=='rate' else 0
       if side=='right' or expected_rate==0:assert value==expected_rate
       else:assert abs(value-expected_rate)<=4*sys.float_info.epsilon*abs(expected_rate)
      elif side=='left':
       from oracle import dev,equivalent
       initial_stress=stress(spec['initial'],spec['parameters']);deviator=dev(initial_stress);q=equivalent(initial_stress);Y,A,n=spec['parameters'][2:]
       lam=A*max(q/Y-1,0)**n;expected_rate=1.5*lam*deviator[j]/max(q,Y)
       assert abs(value-expected_rate)<=max(1e-10,2e-5*abs(expected_rate)),(c['id'],'creep rate',j,value,expected_rate)
   ref=next((x for x in c['references'] if abs(x['time']-time)<1e-12),None);assert ref,(c['id'],time)
   ee=max(ee,compare(point['state'],ref['state'],'state',coarse));pe=max(pe,compare(point['observables'],ref['stress'],'stress',coarse));count+=19;previous=point
  if c.get('late'):
   first=r['points'][2];entry=r['points'][3]
   assert first['time']>spec['start_time'] and first['substeps']==2 and first['iterations']>0
   assert first['state']!=spec['initial'] and entry['state']==first['state'] and entry['observables']==first['observables']
   assert sum(p['substeps'] for p in r['points'])==spec['solver']['maximum_substeps']==2
  else:errors[c['id']]=dict(state=ee,stress=pe)
 assert errors['refinement-fine']['state']<errors['refinement-coarse']['state']/5
 assert errors['refinement-fine']['stress']<errors['refinement-coarse']['stress']/5
 return dict(passed=True,cases=len(cases),raw_calls=2*len(cases),numeric_comparisons=count,errors=errors,scope='BE schedule only; direct midpoint integrate-time excluded')

def collect(solver,output):
 cases=json.loads((BASE/'cases.json').read_text())['cases'];rows=[]
 for source in cases:
  c=resolve(source,rows);row={'id':c['id'],'request':{k:c[k] for k in ['call','types','args','argv']},'calls':[]}
  for _ in range(2):
   proc=subprocess.run([str(solver.resolve()),*c['argv']],capture_output=True,text=True,timeout=180);row['calls'].append(dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
  rows.append(row);output.write_text(json.dumps(rows,indent=2)+'\n')
 report=assess(cases,rows);output.with_name(output.stem+'-report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','native','assess']);ap.add_argument('--solver',type=pathlib.Path);ap.add_argument('--raw',type=pathlib.Path);a=ap.parse_args()
 if a.action=='prepare':raise SystemExit('Use prepare.py; references are generated independently before observations')
 elif a.action=='native':print(json.dumps(collect(a.solver,a.raw),indent=2))
 else:print(json.dumps(assess(json.loads((BASE/'cases.json').read_text())['cases'],json.loads(a.raw.read_text())),indent=2))
