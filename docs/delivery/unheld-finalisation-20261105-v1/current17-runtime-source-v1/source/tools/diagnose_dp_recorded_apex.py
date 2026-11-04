#!/usr/bin/env python3
"""Read retained responses; reconstruct independent constant-elasticity DP returns.
No DSL evaluation, material solver calls, native execution or repository writes.
"""
import argparse,gzip,hashlib,json,math
from pathlib import Path

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def scalar_return(parent,de,K,G,M,Md,c):
    p0=sum(parent[:3])/3; volume=sum(de[:3]); pt=p0+K*volume
    st=[parent[i]-(p0 if i<3 else 0)+2*G*(de[i]-(volume/3 if i<3 else 0)) for i in range(6)]
    qt=math.sqrt(1.5*sum(v*v for v in st)); ft=qt-M*pt-c
    threshold=qt/(3*G); gs=ft/(3*G+M*K*Md); apex=-c/M
    if ft<=0:
        branch='elastic'; gamma=0.; stress=[pt+st[i] if i<3 else st[i] for i in range(6)]
    elif gs<threshold:
        branch='smooth';gamma=gs;factor=1-3*G*gamma/qt
        stress=[pt+K*Md*gamma+factor*st[i] if i<3 else factor*st[i] for i in range(6)]
    else:
        if Md<=0: raise ValueError('No volumetric apex correction for Md<=0')
        branch='apex';gamma=(apex-pt)/(K*Md)
        # Exact algebraic apex output avoids cancellation in p_t+K*Md*gamma.
        stress=[apex]*3+[0.]*3
    return dict(branch=branch,stress=stress,gamma=gamma,p_trial=pt,q_trial=qt,
                trial_yield=ft,smooth_gamma=gs,apex_gamma_threshold=threshold,
                smooth_gamma_minus_threshold=gs-threshold,
                apex_pressure=apex,
                apex_pressure_margin=apex-(pt+K*Md*threshold))

def analyse(repo):
    report=repo/'catalogue/investigations/recorded-refinement-v1/plastic-report.json.gz'
    model=repo/'models/drucker-prager.json'
    raw=json.loads(gzip.decompress(report.read_bytes()));case=next(c for c in raw['cases'] if c['model']=='drucker-prager')
    records=[]
    for level in case['levels']:
        response=level['response']
        if response['ok']: continue
        parent=response['points'][-1];params=response['parameters'];pref,E,nu,M,Md,c=params
        K=E/(3*(1-2*nu));G=E/(2*(1+nu));de=response['last_trial_increment']
        result=scalar_return(parent['state'],de,K,G,M,Md,c)
        scale=max(1.,pref,*[abs(v) for v in response['initial'][:6]])
        residual=[(result['stress'][i]-response['knots_wire'][response['failed_knot']*7+1+i])/scale for i in (1,2)]
        h=response['control_settings']['finite_difference_step'];columns=[]
        for j in (1,2):
            plus=list(de);minus=list(de);plus[j]+=h;minus[j]-=h
            rp=scalar_return(parent['state'],plus,K,G,M,Md,c);rm=scalar_return(parent['state'],minus,K,G,M,Md,c)
            columns.append(dict(component=j,h=h,plus_branch=rp['branch'],minus_branch=rm['branch'],
                                normalized_stress_derivative=[(rp['stress'][i]-rm['stress'][i])/(2*h*scale) for i in (1,2)],
                                plus_apex_margin=rp['apex_pressure_margin'],minus_apex_margin=rm['apex_pressure_margin']))
        elastic_de=list(de);elastic_de[1]=elastic_de[2]=-nu*de[0]
        elastic_seed=scalar_return(parent['state'],elastic_de,K,G,M,Md,c)
        # Axisymmetric scalar root is a diagnostic, not a proposed generic driver.
        target=response['knots_wire'][response['failed_knot']*7+2]
        low=0.;high=max(abs(de[0]),.001)
        assert scalar_return(parent['state'],[de[0],low,low,0,0,0],K,G,M,Md,c)['stress'][1]<target
        assert scalar_return(parent['state'],[de[0],high,high,0,0,0],K,G,M,Md,c)['stress'][1]>target
        for _ in range(100):
            mid=(low+high)/2
            if scalar_return(parent['state'],[de[0],mid,mid,0,0,0],K,G,M,Md,c)['stress'][1]<target:low=mid
            else:high=mid
        radial=(low+high)/2;root_de=[de[0],radial,radial,0,0,0];root=scalar_return(parent['state'],root_de,K,G,M,Md,c)
        assert result['branch']=='apex' and result['apex_pressure_margin']>0
        assert abs(max(abs(v) for v in residual)-response['last_control_error'])<1e-11
        assert all(col['plus_branch']==col['minus_branch']=='apex' and col['normalized_stress_derivative']==[0.,0.] for col in columns)
        assert elastic_seed['branch']!='apex'
        records.append(dict(factor=level['factor'],failed_knot=response['failed_knot'],parent=parent,
            initial=response['initial'],parameters=params,parameter_order=['p_ref','E','nu','M','Md','c'],K=K,G=G,
            target_record=response['knots_wire'][response['failed_knot']*7:(response['failed_knot']+1)*7],
            retained_message=response['message'],retained_material_trials=response['material_trials'],
            retained_finite_difference_probes=response['finite_difference_probes'],retained_attempted_substeps=response['attempted_substeps'],
            retained_last_control_error=response['last_control_error'],initial_seed_increment=de,independent_scalar_return=result,
            reproduced_normalized_radial_residual=residual,analytical_apex_jacobian=[[0.,0.],[0.,0.]],
            independent_scalar_finite_difference_columns=columns,elastic_seed_increment=elastic_de,elastic_seed_scalar_return=elastic_seed,
            independently_bracketed_radial_root=dict(increment=root_de,scalar_return=root,
                note='Existence diagnostic for this symmetric scalar case; not an executed generic-driver update.')))
    return dict(kind='retained-response-independent-dp-apex-diagnostic',status='analytical-only-no-native-execution',
        report_path=str(report.relative_to(repo)),report_sha256=sha(report),model_path=str(model.relative_to(repo)),model_sha256=sha(model),
        report_solver_sha256=raw['solver_sha256'],report_catalogue_hash=raw['catalogue_hash'],
        equations=dict(trial='p_t=p_n+K tr(de); s_t=s_n+2G dev(de); q_t=sqrt(3/2 s_t:s_t)',
            smooth_gamma='(q_t-M*p_t-c)/(3G+M*K*Md)',smooth_condition='trial_yield>0 and smooth_gamma<q_t/(3G)',
            apex_condition='trial_yield>0 and smooth_gamma>=q_t/(3G)',apex='sigma=(-c/M)I; gamma=((-c/M)-p_t)/(K*Md)',
            apex_margin='(-c/M)-(p_t+K*Md*q_t/(3G)); strictly positive margin gives a locally constant stress map',
            tangent='d sigma / d de = 0 on strict apex branch'),
        conclusions=['All retained failures occur after a successful material trial at the zero-free-coordinate seed.',
            'A locally constant apex stress gives a singular reduced radial control Jacobian with nonzero residual.',
            'Tiny derivative probes remain on the same apex branch; finite-difference fallback alone cannot escape.',
            'Independent scalar roots exist for all three endpoints; the singular seed is not evidence of unattainable targets.'],
        limitations=['Retained data do not expose the failed trial state or Jacobian; these are independently reconstructed from pinned model algebra.',
            'Elastic seeds and scalar roots have not been executed through the C++ material solver.',
            'No claim of general nonlinear globalization or trajectory accuracy.'],cases=records)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    data=analyse(args.repo);args.output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(ok=True,cases=len(data['cases']),output=str(args.output))))
