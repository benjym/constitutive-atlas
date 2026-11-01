"""Create the separate full-extension/Appendix-V backward-Euler research identity."""
import json
import math
from pathlib import Path
P=Path(__file__).resolve().parent

def build():
    form=json.loads((P.parent/'crosswalk.json').read_text())['formulation']
    form['equation_form']='incremental_residual'
    params={}
    def param(name,value,lo,hi,unit,label):params[name]={'default':value,'min':lo,'max':hi,'unit':unit,'label':label}
    param('p_ref',98000.,1.,1e9,'Pa','Reference pressure and numerical stress scale')
    param('Cc',.0508,1e-5,1.,'1','lambda/(1+e0), Table 2')
    param('Ce',.0112,1e-6,.5,'1','kappa/(1+e0), Table 2')
    param('e_ref',.83,0.,3.,'1','Fixed reference void ratio, not current e')
    param('Rcs',3.5,1.01,10.,'1','Critical triaxial compression principal-stress ratio')
    param('beta',1.5,1.01,4.,'1','Yield shape exponent')
    param('a_density',500.,0.,10000.,'1','Single clay density coefficient')
    param('nu',.2,-.9,.49,'1','Elastic Poisson ratio')
    state=[]
    def st(name,shape,unit,initial,scale,quantity,role='persistent'):
        state.append(dict(name=name,shape=shape,unit=unit,initial=initial,scale=scale,semantics=dict(role=role,quantity=quantity,transformation='symmetric_spatial_tensor' if shape=='sym' else 'scalar_invariant')))
    st('sigma','sym','Pa',[98000.,98000.,98000.,0.,0.,0.],'p_ref','cauchy_stress')
    st('rho','scalar','1',0.,'1','density_surface_gap')
    st('e','scalar','1',.83,'1','void_ratio_constant_reference_small_strain')
    st('smp','sym','1',[1/math.sqrt(3)]*3+[0.]*3,'1','modified_stress_normal_auxiliary_algebraic_tensor')
    st('gamma_af','scalar','1',0.,'1','scaled_associated_flow_increment','increment_unknown')
    st('gamma_ic','scalar','1',0.,'1','isotropic_plastic_volume_increment','increment_unknown')
    d=[]
    def der(n,e):d.append({'name':n,'expr':e})
    der('S','sigma/p_ref');der('U','(sigma-sigma_n)/p_ref')
    der('pbar','trace(S)/3');der('DS','dev(S)');der('DS2','dot(DS,DS)')
    der('Jthree','determinant(DS)');der('Ithree','determinant(S)')
    der('Itwo','3*pbar**2-DS2/2');der('Ione','trace(S)')
    der('adjS','tensor_square(S)-Ione*S+Itwo*I')
    der('invS','adjS/Ithree')
    der('tn','3*Ithree/Itwo')
    der('nlog','invS-(Ione*I-S)/Itwo')
    der('dtn','tn*nlog')
    der('Xtwo','(pbar*DS2/3-Jthree)/Ithree')
    der('gradXtwo','(DS2/9*I+2*pbar/3*DS-dev(tensor_square(DS))-Xtwo*adjS)/Ithree')
    der('Xcs','sqrt(2)/3*(sqrt(Rcs)-1/sqrt(Rcs))')
    der('Ycs','(1-sqrt(Rcs))/(sqrt(2)*(sqrt(Rcs)+0.5))')
    der('Mpower','Xcs**beta+Xcs**(beta-1)*Ycs')
    der('zeta','select(Xtwo > 0,Xtwo**(beta/2)/(beta*Mpower),0)')
    der('coef','select(Xtwo > 0,Xtwo**(beta/2-1)/Mpower,0)')
    der('tbar','(tensor_square(smp+S)-tensor_square(smp)-tensor_square(S))/2')
    der('xbar','tbar/tn-smp')
    der('mflow','(smp+coef*(xbar-Xtwo*smp))/tn')
    der('nload','nlog+coef*gradXtwo/2')
    der('Cp','Cc-Ce')
    der('Kbar','pbar/Ce')
    der('Gbar','3*Kbar*(1-2*nu)/(2*(1+nu))')
    der('elastic_trial','Kbar*trace(de)*I+2*Gbar*dev(de)')
    der('trial_load','dot(nload,elastic_trial)')
    der('hard','(trace(mflow)+a_density*rho**2/tn)/Cp')
    der('icmod','(1+a_density*rho**2/trace(smp))/Cp')
    der('fsig','dot(nload,U)')
    der('positive_dtn','max(dot(dtn,U),0)')
    der('surface_size','tn*exp(zeta)')
    der('ic_drive','positive_dtn/surface_size')
    der('af_drive','fsig-ic_drive')
    # Pure elasticity on the strict unloading side, source softening branch for h<0,
    # Appendix V when the hardening AF numerator would be negative.
    der('flow_af','gamma_af*mflow')
    der('flow_ic','gamma_ic/3*I')
    der('dep','flow_af+flow_ic')
    eq={
      'sigma':'sigma-sigma_n-p_ref*(Kbar*trace(de-dep)*I+2*Gbar*dev(de-dep))',
      'rho':'rho-rho_n-(1+e_ref)*(trace(dep)-Cp*fsig)',
      'e':'e-e_n+(1+e_ref)*trace(de)',
      'smp':'tensor_square(smp)-adjS/Itwo',
      'gamma_af':'select(trial_load < 0,gamma_af,select(hard < 0,gamma_af*hard-fsig,select(af_drive < 0,gamma_af,gamma_af*hard-af_drive)))',
      'gamma_ic':'select(trial_load < 0,gamma_ic,select(hard < 0,gamma_ic,select(af_drive < 0,gamma_ic*icmod-fsig,gamma_ic*icmod-ic_drive)))'
    }
    # SPD from all three elementary invariants. Conditions hold at hydro/repeated spectra.
    domain=['Cc > Ce','Ione > 0','Itwo > 0','Ithree > 0','trace(smp) > 0',
      'trace(smp)**2 > dot(smp,smp)','determinant(smp) > 0','Mpower > 0','e > -1']
    model=dict(schema_version='0.3',id='nakai-hinokio-2004-clay-appendix-v-be',name='Nakai–Hinokio 2004 subloading tij — clay / Appendix V / BE research',family='critical-state plasticity',status='draft',
      description='Full one-a subloading tij clay with path-dependent AF/IC flow, softening and Appendix V region IV. Project endpoint backward-Euler differential discretization and constant-reference small-strain void bookkeeping; no finite rotation or scientific admission. smp is a persistent algebraic auxiliary for the positive matrix inverse square root. At exact isotropy the continuous flow value is used; the Newton branch derivative there is an algorithmic selection, not a classical material tangent.',
      sources=[dict(url='https://doi.org/10.3208/sandf.44.2_53',role='formulation',locator='Nakai/Hinokio2004 pp54–61 Table1 Eqs1–5,14–54; p70 AppendixIV/V A17–A28; one-a Table2 clay identity. Paper EqA8 intermediate equality not used. Project endpoint BE and density compatibility are separately documented in working-v1/README.md.')],
      formulation=form,parameters=params,state=state,derived=d,domain=domain,equations=eq,
      initialization=dict(method='explicit_state',default_policy='examples_only',required_state=[s['name'] for s in state if s['semantics']['role']=='persistent'],validation='domain_and_initial_checks'),
      initial_checks=['rho >= -1e-10','norm(tensor_square(smp)-adjS/Itwo) <= 1e-8'])
    return model

if __name__=='__main__':
    path=P/'model.json';path.write_text(json.dumps(build(),indent=2,ensure_ascii=False)+'\n');print(path)
