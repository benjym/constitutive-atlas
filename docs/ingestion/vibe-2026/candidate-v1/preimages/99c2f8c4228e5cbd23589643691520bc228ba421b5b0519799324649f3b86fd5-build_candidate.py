"""Generate a declarative transcription; this is not a constitutive kernel.

The expression map follows Mašín2026 AppendixA. Parameters bounds are explicit
prospective Atlas study guards, not source calibration confidence intervals.
"""
from pathlib import Path
import json, math, copy

ROOT = Path(__file__).resolve().parents[4]
fixture = json.loads((ROOT/'tests/fixtures/controlled-time/transport.json').read_text())
m = {k: copy.deepcopy(fixture[k]) for k in ('schema_version','formulation','initialization')}
m.update(id='vibe-2026',name='VIBE 2026 — published explicit Appendix A formulation',
    family='thermo-hydro-mechanical viscohypoplasticity',status='draft',
    description='Complete published explicit Appendix A THM law in fixed-spatial, zero-spin small-strain material-point scope. Source A7/A9 tensor identities are completed uniquely using Eqs39/42. Appendix separate hydraulic/thermal absolute terms differ from Eq27 for opposing internal contributions; no equivalence is claimed. Strict positive-suction and nonsingular-state domain, no saturated endpoint, clipping or author-code endpoint reconstruction. Parameter guards are prospective Atlas study bounds, not universal material ranges. Not approved or executable delivery until independently qualified.',
    sources=[dict(url='https://doi.org/10.1016/j.enggeo.2026.108827',locator='VoR pp15–16 AppendixA1–35; pp4–5 Tables1–3; p13 Eqs39,42; p12 Eq27 discrepancy',role='governing published explicit formulation; private PDF SHA25690b1c3bc56bacf1294e3e8ea60a217ffa1651981c86c63b0c0d9354534764912')])
P={}
def parameter(n,v,lo,hi,unit='1'):
    P[n]=dict(default=v,min=lo,max=hi,unit=unit)
parameter('phi',math.radians(25),math.radians(20),math.radians(30))
parameter('lambda_ref',.10,.08,.12)
parameter('kappa',.02,.016,.024)
parameter('Nref',1.43,1.3,1.56)
parameter('nu',.24,.20,.28)
parameter('ns',0,0,.04);parameter('ls',0,0,.01)
parameter('nT',.04,0,.08);parameter('lT',0,0,.01)
parameter('coupling_m',5,4,6)
parameter('alpha_s',.00025,.0002,.0003,{'si':[0,0,0,-1]})
parameter('nm',.9,.8,1)
parameter('hms',150e6,100e6,200e6,'Pa')
parameter('em_ref',.55,.5,.6)
parameter('Dr',.5e-6,.25e-6,.75e-6,{'si':[0,0,-1,0]})
parameter('se_ref',2e6,1e6,3e6,'Pa')
parameter('eM_ref',.2,.15,.25)
parameter('thermal_a',.118,.11,.13)
parameter('thermal_b',-.0001,-.00012,-.00008,{'si':[0,0,0,-1]})
parameter('ae',.9,.8,.95);parameter('lp',1.1,1,1.2)
parameter('IvT',5,2,8)
for n,v,u in [('Tr',294,'K'),('vf',.1,'1'),('pr',1000,'Pa'),('Oc',1.4,'1'),('xi',.2,'1'),('frm',.5,'1'),('alpha_f',1,'1'),('one_kelvin',1,'K')]:
    parameter(n,v,v,v,u)
m['parameters']=P
def state(n,shape,unit,initial,scale,quantity):
    return dict(name=n,shape=shape,unit=unit,initial=initial,scale=scale,
        semantics=dict(role='persistent',quantity=quantity,transformation='symmetric_spatial_tensor' if shape=='sym' else 'scalar_invariant'))
m['state']=[state('sigma_net','sym','Pa',[5185790.988798023]*3+[0]*3,'pr','net_cauchy_stress'),state('e','scalar','1',.725,'1','global_void_ratio'),state('a_scan','scalar','1',0,'1','hydraulic_scanning_memory')]
D=[]
def derived(n,expr): D.append(dict(name=n,expr=expr))
# Keep source compression-negative tensors explicit; Atlas boundary changes both
# strain rate and net stress signs and uses Mandel components throughout.
for n,x in [
 ('source_sigma','-sigma_net'),('source_rate','-strain_rate'),
 ('thermal_factor','(thermal_a+thermal_b*temperature)/(thermal_a+thermal_b*Tr)'),
 ('pm','-trace(source_sigma)/3+suction'),
 ('em','em_ref*exp(-(pm/hms)**nm)*thermal_factor'),
 ('eM','(e-em)/(1+em)'),
 ('sen','se_ref*eM_ref/eM*thermal_factor'),
 ('se','sen*(ae+a_scan-ae*a_scan)'),
 ('retention_power','(se/suction)**lp'),
 ('SM','1-exp(-retention_power)'),
 ('sigmaM','source_sigma-SM*suction*I'),
 ('pM','-trace(sigmaM)/3'),
 ('macro_dev','dev(sigmaM)'),
 ('macro_dev_sq','dot(macro_dev,macro_dev)'),
 ('macro_dev_det','determinant(macro_dev)'),
 ('invariant_denominator','8*pM**3-pM*macro_dev_sq+macro_dev_det'),
 ('Fm','(3*pM*macro_dev_sq+9*macro_dev_det)/invariant_denominator'),
 ('shat','sigmaM/trace(sigmaM)-I/3'),
 ('shat_sq','dot(shat,shat)'),
 ('cos3theta','select(shat_sq>0,-sqrt(6)*cube_trace(shat)/shat_sq**1.5,0)'),
 ('omega','-log(cos(phi)**2)/log(Oc)+0.3*(Fm-sin(phi)**2)'),
 ('Nst','Nref-ns/lp*log(SM)+nT*log(temperature/Tr)'),
 ('lam','lambda_ref-ls/lp*log(SM)+lT*log(temperature/Tr)'),
 ('pe','pr*exp((Nst-log(1+e))/lam)'),
 ('OI','pe/pM'),
 ('OA','OI*(1-Fm)**(1/omega)'),
 ('eA','exp(log(1+e)+lam*log(OA))-1'),
 ('re','(e-em)/(eA-em)'),
 ('fm','1-re**coupling_m'),
 ('fscan','select(suction_rate>0*pr*Dr,a_scan,select(suction_rate<0*pr*Dr,1-a_scan,0))'),
 ('rlambda','0.1+0.9*fscan**3'),
 ('DsS','rlambda/suction*(1-SM)*lp*log(1-SM)'),
 ('DseS','-(1-SM)*lp*log(1-SM)/se'),
 ('DeMse','-se/eM'),
 ('DTse','se*thermal_b/(thermal_a+thermal_b*temperature)'),
 ('Dp','-em*nm/pm*(pm/hms)**nm'),
 ('DTm','em*thermal_b/(thermal_a+thermal_b*temperature)'),
 ('Aact','DseS*se/(lp*SM)*(ns-ls*log(pM/pr))'),
 ('lact_denominator','eM*(1+em)-Aact*(1+e)'),
 ('lact','(eM*(1+em)*lam+Aact*Dp*pM*(1+eM))/lact_denominator'),
 ('fs','3*pM/2*(lact+kappa)/(lact*kappa)*(1-2*nu)/(1+nu)'),
 ('ci_denominator','(lact+kappa)*(OI**alpha_f-OA**alpha_f)+2*kappa*OA**alpha_f'),
 ('ci','((lact+kappa)*(OI**alpha_f-1)+2*kappa)/ci_denominator'),
 ('fu','OA**(-coupling_m)'),
 ('DsP','-pe*DsS/(lp*SM*lam)*(ns-ls*log(pe/pr))'),
 ('DTP','pe/(temperature*lam)*(nT-lT*log(pe/pr))'),
 ('sign_Ds','select(DsP<0,1,select(DsP>0,-1,0))'),
 ('sign_DT','select(DTP<0*pr/Tr,1,select(DTP>0*pr/Tr,-1,0))'),
 ('Hs_prime','ci*sigmaM*DsP/pe*sign_Ds*select(-DsP*suction_rate>=0*pr*Dr,1,0)'),
 ('HT_prime','ci*sigmaM*DTP/pe*sign_DT*select(-DTP*temperature_rate>=0*pr*Dr,1,0)'),
 ('dB','nu/(1-2*nu)'),
 ('bB','-DseS*DeMse*suction*(1+eM)*Dp/(3*(1+em))'),
 ('cB','-fs*fm*Dp/(9*(1+em))'),
 ('qB','bB+cB+3*cB*dB'),
 ('B_denominator','1+3*qB'),
 ('d_raw','-shat+I*(2/3-(cos3theta+1)/4*Fm**0.25)*(Fm**(xi/2)-sin(phi)**xi)/(1-sin(phi)**xi)'),
 ('d_direction','d_raw/norm(d_raw)'),
 ('Ad','fs*(d_direction+dB*trace(d_direction)*I)+sigmaM*trace(d_direction)/lact'),
 ('Iv','0.004+IvT*((temperature-Tr)/one_kelvin)**3*0.00000001'),
 ('NE','(vf-1)*OA**(-alpha_f)*Ad'),
 ('NVE','-vf*OA**(-1/Iv)*Ad'),
 ('HLsE','-Dp*fs*fm/(3*(1+em))*(1+3*dB)*I+(DsS*suction+SM-Dp*DseS*DeMse*suction*(1+eM)/(1+em))*I'),
 ('HNsE','fu*Hs_prime-sqrt(3)*frm*fm/3*NE*abs(Dp)/(1+em)'),
 ('HLTE','-alpha_s*fs*fm/3*(1+3*dB)*I+DseS*suction*(DTse-DeMse*DTm*(1+eM)/(1+em))*I'),
 ('HNTE','fu*HT_prime-sqrt(3)*frm*fm/3*NE*abs(alpha_s)'),
 ('LE_rate','fs*(source_rate+dB*trace(source_rate)*I)+DseS*DeMse*suction*(1+eM)*trace(source_rate)*I'),
 ('source_rhs','LE_rate+NE*norm(source_rate)+NVE*Dr+HLsE*suction_rate+HNsE*abs(suction_rate)+HLTE*temperature_rate+HNTE*abs(temperature_rate)'),
 ('source_stress_rate','source_rhs-qB/B_denominator*trace(source_rhs)*I'),
 ('Sr_value','SM+em/e*(1-SM)')]: derived(n,x)
m['derived']=D
m['equations']={'sigma_net':'-source_stress_rate','e':'-(1+e)*trace(strain_rate)','a_scan':'(se/sen)*(1-rlambda)/(suction*(1-ae))*suction_rate'}
m['domain']=['suction>0*pr','temperature>0*Tr','thermal_factor>0','pm>0*pr','e>0','em>0','eM>0','a_scan>=0','a_scan<=1','SM>0','SM<1','pM>0*pr','abs(invariant_denominator)>0*pr**3','Fm>=0','Fm<1','omega>0','lam>0','pe>0*pr','OI>0','OA>0','eA>em','re>0','abs(lact_denominator)>0','lact>0','abs(ci_denominator)>0','abs(B_denominator)>0','Iv>0','norm(d_raw)>0','Sr_value>=0','Sr_value<=1']
m['observables']=[dict(name='stress',shape='sym',unit='Pa',scale='pr',expr='sigma_net')]
for n,x in [('micro_void_ratio','em'),('macro_void_ratio','eM'),('macro_saturation','SM'),('saturation','Sr_value'),('relative_density','re'),('overconsolidation','OA'),('viscosity_factor','Iv')]:
    m['observables'].append(dict(name=n,shape='scalar',unit='1',scale='1',expr=x))
m['initialization']['required_state']=['sigma_net','e','a_scan']
dest=ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print(dest)
