"""Apply prospective material/API gates to saved observations; never fits a law."""
from pathlib import Path
from decimal import localcontext
import json,sys,math,struct,hashlib
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from reference import eigen,q,quantities
req=json.loads((B/'requests.json').read_text());out=json.loads(Path(sys.argv[1]).read_text());fail=[];summary={}
def check(x,label):
 if not x:fail.append(label)
def bits(x):return [struct.pack('>d',float(v)).hex() for v in x]
def same(x,y):return bits(x)==bits(y)
def error(x,y):return max((abs(float(a)-float(b))/1e5 for a,b in zip(x,y)),default=math.inf) if len(x)==len(y) else math.inf
def physical(z,old,label):
 check(len(z)==7 and all(math.isfinite(x) for x in z),label+' finite shape')
 if len(z)!=7 or not all(math.isfinite(x) for x in z):return
 with localcontext() as c:
  c.prec=60;v=eigen(z[:6]);D=float(max(v)-min(v));smin=float(min(v))
 check(smin>0 and z[6]>=0 and z[6]+2e-10*1e5>=D,label+' source admissibility')
 check(z[6]>=old[6],label+' history monotone')
check(out['requests_sha256']==hashlib.sha256((B/'requests.json').read_bytes()).hexdigest(),'request identity')
expected_metadata=json.loads((B/'frozen/generated/models.json').read_text());check(out['describe']['response']==expected_metadata,'embedded catalogue identity')
worst=0.
for c,a in zip(req['cases'],out['cases']):
 label=c['id'];r=a['calls'][0]['response'];check(r.get('ok'),label+' accepted')
 if not r.get('ok'):continue
 check(a['admissible']['response']['ok'],label+' exact engine constraint');z=r['state'];e=error(z,c['target']);worst=max(worst,e);check(e<=2e-8,label+' source endpoint');physical(z,c['initial'],label)
 check(r['diagnostics']['substeps']==1,label+' unsplit endpoint');check(a['calls'][1]['response'].get('ok') and same(z,a['calls'][1]['response'].get('state',[])),label+' replay')
 ev=a['residual']['response'];check(ev.get('ok') and max(map(abs,ev.get('values',[math.inf])))/1e5<=2e-10,label+' residual')
summary['endpoint_max_normalized_error']=worst
case_results={a['id']:a['calls'][0]['response'] for a in out['cases']}
for c in req['cases']:
 if 'rotation_partner' not in c:continue
 a=case_results[c['rotation_partner']];b=case_results[c['id']]
 if not a.get('ok') or not b.get('ok'):continue
 v=a['state'];R=c['rotation'];A=[[v[0],v[3]/math.sqrt(2),v[5]/math.sqrt(2)],[v[3]/math.sqrt(2),v[1],v[4]/math.sqrt(2)],[v[5]/math.sqrt(2),v[4]/math.sqrt(2),v[2]]];T=[[sum(R[i][k]*A[k][l]*R[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)];target=[T[i][i] for i in range(3)]+[math.sqrt(2)*T[i][j] for i,j in [(0,1),(1,2),(0,2)]]+[v[6]]
 check(error(target,b['state'])<=2e-8,c['id']+' paired covariance')
paths={};hyper={};cross={};patherrors={}
for p,a in zip(req['paths'],out['paths']):
 label=p['id'];calls=a['calls'];check(len(calls)==len(p['increments']) and all(x['response'].get('ok') for x in calls),label+' complete')
 old=p['initial'];branches=set()
 for i,x in enumerate(calls):
  r=x['response']
  if not r.get('ok'):break
  z=r['state']
  with localcontext() as ctx:
   ctx.prec=60;branches.add(quantities(z,old,p['parameters'])[2])
  check(i<len(a['constraints']) and a['constraints'][i]['response']['ok'],label+' exact engine constraint '+str(i));physical(z,old,label+':'+str(i));old=z
  check(i<len(a['holds']) and a['holds'][i]['response'].get('ok') and same(z,a['holds'][i]['response'].get('state',[])),label+' hold '+str(i))
  if p['kind']=='known-history':check(error(z,p['targets'][i])<=2e-8,label+' known source history '+str(i))
 check(len(a['restart'])==len(p['increments'])-a['restart_index'],label+' restart complete')
 for i,x in enumerate(a['restart']):
  j=i+a['restart_index'];check(j<len(calls) and x['response'].get('ok') and same(x['response'].get('state',[]),calls[j]['response'].get('state',[])),label+' restart '+str(i))
 if not calls or not calls[-1]['response'].get('ok'):continue
 z=calls[-1]['response']['state'];paths[label]=z
 if p['kind']=='hyperbola':
  D=z[0]-z[1];finiteerr=abs(D-float(p['expected_D']))/1e5;he=abs(D-float(p['hyperbola_D']))/max(float(p['F']),1e5);check(finiteerr<=2e-8,label+' independent quadratic root');patherrors[label]=dict(finite_endpoint_error=finiteerr,hyperbola_error=he)
  group=label.rsplit('-',1)[0];hyper.setdefault(group,[]).append((len(p['increments']),he))
 elif p['kind'] in ('max-crossing','failure-crossing'):
  check({'primary','unload_reload' if p['kind']=='max-crossing' else 'postfailure'}<=branches,label+' named branch crossing');cross.setdefault(label.rsplit('-',1)[0],{})[p['partitions']]=z
for label,rows in hyper.items():
 rows.sort();check(rows[-1][0]==128 and rows[-1][1]<=1e-3,label+' finest hyperbola')
 for (_,a),(_,b) in zip(rows[-3:],rows[-2:]):check(b==0 or a/b>=1.5,label+' refinement')
for label,rows in cross.items():check(64 in rows and 128 in rows and error(rows.get(64,[]),rows.get(128,[]))<=1e-2,label+' crossing convergence')
summary['paths']=patherrors
for c,a in zip(req['transactions'],out['transactions']):
 r=a['call']['response'];check(not r.get('ok') and same(r.get('state',[]),c['initial']),c['id']+' full parent rollback');check(r.get('diagnostics',{}).get('substeps',-1)>=c['min_internal_substeps'],c['id']+' tentative substeps');check(a['recovery']['response'].get('ok') and error(a['recovery']['response'].get('state',[]),req['cases'][0]['target'])<=2e-8,c['id']+' nonzero recovery')
for c,a in zip(req['invalids'],out['invalids']):
 r=a['call']['response'];check(not r.get('ok'),c['id']+' reject');check('state' not in r or same(r['state'],c.get('initial',[])),c['id']+' immutable parent');check(a['recovery']['response'].get('ok') and error(a['recovery']['response'].get('state',[]),req['cases'][0]['target'])<=2e-8,c['id']+' nonzero recover')
for c,a in zip(req['diagnostics'],out['diagnostics']):check(a['call']['response'].get('ok')==c['expect_success'],c['id']+' resolution rejection')
summary['derivatives']=[]
for c,a in zip(req['derivatives'],out['derivatives']):
 r=a['call']['response'];check(r.get('ok'),c['id']+' AD');errors=[]
 if not r.get('ok'):continue
 jac=r['jacobian'];check(len(jac)==7 and all(len(x)==20 for x in jac),c['id']+' AD shape')
 for sweep in c['sweeps']:
  errors.append(max(abs(jac[i][j]-float(sweep['columns'][j][i]))/max(1.,abs(float(sweep['columns'][j][i]))) for i in range(7) for j in range(20)))
 check(any(a<=2e-5 and b<=2e-5 for a,b in zip(errors,errors[1:])),c['id']+' FD plateau');summary['derivatives'].append(dict(id=c['id'],errors=errors))
for c,a in zip(req['presets'],out['presets']):
 r=a['call']['response'];label=c['id'];points=r.get('points',[]);check(r.get('ok') and len(points)==c['steps']+1,label+' public run complete')
 check(not a['invalid']['response'].get('ok'),label+' invalid public run');check(a['recovery']['response'].get('ok'),label+' public recovery')
 check(a['hold']['response'].get('ok') and points and same(a['hold']['response'].get('state',[]),points[-1]['state']),label+' public endpoint hold')
 replay=a['replay']['response'].get('points',[]);check(a['replay']['response'].get('ok') and len(replay)==len(points) and all(same(x['state'],y['state']) for x,y in zip(points,replay)),label+' public exact replay')
 tail=a['restart']['response'].get('points',[]);check(a['restart']['response'].get('ok') and len(tail)==c['steps']//2+1 and all(error(x['state'],y['state'])<=2e-8 for x,y in zip(points[c['steps']//2:],tail)),label+' public checkpoint continuation')
 check(len(a['recovery']['response'].get('points',[]))==len(points) and all(same(x['state'],y['state']) for x,y in zip(points,a['recovery']['response'].get('points',[]))),label+' public post-invalid replay')
 old=c['initial']
 for point in points:physical(point['state'],old,label);old=point['state'];check(len(point['strain'])==6,label+' strain shape')
 if points:
  p=c['parameters'];conf=100000.;Ei=p['K']*p['pa']*(conf/p['pa'])**p['n'];F=2*(p['c_cohesion']*math.cos(p['phi'])+conf*math.sin(p['phi']))/(1-math.sin(p['phi']));D=Ei*c['target']/(1+p['Rf']*Ei*c['target']/F);check(abs(points[-1]['state'][0]-points[-1]['state'][1]-D)/max(F,1e5)<=1e-3,label+' source hyperbola')
for k in ['cases','paths','transactions','invalids','diagnostics','derivatives','presets']:
 check(len(req[k])==len(out[k]),k+' full coverage');check([c['id'] for c in req[k]]==[a['id'] for a in out[k]],k+' ordered identity')
result=dict(identity='duncan-complete-material-api-v1-assessment',backend=out['backend'],observation_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),pass_=not fail,failures=fail,summary=summary)
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(pass_=not fail,failures=fail,endpoint_error=worst)));sys.exit(bool(fail))
