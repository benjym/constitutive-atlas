"""Bounded Python common-interpreter checks against separate Cartesian oracle.
Run from repository root. No compiled artifact, build, or vendor code execution.
"""
import hashlib,json,math,random,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parents[3]))
from atlas.model import load,interpret,observe
from atlas.initialization import initialize_state
from reference import source_stress,deviatoric_stress_ramp
from make_candidate import candidate_bytes
m=load(D/'candidate.json');assert (D/'candidate.json').read_bytes()==candidate_bytes()
p={k:f['default'] for k,f in m['parameters'].items()}
r=random.Random(36063);n=0;worst=0.
for _ in range(120):
    e=[r.uniform(-.01,.01) for _ in range(6)];v=[r.uniform(-.003,.003) for _ in range(6)];t=r.uniform(-5,5)
    prepared=initialize_state(m,{'eps':e},p,time=t,loading=v)
    assert prepared['initial']==e
    eq=interpret(m,{'eps':e},None,v,p,time=t)['eps'].v
    assert list(eq)==v
    actual=observe(m,{'eps':e},v,p,time=t)['stress'].v
    expected=source_stress(e,v,**p)
    for a,b in zip(actual,expected):
        worst=max(worst,abs(a-b));assert math.isclose(a,b,rel_tol=1e-12,abs_tol=2e-8)
    n+=1
# A state's rate-dependent stress must not be cached as persistent memory.
e=[.002,-.001,-.001,0,0,0];v=[.001,-.0005,-.0005,0,0,0]
a=observe(m,{'eps':e},v,p,time=2)['stress'].v
b=observe(m,{'eps':e},[0]*6,p,time=2)['stress'].v
assert list(a)==[96000.,-48000.,-48000.,0,0,0] and list(b)==[48000.,-24000.,-24000.,0,0,0]
rejected=[]
def reject(name,state={'eps':[0]*6},params=None,loading=[0]*6,time=0.):
    try:initialize_state(m,state,p if params is None else params,loading=loading,time=time)
    except (ValueError,TypeError):rejected.append(name)
    else:raise AssertionError('unexpected accepted '+name)
reject('missing persistent eps',state={})
reject('extra phantom state',state={'eps':[0]*6,'q':[0]*6})
reject('wrong state shape',state={'eps':[0]*5})
reject('nonfinite strain',state={'eps':[math.nan]+[0]*5})
reject('missing clock',time=None)
reject('missing loading',loading=None)
reject('nonfinite clock',time=math.inf)
reject('wrong loading shape',loading=[0]*5)
reject('nonfinite loading',loading=[math.inf]+[0]*5)
for key in p:
    for x in [0.,-1.,math.inf,math.nan]:reject(key+'='+str(x),params={**p,key:x})
reject('omitted parameter',params={'K':p['K'],'G':p['G']})
# Rejections are pure, and recovery uses the same intact valid explicit state.
parent={'eps':e.copy()};before=json.dumps(parent)
reject('failed loading preserves parent',state=parent,loading=[math.nan]+[0]*5)
assert json.dumps(parent)==before
assert initialize_state(m,parent,p,time=2,loading=[0]*6)['initial']==e
result={'identity':'kelvin-voigt-comsol63-common-interpreter-v1','model_sha256':hashlib.sha256((D/'candidate.json').read_bytes()).hexdigest(),'all_passed':True,'random_cartesian_reference_cases':n,'stress_components':6*n,'max_stress_absolute_error_Pa':worst,'initialization_rejections':rejected,'rejection_count':len(rejected),'rate_jump_checked':True,'failed_initialization_recovery_checked':True,'limitations':['Initialization/interpreter only; native and Wasm qualification is parent-owned','Numerical bounds are representation bounds, not a demonstrated parameter envelope']}
out=json.dumps(result,indent=2)+'\n';dest=D/'candidate-check-results.json'
if dest.exists():assert dest.read_text()==out,'retained results differ'
else:dest.write_text(out)
print(out,end='')
