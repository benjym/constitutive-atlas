"""Independent Python-only review of retained lifecycle evidence; no native calls.

Correct Cartesian tensor determinant, source hydrostatic integration and
log-domain scalar backward-Euler roots. Diagnostic, not revised acceptance.
"""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,math,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[7]))
from atlas.model import load,evaluation_environment,interpret,prepare_increment
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
model=load(BASE/'model.json'); report=json.loads((BASE/'native-lifecycle-results.json').read_text()); policy=json.loads((BASE/'lifecycle-policy.json').read_text())
assert sha(BASE/'model.json')==report['model_sha256']
assert sha(BASE/'lifecycle-policy.json')==report['policy_sha256']
assert len(report['checks'])==32 and sum(not c['passed'] for c in report['checks'])==4 and not report['passed']
manifest=json.loads((BASE/'native-source-manifest.json').read_text());assert all(sha(v['path'])==v['sha256'] for v in manifest['files'])

def parameters(row):
    cmd=row['command']; return dict(zip(model['parameters'],map(float,cmd[cmd.index('--parameters')+1].split(','))))
def initial(row):
    c=row['command'];return list(map(float,c[c.index('--initial')+1].split(',')))
def as_state(z):return {'sigma':z[:6],'q':z[6],'wp':z[7]}
def tensor(v):
    x,y,z,xy,yz,xz=v[:6];r=math.sqrt(2)
    return [[x,xy/r,xz/r],[xy/r,y,yz/r],[xz/r,yz/r,z]]
def det(m):
    return sum(m[0][j]*(m[1][(j+1)%3]*m[2][(j+2)%3]-m[1][(j+2)%3]*m[2][(j+1)%3]) for j in range(3))
def corrected_H(z,p):
    m=tensor(z);t=sum(m[i][i] for i in range(3));return max(p['ft'],t**3/det(m)+max(z[6],0))
def rotate(v):
    # Derive Q*S*Q^T independently by matrix multiplication and encode Mandel.
    c=math.sqrt(.5);r=[[c,-c,0],[c,c,0],[0,0,1]];s=tensor(v)
    out=[[sum(r[i][k]*s[k][l]*r[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    root=math.sqrt(2)
    return [out[0][0],out[1][1],out[2][2],root*out[0][1],root*out[1][2],root*out[0][2]]

def logadd(a,b):
    top=max(a,b);return top+math.log1p(math.exp(-abs(a-b)))
def be_step_log(xprev,length,K,n):
    # u=p/pa; u + length*K*u^n = u_prev has exactly one positive root.
    loglk=math.log(length*K)
    def residual(x):return logadd(x-xprev,loglk+n*x-xprev)
    hi=xprev;lo=min(xprev-1,(xprev-loglk-math.log(2))/n)
    while residual(lo)>0:lo-=max(1,abs(lo))
    for _ in range(120):
        mid=(lo+hi)/2
        if residual(mid)>0:hi=mid
        else:lo=mid
    return (lo+hi)/2

cov=[];unload=[]
# Identify calls from actual command contents rather than hardcoded row numbers.
for start,label in [(0,'dense'),(len(report['requests'])//2,'loose')]:
    rows=report['requests'][start:start+len(report['requests'])//2]
    p=parameters(rows[0]);general=','.join(map(str,policy['general_3d_increment']))
    # Calls occur direct then retry then rotated, as frozen runner establishes.
    direct=rows[5]['response'];rotated=rows[7]['response'];assert direct['ok'] and rotated['ok']
    zd,zr=direct['state'],rotated['state'];hd,hr=corrected_H(zd,p),corrected_H(zr,p)
    model_hd=evaluation_environment(model,as_state(zd),as_state(zd),[0]*6,p)['H']
    model_hr=evaluation_environment(model,as_state(zr),as_state(zr),[0]*6,p)['H']
    stress_err=max(abs(a-b)/60000 for a,b in zip(rotate(zd[:6]),zr[:6]))
    h_error=abs(hd-hr);werr=abs(zd[7]-zr[7])/max(1,abs(zd[7]))
    assert h_error<=policy['covariance_physical_H_absolute_tolerance']
    assert abs(model_hd-model_hr)<=policy['covariance_physical_H_absolute_tolerance']
    cov.append({'set':label,'correct_matrix_H_direct':hd,'correct_matrix_H_rotated':hr,'correct_H_error':h_error,
       'model_H_error':abs(model_hd-model_hr),'matrix_vs_model_H_direct_difference':abs(hd-model_hd),
       'correct_matrix_stress_covariance_error':stress_err,'work_error':werr,
       'original_check':next(c for c in report['checks'] if c['name']==label+'_covariance'),
       'disposition':'Original checker used raw Mandel shears as Cartesian shears; corrected retained-response diagnostic satisfies original numerical covariance bounds. Original study remains failed.'})
    request=rows[4];response=request['response'];z0=initial(request);sigma0=z0[0];de=list(map(float,request['command'][request['command'].index('--strain')+1].split(',')));assert de==[-2,-2,-2,0,0,0]
    # ν_i=0, hydrostatic f27, no plastic strain: d(p/pa)/dε=K*(p/pa)^n.
    u0=sigma0/p['pa'];critical=-u0**(1-p['n'])/((1-p['n'])*p['Kur'])
    fractions=response['diagnostics']['increment_fractions']
    fraction_sum=sum(Q.from_float(v) for v in fractions)
    record={'set':label,'native_ok':response['ok'],'continuous_zero_pressure_strain_per_axis':critical,
        'requested_per_axis_strain':de[0],'request_beyond_positive_continuous_path':de[0]<critical,
        'input_is_finite':all(math.isfinite(v) for v in de),'native_state':response['state'],
        'accepted_substeps':response['diagnostics']['substeps'],'accepted_fraction_sum_exact':str(fraction_sum),
        'small_strain_amplitude_qualification':'200percent extension is outside the demonstrated infinitesimal test regime; finite descriptor alone supplies no amplitude bound.'}
    if response['ok']:
        assert fraction_sum==1
        state=as_state(response['state']);env=evaluation_environment(model,state,state,[0]*6,p)
        held=interpret(model,state,state,[0]*6,p);prepared=prepare_increment(model,state,[0]*6,p)
        assert prepared==state
        hold_norm=max(abs(v)/(p['pa'] if name in ('sigma','wp') else p['ft']) for name,x in held.items() for v in (x.v if hasattr(x,'v') else [x]))
        # Scalar exact BE replay of the accepted subdivision, unlike a misleading
        # comparison of final state with one unsplit full-increment residual.
        xp=math.log(u0); first_log=None
        for i,fraction in enumerate(fractions):
            xp=be_step_log(xp,abs(de[0])*fraction,p['Kur'],p['n'])
            if i==0:first_log=xp
        record.update({'final_model_min_pressure_Pa':env['smin']*p['pa'],'final_model_f':env['f'],'final_decoded_H':env['H'],
           'final_E_Pa':env['E'],'zero_reentry_preparation':'accepted unchanged','zero_hold_residual_scaled_norm':hold_norm,
           'first_accepted_subincrement_per_axis':de[0]*fractions[0],
           'first_BE_pressure_Pa':p['pa']*math.exp(first_log),
           'scalar_exact_BE_partition_final_log10_pressure_Pa':(math.log(p['pa'])+xp)/math.log(10),
           'native_final_log10_pressure_Pa':math.log10(response['state'][0]),
           'residual_stress_absolute_scale_Pa':p['pa']*2e-10,
           'partition_replay_limit':'Scalar log-domain endpoint-root diagnostic; not compiled replay, and not an oracle for individual native residual termination states.'})
    else:
        assert response['state']==z0
        record['rollback_exact']=True
    unload.append(record)
triax=json.loads((BASE/'native-triaxial-results.json').read_text());assert triax['passed'] and len(triax['requests'])==24 and all(r['ok'] for r in triax['requests'])
refs=json.loads((BASE/'triaxial-reference-results.json').read_text());assert refs['passed'] and len(refs['cases'])==8
result={'id':'REVIEW-lade-duncan-lifecycle-v2-python-diagnostic','model_sha256':sha(BASE/'model.json'),
 'original_lifecycle':{'checks':32,'failures':4,'passed':False,'failed_names':[c['name'] for c in report['checks'] if not c['passed']]},
 'native_snapshot_hashes':'all '+str(len(manifest['files']))+' match','native_triaxial':'24/24 successful; retained frozen study passes','independent_reference':'8/8 retained convergence checks pass',
 'corrected_covariance_diagnostics':cov,'hydrostatic_unloading_diagnostics':unload,
 'disposition':'Two covariance oracle defects; finite minus2 increment has no declared schema-invalid amplitude premise, making rollback/retry expectations unsupported. Large-unloading response nonetheless does not establish positive-domain differential source fidelity; source-derived zero-pressure event and residual-scale/partition behavior need separately frozen qualification. Original lifecycle remains failed.',
 'limits':['No native/compiled execution','No root files rewritten','No revised acceptance result','No E5/model approval']}
if __name__=='__main__':
    (HERE/'diagnostic-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
