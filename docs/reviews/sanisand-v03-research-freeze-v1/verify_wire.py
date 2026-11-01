"""Reconstruct exact binary64 wire requests from hash-bound independent references."""
from decimal import Decimal as D, localcontext
import gzip
import hashlib
import json


def validate_wire(R, P):
 REF=R/'docs/references/sanisand-project-monotonic-v1'
 for name, expected in json.loads((REF/'manifest.json').read_text())['files'].items():
  assert hashlib.sha256((R/name).read_bytes()).hexdigest() == expected, name
 model=json.loads((P/'model.json').read_text());inputs=json.loads((REF/'inputs.json').read_text());refs=json.loads(gzip.decompress((REF/'reference-p80-t12.json.gz').read_bytes()))
 params=[float(inputs['parameters'][n])for n in model['parameters']];csv=lambda xs:','.join(repr(float(v))for v in xs)
 controls=[float(v)for i in range(6)for v in [0]+[1 if i==j else 0 for j in range(6)]]
 requests=[];maximum_input_rounding=D(0)
 with localcontext()as ctx:
  ctx.prec=85
  for c,ref in zip(inputs['cases'],refs['cases']):
   assert c['id']==ref['id'];v=list(map(D,c['direction_cartesian']));direction=[v[i]for i in[0,4,8]]+[D(2).sqrt()*v[i]for i in[1,5,2]]
   state=list(map(float,ref['samples'][0]['state']))+[0.0]
   for n in [256,512,1024]:
    samples=ref['samples'];times=[D(0),D(samples[1]['parameter'])]
    for left,right in zip(samples[1:-1],samples[2:]):
     a,b=D(left['parameter']),D(right['parameter']);times.extend(a+(b-a)*j/(n//16)for j in range(1,n//16+1))
    assert len(times)==n+2 and all(a<b for a,b in zip(times,times[1:]))
    knots=[]
    for t in times:
     targets=[float(t*x)for x in direction]
     for x,target in zip(direction,targets):maximum_input_rounding=max(maximum_input_rounding,abs(D.from_float(target)-t*x))
     knots.extend([float(t)]+targets)
    args=[model['id'],csv(params),csv(state),'0,0,0,0,0,0',csv(controls),csv(knots),'2e-10,1e-6,45,14,20000,11','1e-10,30,10,20000,1e-7','effective']
    requests.append({'id':c['id']+'/N'+str(n),'case':c['id'],'plastic_steps':n,'function':'atlas_replay_recorded_scope','types':['string']*9,'args':args,'sample_indices':[0,1]+[1+j*n//16 for j in range(1,17)],'knots_count':n+2})
 actual=json.loads(gzip.decompress((P/'trajectory-requests.json.gz').read_bytes()))
 assert actual == requests, 'wire reconstruction mismatch'
 assert str(maximum_input_rounding) == json.loads((P/'wire-summary.json').read_text())['maximum_absolute_strain_rounding']
 return len(requests)
