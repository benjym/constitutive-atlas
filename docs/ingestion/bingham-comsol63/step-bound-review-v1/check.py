"""Independent source-bound arithmetic only; no interpreter or material calls."""
from pathlib import Path
import hashlib,json,math
from decimal import Decimal,localcontext
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SRC=OUT.parent/'step-bound-analysis-v1'
with localcontext() as ctx:
 ctx.prec=60
 G=Decimal(10000000);eta=Decimal(20000000);Y=Decimal(100000);T=Decimal(2)
 a=3*G/eta;tau=1/a;v=2*G*Decimal('.012');F=Decimal(390000)
 M=min(tau/1024,Y/(v*1024));H=M/2;I=v*H*H/(2*eta)
 globalH=Decimal('3e-7')*eta/(2*T*F)
 data=dict(tau_s=float(tau),M_s=float(M),H_s=float(H),I=float(I),stress_scalar_Pa=float(3*G*I),vp_component=float(Decimal('1.5')*(Decimal(2)/3).sqrt()*I),continuation_alpha=float((1+a*T)*I),global_exact_BE_H_s=float(globalH),global_exact_BE_M_s=float(2*globalH))
 checks=[]
 for x in map(Decimal,['1e-12','1e-9','1e-6','.001','.1','1','10']):
  value=x-(1+x).ln();upper=x*x/2
  assert 0<=value<=upper
  checks.append(dict(x=str(x),value=str(value),upper=str(upper)))
 authored=json.loads((SRC/'results.json').read_text())
 f=authored['event_local_proposed_formula']
 for k,want in [('M_s',data['M_s']),('H_s',data['H_s']),('missed_exit_alpha_upper',data['I']),('immediate_scalar_stress_error_upper_Pa',data['stress_scalar_Pa']),('immediate_vp_component_upper',data['vp_component']),('later_alpha_error_upper_over_T',data['continuation_alpha'])]:
  assert math.isclose(f[k],want,rel_tol=2e-15),k
 for k,h in authored['source_hashes'].items():assert hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==h,k
 handoff=json.loads((SRC/'handoff.json').read_text())
 for k,h in handoff['owned_files'].items():assert hashlib.sha256((SRC/k).read_bytes()).hexdigest()==h,k
 data.update(algebra_checks=checks,source_pins_verified=len(authored['source_hashes']),source_handoff_pins_verified=len(handoff['owned_files']),compiled_calls=0,material_calls=0)
 (OUT/'RESULTS.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data,indent=2))
