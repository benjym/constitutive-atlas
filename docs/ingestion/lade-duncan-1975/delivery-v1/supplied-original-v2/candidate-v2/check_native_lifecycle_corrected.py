"""Separate corrected campaign; original failed study remains immutable."""
from pathlib import Path
import json,subprocess,hashlib,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
EXE=ROOT/'.local/lade-duncan-candidate-v2/native-build/atlas_lade_gap_candidate'
model=json.loads((HERE/'model.json').read_text());policy=json.loads((HERE/'lifecycle-policy.json').read_text());requests=[];checks=[]; corrected=json.loads((HERE/'lifecycle-corrected-policy.json').read_text())
def call(state,de,params,settings=None):
    cmd=[str(EXE),'--model',model['id'],'--mode','integrate','--initial',','.join(map(str,state)),'--strain',','.join(map(str,de)),'--parameters',','.join(str(params[k]) for k in model['parameters'])]
    if settings:cmd += ['--integration-settings',','.join(map(str,settings))]
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=120);r=json.loads(p.stdout);requests.append({'command':cmd,'returncode':p.returncode,'response':r});return r

def check(name,passed,detail=None):checks.append({'name':name,'passed':bool(passed),'detail':detail})
def level(v):
    x,y,z,xy,yz,zx=v[:6];xy/=math.sqrt(2);yz/=math.sqrt(2);zx/=math.sqrt(2);det=x*y*z+2*xy*yz*zx-x*yz*yz-y*zx*zx-z*xy*xy
    return (x+y+z)**3/det

def H(z,params):return max(params['ft'],level(z)+max(z[6],0))
def rotate(v):
    # Q=[c,-c,0;c,c,0;0,0,1]. Explicit symmetric tensor action in Mandel basis.
    x,y,z,xy,yz,xz=v;s=math.sqrt(2);a=xy/s;b=yz/s;c=xz/s
    return [(x+y)/2-a,(x+y)/2+a,z,(x-y)/s,(b+c),(c-b)]
for label,over in [('dense',{}),('loose',dict(k1=58,ft=33,A=.39,rf=.970,M=6.80e-4,l=1.17,Kur=1600,n=.86))]:
    p={n:f['default'] for n,f in model['parameters'].items()};p.update(over);z=[60000]*3+[0]*3+[p['ft']-27,0];de=policy['general_3d_increment']
    for q in policy['signed_zero_hold_carriers']:
        state=z.copy();state[6]=q;r=call(state,[0]*6,p);check(label+f'_hold_{q}',r.get('ok') and r['state']==state)
    fail=call(z,corrected['forced_failed_increment'],p,corrected['forced_failure_settings']);check(label+'_rollback',not fail.get('ok') and fail.get('state')==z)
    badp=p.copy();badp['Kur']=-1;r=call(z,de,badp);check(label+'_negative_parameter_reject',not r.get('ok'))
    r=call(z,['nan',0,0,0,0,0],p);check(label+'_nonfinite_loading_reject',not r.get('ok'))
    badz=[-1]*3+[0]*3+[p['ft']-27,0];r=call(badz,de,p);check(label+'_negative_parent_reject',not r.get('ok') and r.get('state')==badz)
    direct=call(z,de,p);retry=call(fail.get('state',z),de,p);check(label+'_recovery',direct.get('ok') and retry.get('ok') and direct['state']==retry['state'])
    rr=call(rotate(z[:6])+z[6:],rotate(de),p)
    if direct.get('ok') and rr.get('ok'):
        expect=rotate(direct['state'][:6]);error=max(abs(a-b)/60000 for a,b in zip(expect,rr['state'][:6]));eh=abs(H(direct['state'],p)-H(rr['state'],p));ew=abs(direct['state'][7]-rr['state'][7])/max(1,abs(direct['state'][7]));passed=error<=policy['covariance_max_stress_relative_to_60000_tolerance'] and eh<=policy['covariance_physical_H_absolute_tolerance'] and ew<=policy['covariance_work_relative_using_1Pa_floor_tolerance']
        check(label+'_covariance',passed,{'stress_error':error,'H_error':eh,'wp_error':ew})
    else:check(label+'_covariance',False)
    for i,s in enumerate(policy['near_tie_initial_stresses_Pa']):
        f=level(s);state=s+[max(p['ft']-f,0),0];r=call(state,[1e-5,0,0,0,0,0],p);check(label+f'_near_tie_{i}',r.get('ok'))
    active=[240000,60000,60000,0,0,0,0,0];f=level(active);a=p['M']*p['pa']*(60000/p['pa'])**p['l'];active[7]=a*(f-p['ft'])/(1-p['rf']*(f-p['ft'])/(p['k1']-p['ft']));state=active;states=[]
    for i,inc in enumerate(policy['loading_increments']):
        r=call(state,inc,p);check(label+f'_active_step_{i}',r.get('ok'))
        if not r.get('ok'):break
        check(label+f'_monotonic_H_{i}',H(r['state'],p)+policy['history_monotonic_absolute_tolerance']>=H(state,p));states.append(r['state']);state=r['state']
    replay=active
    for inc in policy['loading_increments']:
        r=call(replay,inc,p)
        if not r.get('ok'):break
        replay=r['state']
    check(label+'_restart_replay',len(states)==len(policy['loading_increments']) and replay==states[-1])
report={'model_sha256':hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((HERE/'lifecycle-corrected-policy.json').read_bytes()).hexdigest(),'requests':requests,'checks':checks,'passed':all(x['passed'] for x in checks)};(HERE/'native-lifecycle-corrected-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':checks},indent=2));raise SystemExit(0 if report['passed'] else 1)
