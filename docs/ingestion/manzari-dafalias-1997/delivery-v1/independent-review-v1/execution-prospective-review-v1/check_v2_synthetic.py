import runpy,json,subprocess,tempfile,copy,hashlib,math
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;P=D.parents[1]/'parity-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'manifest.json')=='1b02e0a416b75a737d744226a934080bfe230415a8b12298c43e4543502a1702'
for file,h in json.loads((P/'manifest.json').read_text()).items():assert sha(P/file)==h
ns=runpy.run_path(str(D/'check_synthetic.py'));base=ns['report'];inter=ns['inter'];tests=[]
refs=json.loads((D.parents[1]/'reference-v1/interior-lode-v1/reference-results.json').read_text())
c=next(iter(refs['cases'].values()));cp=c['checkpoints'][1];lz=cp['sigma_Pa']+[cp['e']]+cp['alpha']+[1e-5]
for name in ['linearize']+[f'fd-{j}-{sign}' for j in range(6) for sign in [-1,1]]:base['special'][name]['state']=lz.copy()
def run(name,mutate,expected):
 a=copy.deepcopy(base);b=copy.deepcopy(base);a['identity']['backend']='native';b['identity']['backend']='wasm';mutate(a,b)
 with tempfile.TemporaryDirectory(dir=D) as td:
  td=Path(td);ap=td/'SYNTHETIC-native.json';bp=td/'SYNTHETIC-wasm.json';out=td/'checks.json';ap.write_text(json.dumps(a));bp.write_text(json.dumps(b))
  p=subprocess.run(['python3','-B',str(P/'check.py'),str(ap),str(bp),'--output',str(out)],capture_output=True,text=True)
  r=json.loads(out.read_text()) if out.exists() else None;passed=bool(r and r['passed'])
  tests.append({'test':name,'expected':expected,'checker_accepted':passed,'expectation_met':expected==passed,'exit_code':p.returncode,'failed_checks':r['failures'] if r else None})
run('synthetic ideal',lambda a,b:None,True)
def badcoord(a,b):
 for x in [a,b]:x['cases'][inter]['points'][1]['coordinate']=-99
run('identical wrong coordinate',badcoord,False)
def badreceipt(a,b):
 for x in [a,b]:x['cases']['restart-replay']['restart_receipt']={'index':-1,'all_persistent_state':[]}
run('identical corrupt restart receipt',badreceipt,False)
def badpart(a,b):
 for x in [a,b]:
  for name in ['linearize']+[f'fd-{j}-{sign}' for j in range(6) for sign in [-1,1]]:x['special'][name]['diagnostics']['increment_fractions']=[]
run('identical empty partitions',badpart,False)
branch=runpy.run_path(str(P/'check.py'))['branch'];n=c['n_mandel'];S=math.sqrt(2/3);s=math.sqrt(2)
correct=np.array([[n[0],n[3]/s,n[5]/s],[n[3]/s,n[1],n[4]/s],[n[5]/s,n[4]/s,n[2]]])
wrong=np.array([[n[0],n[5]/s,n[4]/s],[n[5]/s,n[1],n[3]/s],[n[4]/s,n[3]/s,n[2]]])
ca=math.sqrt(6)*float(np.trace(correct@correct@correct));cw=math.sqrt(6)*float(np.trace(wrong@wrong@wrong));psi=-.15
image=lambda cosine:S*(1.14+2*(3.975)/(3.975+2-(3.975-2)*cosine)*max(-psi,0)-.05)
# Above coefficient is g(kbe/kbc)*kbc, with kbe=2.
image=lambda cosine:S*(1.14+(4*3.975/(3.975+2-(3.975-2)*cosine))*max(-psi,0)-.05)
ba=image(ca);bw=image(cw);beta=(ba+bw)/2
alpha=[beta*x for x in n];sig=[160000*((1 if i<3 else 0)+(beta+S*.05)*v) for i,v in enumerate(n)];state=sig+[.65]+alpha+[1e-5]
actual=branch(state,ns['p']['special']['parameters']);expected_bn=ba-beta;wrong_bn=bw-beta
witness={'correct_cos3theta':ca,'implemented_cos3theta':cw,'correct_bn':expected_bn,'implemented_bn':wrong_bn,'expected_signature':[False,expected_bn>0,None],'observed_signature':actual,'state':state}
assert actual is not None and actual[1] != (expected_bn>0),witness
(D/'v2-checks.json').write_text(json.dumps({'scope':'synthetic-only prospective parity-v2 review','manifest_sha256':sha(P/'manifest.json'),'tests':tests,'wrong_Mandel_branch_witness':witness},indent=2)+'\n')
print(json.dumps({'tests':tests,'wrong_Mandel_branch_witness':witness},indent=2))
