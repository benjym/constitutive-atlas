#!/usr/bin/env python3
"""Materialize frozen generic API requests; no production imports or execution."""
import hashlib,json,math,struct
from pathlib import Path
D=Path(__file__).resolve().parent; P=D.parent
SHA='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def grid(end,n,checkpoints):return sorted(set([end*i/n for i in range(n+1)]+checkpoints),reverse=end<0)
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)]for i in range(3)]
def rot(v,q):
 s=math.sqrt(2);a=[[v[0],v[3]/s,v[5]/s],[v[3]/s,v[1],v[4]/s],[v[5]/s,v[4]/s,v[2]]]
 a=mm(mm(q,a),list(map(list,zip(*q))))
 return [a[0][0],a[1][1],a[2][2],s*a[0][1],s*a[1][2],s*a[0][2]]
def main():
 mp=P/'manzari-dafalias-1997-constant-m-be-v1.json';assert digest(mp)==SHA
 model=json.loads(mp.read_text());axis=P/'reference-v1/requests.json';inter=P/'reference-v1/interior-lode-v1/requests.json'
 ar=json.loads(axis.read_text());ir=json.loads(inter.read_text());names=list(model['parameters']);defaults=[model['parameters'][n]['default'] for n in names]
 def params(e):
  p=defaults.copy();p[names.index('e0')]=e;return p
 def state(cp):return cp['sigma_Pa']+[cp['e']]+cp['alpha']+[0.]
 cases=[]
 for c in ar['cases']:
  z=c['initial_state']['sigma_Pa']+[c['initial_state']['e']]+c['initial_state']['alpha']+[0.]
  for count in [2048,4096]:
   cs=grid(c['axial_strain_end'],count,[x['axial_strain'] for x in c['checkpoints']])
   cases.append({'id':c['name']+'-'+str(count),'kind':'controls','group':'axis','reference':c['name'],'resolution':count,'parameters':params(c['fixed_e0']),'initial':z,'protocol':1 if c['protocol']=='drained' else 2,'controls':cs,'controls_bits':[struct.pack('>d',x).hex() for x in cs],'checkpoints':c['checkpoints']})
 for c in ir['cases']:
  for count in [2048,4096]:
   ts=grid(.01,count,[x['t'] for x in c['checkpoints']]);n=c['n_mandel']
   cases.append({'id':c['name']+'-'+str(count),'kind':'chain','group':'interior','reference':c['name'],'resolution':count,'parameters':params(c['e0']),'initial':state(c['checkpoints'][0]),'coordinates':ts,'increments':[[n[j]*(b-a) for j in range(6)] for a,b in zip(ts,ts[1:])],'checkpoints':c['checkpoints'],'direction':n})
 base=next(c for c in cases if c['group']=='interior' and c['resolution']==4096)
 replay=json.loads(json.dumps(base));replay.update(id='restart-replay',group='restart',compare_to=base['id'],restart_index=2048);cases.append(replay)
 a,b,c=.29,-.41,.17
 rz=[[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]];ry=[[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]];rx=[[1,0,0],[0,math.cos(c),-math.sin(c)],[0,math.sin(c),math.cos(c)]];q=mm(mm(rz,ry),rx)
 cv=json.loads(json.dumps(base));cv.update(id='tensor-covariance',group='covariance',compare_to=base['id'],rotation=q)
 cv['initial']=rot(base['initial'][:6],q)+[base['initial'][6]]+rot(base['initial'][7:13],q)+[0.];cv['increments']=[rot(v,q) for v in base['increments']];cv['direction']=rot(base['direction'],q)
 for cp in cv['checkpoints']:cp['sigma_Pa']=rot(cp['sigma_Pa'],q);cp['alpha']=rot(cp['alpha'],q);cp['strain']=rot(cp['strain'],q)
 cases.append(cv)
 z=[160000.]*3+[0.]*3+[.65]+[0.]*7
 for protocol in [1,2]:cases.append({'id':'public-default-'+str(protocol),'kind':'run','group':'public','parameters':params(.65),'initial':z,'protocol':protocol,'target':.01,'steps':100})
 for ev in [-.001,.001]:
  cs=grid(ev/3,512,[]);expected_p=(160000**.4+.4*31400000/100000**.6*ev)**(1/.4)
  cases.append({'id':'hydrostatic-'+str(ev),'kind':'controls','group':'hydrostatic','parameters':params(.65),'initial':z,'protocol':4,'controls':cs,'controls_bits':[struct.pack('>d',x).hex() for x in cs],'expected_state':[expected_p]*3+[0.]*3+[.65-1.65*ev]+[0.]*7})
 yieldstrain=next(c for c in ar['cases'] if c['name']=='undrained-dense-compression')['checkpoints'][1]['axial_strain'];amp=yieldstrain/4
 cs=[amp*i/128 for i in range(129)]+[amp*(1-i/128) for i in range(1,129)]
 cases.append({'id':'elastic-quarter-yield-cycle','kind':'controls','group':'elastic-cycle','parameters':params(.65),'initial':z,'protocol':2,'controls':cs,'controls_bits':[struct.pack('>d',x).hex() for x in cs],'expected_state':z})
 special={'parameters':params(.65),'initial':z,'valid_increment':[1e-7,-5e-8,-5e-8,0,0,0],'forced_increment':[.005,-.0025,-.0025,0,0,0],'forced_settings':[2e-10,1e-6,1,0,1,11],'ad_parent_case':base['id'],'ad_parent_coordinate':.0005,'ad_increment':[1e-5*x for x in base['direction']],'fd_step':1e-8}
 plan={'version':'md1997-resolution-study-v4','model':model['id'],'model_sha256':SHA,'parameter_order':names,'settings':[2e-10,1e-6,45,14,20000,11],'source_inputs':{str(mp.relative_to(P)):digest(mp),str(axis.relative_to(P)):digest(axis),str(inter.relative_to(P)):digest(inter)},'cases':cases,'special':special}
 (D/'requests.json').write_text(json.dumps(plan,indent=2,allow_nan=False)+'\n')
 files=[f for f in sorted(D.iterdir()) if f.is_file() and f.name not in ['manifest.json']]
 (D/'manifest.json').write_text(json.dumps({f.name:digest(f) for f in files},indent=2)+'\n')
 print(json.dumps({'prepared':True,'cases':len(cases),'compiled_calls':0,'requests_sha256':digest(D/'requests.json')}))
if __name__=='__main__':main()
