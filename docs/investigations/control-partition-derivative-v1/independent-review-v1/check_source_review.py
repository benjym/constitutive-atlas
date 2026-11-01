import contextlib,hashlib,io,json,math,runpy
from decimal import Decimal,localcontext
from pathlib import Path
D=Path(__file__).resolve().parent;S=D.parent/'implementation-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
check('assigned exact manifest',h(S/'manifest.json')=='d22a68514ea2eb376aa2c406cf67a468a7a865893db71ff795efe1f16c3407dc')
check('assigned source receipt',h(S/'source-freeze.json')=='4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8')
stream=io.StringIO()
with contextlib.redirect_stdout(stream):runpy.run_path(str(S/'check_source.py'),run_name='__main__')
r=json.loads(stream.getvalue());(D/'reproduced-source-checks.json').write_text(json.dumps(r,indent=2)+'\n');check('582 files/three edits/protocol3 checked',r['source_files']==582 and r['changed']==['cpp/include/atlas/solver.hpp'] and r['protocol3_and_downstream']=='byte-identical')
f=json.loads((S/'source-freeze.json').read_text());check('assigned solver bytes',h(Path(f['source_directory'])/'cpp/include/atlas/solver.hpp')=='05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218')
with localcontext() as ctx:
 ctx.prec=60;E=Decimal(30000000);nu=Decimal('.25');axial=Decimal('.001');G=E/(2*(1+nu));K=E/(3*(1-2*nu));lam=K-2*G/3;derivative=2*G+2*lam;lateral=-lam*axial/derivative;vol=axial+2*lateral;stress=Decimal(100000)+2*G*axial+lam*vol;void=Decimal('.7')-Decimal('1.7')*vol
 check('independent Decimal48MPa slope',derivative==Decimal(48000000));check('independent root/fullstate',lateral==Decimal('-.00025') and stress==130000 and void==Decimal('.69915'))
# Independent bounded decision logic: compare distinct amplitude candidates and reset on invalid metadata.
def select(sequence):
 previous=None
 for k,(valid,slope) in enumerate(sequence):
  if valid and previous is not None and abs(slope-previous)<=.001*max(1,abs(slope),abs(previous)):return True,k
  previous=slope if valid else None
 return False,None
check('jump requires recoverypair at h/2 andh/4',select([(False,0),(True,78e6),(True,78e6)])==(True,2))
check('invalid resets consecutivepair',select([(True,78e6),(False,0),(True,78e6),(True,78e6)])==(True,3))
check('stable negative andzero allowed',select([(True,-78e6),(True,-78e6)])==(True,1) and select([(True,0),(True,0)])==(True,1))
check('partition unavailable/unstable boundedfailure',select([(False,0)]*11)==(False,None) and select([(True,78e6 if k%2 else 156e6) for k in range(11)])==(False,None))
(D/'source-review-checks.json').write_text(json.dumps({'compiled_calls':0,'source_decision':'prospectively sound bounded change; checker integrity blocked separately','checks':checks},indent=2)+'\n')
