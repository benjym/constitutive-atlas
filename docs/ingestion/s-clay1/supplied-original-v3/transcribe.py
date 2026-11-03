"""Create the first candidate; production is the emitted declarative JSON only."""
import json
from pathlib import Path
from atlas.model import formulation_inputs
O=Path(__file__).parent
p={}
for name,d,lo,hi,u,label in [('p_ref',20000,1,1e9,'Pa','Numerical stress scale'),('M',1.1,.1,3,'1','Critical-state stress ratio'),('lambda_c',.44,.001,2,'1','Virgin compression slope'),('kappa',.04,.0001,1,'1','Elastic swelling slope'),('nu',.2,-.9,.49,'1','Elastic Poisson ratio'),('beta',.67,0,10,'1','Relative shear contribution to fabric rotation'),('mu',20,0,1000,'1','Fabric rotation rate')]:
 p[name]={'default':d,'min':lo,'max':hi,'unit':u,'label':label}
def state(name,shape,unit,initial,scale,quantity,role='persistent'):
 return dict(name=name,shape=shape,unit=unit,initial=initial,scale=scale,semantics=dict(role=role,quantity=quantity,transformation='symmetric_spatial_tensor' if shape=='sym' else 'scalar_invariant'))
m=dict(schema_version='0.3',id='s-clay1',name='S-CLAY1 — Wheeler et al. (2003)',family='anisotropic critical-state plasticity',status='transcribed',description='Original constant-M full 3D S-CLAY1 with associated flow, isotropic pressure-dependent elasticity and volumetric/shear rotational hardening. Atlas endpoint implicit elasticity/fabric and exponential volume/size discretization. Fixed-frame infinitesimal strain; illustrative Otaniemi parameters, no bonding, creep or finite-rotation transport.',sources=[dict(url='https://doi.org/10.1139/T02-119',locator='Wheeler et al.2003 CGJ40 pp403–418: Eq1 elasticity; Eqs2–5,7–9 yield/flow/hardening; AppendixA1–A14 tensor generalization. ConstantM option p404/407/413. Atlas finite-step choices: source packet supplied-original-v3/README.md.',role='original governing formulation')],parameters=p,
 formulation=dict(time_dependence='strain_path',equation_form='incremental_residual',kinematics='small_strain_3d',frame='fixed_spatial',objective_rate='none',tensor_representation='mandel',stress_sign='compression_positive',strain_sign='compression_positive',inputs=formulation_inputs(physical=False),stress=dict(source='state',name='sigma',measure='cauchy',scope='effective')),
 state=[state('sigma','sym','Pa',[20000,12500,12500,0,0,0],'p_ref','cauchy_stress'),state('fabric','sym','1',[.28,-.14,-.14,0,0,0],'1','deviatoric_fabric_tensor'),state('v','scalar','1',3.46,'1','specific_volume'),state('pm','scalar','Pa',17600,'p_ref','yield_surface_size'),state('gamma','scalar','1',0,'1','scaled_incremental_plastic_multiplier','plastic_multiplier')],
 initialization=dict(method='explicit_state',default_policy='examples_only',required_state=['sigma','fabric','v','pm'],validation='domain_and_initial_checks'),
 derived=[dict(name=n,expr=e) for n,e in [
 ('mean','trace(sigma) / 3'),('sdev','dev(sigma)'),('a2','1.5 * dot(fabric,fabric)'),('shift','sdev - mean * fabric'),
 ('yield_dim','1.5 * dot(shift,shift) - (M**2 - a2) * (pm - mean) * mean'),('yield_scaled','yield_dim / p_ref**2'),
 ('flow_volume','2 * M**2 * mean - 3 * dot(sdev,fabric) - (M**2 - a2) * pm'),('flow_dev','3 * shift'),
 ('plastic_volume','gamma * flow_volume / p_ref'),('plastic_shear','gamma * sqrt(2.0 / 3.0) * norm(flow_dev) / p_ref'),
 ('K','v * mean / kappa'),('G','3 * K * (1 - 2 * nu) / (2 * (1 + nu))')]],
 equations=dict(sigma='sigma - sigma_n - K * (trace(de) - plastic_volume) * I - 2 * G * (dev(de) - gamma * flow_dev / p_ref)',fabric='fabric - fabric_n - mu * ((3 * sdev / (4 * mean) - fabric) * max(plastic_volume, 0) + beta * (sdev / (3 * mean) - fabric) * plastic_shear)',v='v - v_n * exp(-trace(de))',pm='pm - pm_n * exp(v * plastic_volume / (lambda_c - kappa))',gamma='sqrt(gamma**2 + yield_scaled**2) - gamma + yield_scaled'),
 domain=['lambda_c > kappa','mean > 0 * p_ref','pm > 0 * p_ref','v > 1','M**2 > a2','abs(trace(fabric)) < 1e-9','gamma > -1e-9'],
 initial_checks=['yield_scaled <= 1e-8'])
(O/'candidate/s-clay1.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
