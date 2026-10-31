"""Source-reference ideal frames and deliberately corrupted frames; no candidate calls."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,gzip,copy,sys
import assess as a
P=Path(__file__).resolve().parent
rows=a.load(P/'requests.json');refs={c['id']:c['canonical']for f in(P/'reference/reference-p360.json.gz',P/'supplemental-reference/reference-p360.json.gz')for c in a.load(f)['cases']};fields=a.load(P/'trace-fields.json')
def trace(ref):
 p={k:D(v)for k,v in ref['coefficients'].items()};K,G,c,s,d,cf=[p[k]for k in('K','G','c','sf','sd','cf')];v1,v2,v3=map(D,ref['eigenvalues']);x,y=v1-v2,v2-v3;h=2*c*cf;A=2*(K-2*G/3)*d;ds=4*K*d*s+4*G*(1+d*s/3);dl=4*K*d*s+G*(3-s-d+d*s/3);dr=4*K*d*s+G*(3+s+d+d*s/3);da=4*K*d*s;F=(1+s)*v1-(1-s)*v3-h
 q=dict(K=K,G=G,sf=s,sd=d,cf=cf,h=h,aa=A,ds=ds,dl=dl,dr=dr,da=da,v1=v1,v2=v2,v3=v3,ftrial=F,gsl=x/(2*G*(1+d)),gsr=y/(2*G*(1-d)),gla=(x+2*y)/(2*G*(3-d)),gra=(2*x+y)/(2*G*(3+d)),class_ga=(F-(1+s/3)*x-(1-s/3)*y)/da,class_gs=F/ds)
 q={k:float(v)for k,v in q.items()};branch=0 if q['ftrial']<=0 else 4 if q['class_ga']>=max(q['gla'],q['gra'])else 1 if q['class_gs']<min(q['gsl'],q['gsr'])else 2 if q['gsl']<q['gsr']else 3
 for name in('face','left','right'):q[name+'_gamma']=float(ref['branches'][name]['gamma'])if a.BRANCHES[branch]==name else 0.
 return [q[k]for k in fields],branch
frames=[]
with localcontext()as ctx:
 ctx.prec=220
 for r in rows:
  f=dict(id=r['id'],mode=r['mode'],kind=r['kind'],input_unchanged=True,ok=True,output=[],branch=-1,failure_line=-1,trace=[None]*24)
  family=r['family']
  if family in('nonfinite','invalid-parameter','initial-reject','solver-initial-reject'):
   f['ok']=False
   if family=='solver-initial-reject':f.update(output=[{'value':float.fromhex(v)}for v in r['parent']],iterations=0,substeps=0,rejected=0)
  elif r['mode']=='transaction':
   f.update(ok=False,output=[{'value':0.}for k in range(6)],message='integration failed: synthetic preflight')
   f['transaction']=dict(returned_parent=True,committed_unchanged=True,recovery_ok=True,recovery_matches_fresh=True,committed_state=[0.]*6,recovery_state=[0.]*6,fresh_state=[0.]*6,tentative_ok=False,tentative_changed=True,trial_iterations=1,iterations=1,rejected=1)
  elif family in('initial-valid','initial-unchecked'):
   columns=a.analytic_elastic_directions(r)
   for k,v in enumerate(r['current']):f['output'].append(dict(value=float.fromhex(v),derivatives=[float(col[k])for col in columns]))
  else:
   ref=refs[r['case']];f['trace'],f['branch']=trace(ref);branch=ref['branches'][a.BRANCHES[f['branch']]];assert branch['status']=='defined'
   for k,w in enumerate(branch['returned_atlas']):
    value=D(w)if r['mode']=='solve'else a.hexnumber(r['current'][k])-D(w);o={'value':float(value)}
    if r['kind']=='jet':o['derivatives']=[float(t['residual'][k])for t in branch['directions']]
    f['output'].append(o)
   if r['mode']=='solve':f.update(iterations=2,substeps=1,rejected=0)
  frames.append(f)
result=a.run(frames);(P/'preflight-ideal.json').write_text(json.dumps(result,indent=2)+'\n')
if not result['passed']:print(json.dumps(result['failures'][:10],indent=2));raise SystemExit(1)
probes=[]
def probe(name,mutate):
 f=copy.deepcopy(frames);mutate(f);r=a.run(f);assert not r['passed'],name;probes.append({'name':name,'rejected':True,'failure_count':len(r['failures'])})
i=next(i for i,r in enumerate(rows)if r['id']=='certificate/face/diagonal/jet');mix=next(i for i,r in enumerate(rows)if r['id']=='mixed-scale-middle/extreme/jet');invalid=next(i for i,r in enumerate(rows)if r['family']=='invalid-parameter');transaction=next(i for i,r in enumerate(rows)if r['family']=='solver-rollback')
probe('missing-row',lambda f:f.pop())
probe('wrong-id',lambda f:f[i].update(id='wrong'))
probe('input-mutated',lambda f:f[i].update(input_unchanged=False))
probe('reject-core',lambda f:f[i].update(ok=False,output=[]))
probe('wrong-branch',lambda f:f[i].update(branch=4))
probe('bad-coefficient',lambda f:f[i]['trace'].__setitem__(0,f[i]['trace'][0]*2))
probe('wrong-value',lambda f:f[i]['output'][0].update(value=100.))
probe('missing-direction',lambda f:f[i]['output'][0]['derivatives'].pop())
probe('bad-parent-direction',lambda f:f[i]['output'][0]['derivatives'].__setitem__(6,100.))
probe('bad-last-direction',lambda f:f[i]['output'][0]['derivatives'].__setitem__(37,100.))
probe('current-identity',lambda f:f[i]['output'][0]['derivatives'].__setitem__(0,1.+1e-12))
probe('lost-middle',lambda f:f[mix]['output'][1].update(value=0.))
probe('mixed-spurious-shear',lambda f:f[mix]['output'][3].update(value=1e-200))
probe('nonfinite-output',lambda f:f[i]['output'][0].update(value=float('nan')))
probe('invalid-parameter-success',lambda f:f[invalid].update(ok=True))
probe('scratch-not-discarded',lambda f:f[invalid].update(output=[{'value':0.}]))
probe('committed-state',lambda f:f[transaction]['transaction']['committed_state'].__setitem__(0,1.))
probe('fresh-state',lambda f:f[transaction]['transaction']['fresh_state'].__setitem__(0,1.))
probe('no-tentative-update',lambda f:f[transaction]['transaction'].update(tentative_changed=False))
probe('missing-rejection-work',lambda f:f[transaction]['transaction'].update(rejected=0))
analytic=next(i for i,r in enumerate(rows)if r['family']=='initial-valid')
for j in (6,12,37):probe('initial-elastic-column-'+str(j),lambda f,j=j:f[analytic]['output'][0]['derivatives'].__setitem__(j,100.))
probe('boolean-branch',lambda f:f[i].update(branch=True))
probe('boolean-failure-line',lambda f:f[i].update(failure_line=True))
probe('boolean-iterations',lambda f:f[transaction]['transaction'].update(iterations=True))
# Exercise a permitted finite-gap rejection and reject nearby false witnesses.
supp=next(i for i,r in enumerate(rows)if r['id']=='finite-unresolved/left/jet')
assert frames[supp]['branch']==2
line=next(int(m.group(1))for line in(P/'generated/models.hpp').read_text().splitlines()if '!atlas::finite_value(left_gamma)'in line for m in[__import__('re').search(r'study_failure_line=(\d+)',line)])
finite=copy.deepcopy(frames);finite[supp].update(ok=False,output=[],failure_line=line)
accepted=a.run(finite);assert accepted['passed'],accepted['failures']
for name,mutation in [('missing-gap-failure-site',lambda f:f[supp].update(failure_line=-1)),('unordered-spectrum',lambda f:f[supp]['trace'].__setitem__(12,f[supp]['trace'][13]-1.)),('negative-nonselected-multiplier',lambda f:f[i]['trace'].__setitem__(22,-1.))]:
 f=copy.deepcopy(finite);mutation(f);rr=a.run(f);assert not rr['passed'],name;probes.append({'name':name,'rejected':True,'failure_count':len(rr['failures'])})
solver=next(i for i,r in enumerate(rows)if r['family']=='solver-source')
probe('successful-unsplit-solver-rejected-work',lambda f:f[solver].update(rejected=1))
(P/'preflight-corruptions.json').write_text(json.dumps({'passed':True,'probes':probes,'candidate_calls':0,'compiled_observations':0},indent=2)+'\n')
print(json.dumps({'ideal_passed':True,'corruption_probes':len(probes),'candidate_calls':0,'compiled_observations':0}))

