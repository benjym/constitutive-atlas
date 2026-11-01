import runpy,json,subprocess,tempfile,copy,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parents[1]/'parity-v1'
ns=runpy.run_path(str(D/'check_synthetic.py'));base=ns['report'];inter=ns['inter'];tests=[]
def run(name,mutate,expected):
 a=copy.deepcopy(base);b=copy.deepcopy(base);a['identity']['backend']='native';b['identity']['backend']='wasm';mutate(a,b)
 with tempfile.TemporaryDirectory(dir=D) as td:
  td=Path(td);ap=td/'SYNTHETIC-native.json';bp=td/'SYNTHETIC-wasm.json';out=td/'checks.json'
  ap.write_text(json.dumps(a));bp.write_text(json.dumps(b))
  p=subprocess.run(['python3','-B',str(P/'check.py'),str(ap),str(bp),'--output',str(out)],capture_output=True,text=True)
  r=json.loads(out.read_text()) if out.exists() else None;passed=bool(r and r['passed'])
  tests.append({'test':name,'expected':expected,'checker_accepted':passed,'expectation_met':expected==passed,'exit_code':p.returncode,'failed_checks':r['failures'] if r else None})
run('identical synthetic ideal',lambda a,b:None,True)
run('different full state',lambda a,b:b['cases'][inter]['points'][1]['state'].__setitem__(7,3.),False)
run('duplicate native backend',lambda a,b:b['identity'].__setitem__('backend','native'),False)
run('different intermediate coordinates',lambda a,b:b['cases'][inter]['points'][1].__setitem__('coordinate',-99),False)
def same_wrong(a,b):
 for x in [a,b]:x['cases'][inter]['points'][1]['coordinate']=-99
run('identical wrong intermediate coordinates',same_wrong,False)
def samewrongreceipt(a,b):
 for x in [a,b]:x['cases']['restart-replay']['restart_receipt']={'index':-1,'all_persistent_state':[]}
run('identical corrupt restart receipt',samewrongreceipt,False)
(D/'parity-checks.json').write_text(json.dumps({'scope':'synthetic comparator checks only','checker_sha256':hashlib.sha256((P/'check.py').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((P/'POLICY.md').read_bytes()).hexdigest(),'tests':tests},indent=2)+'\n')
print(json.dumps(tests,indent=2))
