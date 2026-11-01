"""Frozen v4 hydrostatic/proportional domain and transaction campaign."""
from pathlib import Path
import hashlib,json,math,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
EXE=ROOT/'.local/lade-midpoint-control-v1/native-build/atlas_lade_domain_candidate'
RAW=ROOT/'.local/lade-midpoint-control-v1/native-domain-requests';RAW.mkdir(exist_ok=True)
model=json.loads((HERE/'model.json').read_text());policy=json.loads((HERE/'POLICY.json').read_text());requests=[];checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
def call(state,de,p,settings):
    command=[str(EXE),'--model',model['id'],'--mode','integrate','--parameters',','.join(str(p[k]) for k in model['parameters']),'--initial',','.join(map(str,state)),'--strain',','.join(map(str,de)),'--integration-settings',','.join(map(str,settings))]
    proc=subprocess.run(command,text=True,capture_output=True,timeout=120);r=json.loads(proc.stdout)
    path=RAW/f'{len(requests):04}.json';path.write_text(proc.stdout)
    requests.append({'command':command,'returncode':proc.returncode,'raw_path':str(path.relative_to(ROOT)),'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ok':r.get('ok'),'message':r.get('message'),'state':r.get('state'),'substeps':r.get('diagnostics',{}).get('substeps'),'reserved_trials':r.get('diagnostics',{}).get('reserved_path_trials')})
    return r
def level(v):
    x,y,z,a,b,c=v[:6];a/=math.sqrt(2);b/=math.sqrt(2);c/=math.sqrt(2)
    return (x+y+z)**3/(x*y*z+2*a*b*c-x*b*b-y*c*c-z*a*a)
def rotate(v):
    # Product of z/y rotations, applied independently in Cartesian components.
    a=.37;b=.61;ca=math.cos(a);sa=math.sin(a);cb=math.cos(b);sb=math.sin(b)
    Q=[[ca*cb,-sa,ca*sb],[sa*cb,ca,sa*sb],[-sb,0,cb]]
    x,y,z,xy,yz,zx=v;r=math.sqrt(2);S=[[x,xy/r,zx/r],[xy/r,y,yz/r],[zx/r,yz/r,z]]
    T=[[sum(Q[i][k]*S[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return [T[0][0],T[1][1],T[2][2],r*T[0][1],r*T[1][2],r*T[2][0]]
base_settings=policy['numerics']['default_study_settings'];gate=policy['gates'];rows=[]
for label,over in [('dense',{}),('loose',dict(k1=58,ft=33,A=.39,rf=.970,M=6.80e-4,l=1.17,Kur=1600,n=.86))]:
    p={k:v['default'] for k,v in model['parameters'].items()};p.update(over)
    def state(p0,B=None):
        stress=[p0]*3+[0]*3 if B is None else [p0*x for x in B]
        return stress+[p['ft']-level(stress),0]
    def critical(p0):return -(p0/p['pa'])**(1-p['n'])/((1-p['n'])*p['Kur'])
    for frac in gate['hydro_interior_fractions']:
        errors=[]
        for tol in gate['interior_refinement_tolerances']:
            setting=base_settings.copy();setting[6]=tol;parent=state(60000);ec=critical(60000);r=call(parent,[ec*frac]*3+[0]*3,p,setting)
            ref=60000*(1-frac)**(1/(1-p['n']));err=abs(r['state'][0]-ref)/ref if r.get('ok') else math.inf;errors.append(err)
            check(f'{label}_interior_{frac}_{tol}',r.get('ok') and r['state'][7]==0,{'pressure_relative_error':err})
        check(f'{label}_interior_refinement_{frac}',all(b<=a for a,b in zip(errors,errors[1:])),errors)
        if str(frac) in gate['hydro_finest_pressure_relative_bounds']:check(f'{label}_interior_bound_{frac}',errors[-1]<=gate['hydro_finest_pressure_relative_bounds'][str(frac)],errors[-1])
    for frac in gate['hydro_cross_fractions']:
        for count in gate['cross_external_partitions']:
            z=state(60000);ec=critical(60000);failed=False;rollback=False
            for _ in range(count):
                parent=z.copy();r=call(parent,[ec*frac/count]*3+[0]*3,p,base_settings)
                if not r.get('ok'):failed=True;rollback=r.get('state')==parent;break
                z=r['state']
            check(f'{label}_cross_{frac}_{count}',failed and rollback,{'failed':failed,'rollback_exact':rollback})
    for p0 in gate['tiny_pressure_Pa']:
        ec=critical(p0);parent=state(p0)
        for frac in [.5,1.25]:
            r=call(parent,[ec*frac]*3+[0]*3,p,base_settings)
            if frac<1:tiny_direct=r
            else:
                retry=call(r.get('state',parent),[ec*.5]*3+[0]*3,p,base_settings)
                check(f'{label}_tiny_recovery_{p0}',tiny_direct.get('ok') and retry.get('ok') and tiny_direct['state']==retry['state'])
            ok=r.get('ok') and r['state'][0]<p0 and r['state'][0]>0 if frac<1 else not r.get('ok') and r.get('state')==parent
            check(f'{label}_tiny_{p0}_{frac}',ok,{'ok':r.get('ok'),'pressure':r.get('state',[None])[0]})
        hold=call(parent,[0]*6,p,base_settings);check(f'{label}_tiny_hold_{p0}',hold.get('ok') and hold['state']==parent)
    # Source-consistent proportional anisotropic stress path: f is constant.
    B=rotate([1.1,1.,.9,0,0,0]);parent=state(60000,B)
    ec=critical(60000)*(.9**(-p['n']))
    for frac in [.5,1.001,1.25]:
        r=call(parent,[ec*frac*x for x in B],p,base_settings)
        if frac<1:
            ref=[x*(1-frac)**(1/(1-p['n'])) for x in parent[:6]]
            error=math.sqrt(sum((a-b)**2 for a,b in zip(r.get('state',[math.inf]*6)[:6],ref)))/math.sqrt(sum(x*x for x in ref))
            ok=r.get('ok') and error<=gate['hydro_finest_pressure_relative_bounds']['0.5']
        else:error=None;ok=not r.get('ok') and r.get('state')==parent
        check(f'{label}_rotated_proportional_{frac}',ok,{'error':error,'ok':r.get('ok')})
    parent=state(60000);r=call(parent,[-2]*3+[0]*3,p,base_settings)
    check(f'{label}_original_extreme_reject',not r.get('ok') and r.get('state')==parent)
    de=[1e-5,0,0,0,0,0];direct=call(parent,de,p,base_settings);retry=call(r.get('state',parent),de,p,base_settings)
    check(f'{label}_extreme_recovery',direct.get('ok') and retry.get('ok') and direct['state']==retry['state'])
report={'id':'lade1975-midpoint-elastic-native-domain-v4','model_sha256':hashlib.sha256((HERE/'model.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((HERE/'POLICY.json').read_bytes()).hexdigest(),'exe_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),'requests':requests,'checks':checks,'passed':all(c['passed'] for c in checks),'limitations':'Bounded finite-precision qualification and source scalar proof; no rigorous general3D event guarantee or E5 acceptance.'}
(HERE/'native-domain-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'requests':len(requests),'checks':len(checks),'failures':[c for c in checks if not c['passed']]},indent=2));raise SystemExit(0 if report['passed'] else 1)
