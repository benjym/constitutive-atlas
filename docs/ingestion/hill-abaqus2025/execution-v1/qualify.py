"""Prospective corpus, independent Decimal references and saved native/Wasm assessor."""
import importlib.util,json,hashlib,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('hill_oracle',BASE.parent/'source-v1/check_algebra.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
MODEL='hill-abaqus2025-perfect-be'
SETTINGS='1e-11,1e-6,60,0,1,20'
KEYS=['p_ref','K','Gmod','sigma_y','F','Gh','Hh','L','M','N']
DEFAULT=[1e5,20e6,12e6,60000,.7,.5,.3,1.2,1.7,2]
def freeze():
 cases=[]
 def add(name,path,p=DEFAULT,initial=None):
  initial=initial or [0]*7;z=initial[:6];refs=[]
  for de in path:
   row=o.endpoint(dict(zip(KEYS,p)),z,de);refs.append([float(x) for x in row]);z=row[:6]
  cases.append(dict(id=name,parameters=p,initial=initial,increments=path,expected=refs))
 add('zero',[[0]*6]);add('hydrostatic',[[.002,.002,.002,0,0,0],[-.002,-.002,-.002,0,0,0]])
 for i in range(6):
  for sign in [-1,1]:
   e=[0]*6;e[i]=sign*1e-5;add(f'elastic-{i}-{sign}',[e])
   e=[0]*6;e[i]=sign*.005;add(f'plastic-{i}-{sign}',[e])
 add('mixed-nonproportional',[[.003,-.001,-.002,.002,-.001,.001],[0,0,0,-.003,.002,-.001],[-.002,.001,.001,.001,0,-.002],[0]*6])
 add('public-preset',[[.003,-.0015,-.0015,0,0,0],[-.003,.0015,.0015,0,0,0],[0]*6])
 add('hydrostatic-shift',[[.003,-.001,-.002,.002,-.001,.001]],initial=[30000,30000,30000,0,0,0,0])
 for p in [DEFAULT[:4]+[.5,.5,.5,1.5,1.5,1.5],DEFAULT[:4]+[1.1,.9,.4,.8,2.1,1.3]]:
  add('coefficient-variant-'+str(p[4]),[[.005,-.002,-.003,.002,-.003,.001],[-.004,.001,.003,-.003,.001,.001],[0]*6],p)
 data=dict(model=MODEL,settings=SETTINGS,model_sha256=hashlib.sha256((Path(__file__).resolve().parents[4]/'models/research/hill'/f'{MODEL}.json').read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256(Path(o.__file__).read_bytes()).hexdigest(),cases=cases)
 (BASE/'references.json').write_text(json.dumps(data,indent=2)+'\n');print(len(cases),'cases',sum(len(c['increments']) for c in cases),'increments frozen')
def assess(raw):
 refs=json.loads((BASE/'references.json').read_text());assert len(raw)==len(refs['cases']);worst=[0.,0.];calls=0
 for c,r in zip(refs['cases'],raw):
  assert c['id']==r['id'];assert r['runs'][0]==r['runs'][1]
  for rows in r['runs']:
   assert len(rows)==len(c['expected'])
   z=c['initial']
   for de,ref,row in zip(c['increments'],c['expected'],rows):
    assert row['ok'],(c['id'],row)
    assert row['initial']==z and row['parameters']==c['parameters'] and row['strain']==de
    assert len(row['state'])==7
    for i,(a,b) in enumerate(zip(row['state'],ref)):
     err=abs(a-b);limit=(.01+1e-10*abs(b)) if i<6 else 1e-9
     assert err<=limit,(c['id'],i,a,b,err,limit);worst[i==6]=max(worst[i==6],err)
    z=row['state'];calls+=1
 return dict(passed=True,calls=calls,max_stress_error_Pa=worst[0],max_multiplier_error=worst[1])
def run(solver):
 refs=json.loads((BASE/'references.json').read_text());raw=[]
 for c in refs['cases']:
  runs=[]
  for _ in range(2):
   z=c['initial'];rows=[]
   for de in c['increments']:
    csv=lambda x:','.join(format(v,'.17g') for v in x)
    cmd=[solver,'--mode','integrate','--model',MODEL,'--parameters',csv(c['parameters']),'--initial',csv(z),'--strain',csv(de),'--integration-settings',SETTINGS]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);row=json.loads(p.stdout);rows.append(row)
    if not row['ok']:break
    z=row['state']
   runs.append(rows)
  raw.append(dict(id=c['id'],runs=runs));(BASE/'native-raw.json').write_text(json.dumps(raw,indent=2)+'\n')
 report=assess(raw);(BASE/'native-assessment.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':
 if sys.argv[1]=='freeze':freeze()
 elif sys.argv[1]=='native':run(sys.argv[2])
 else:print(assess(json.loads(Path(sys.argv[2]).read_text())))
