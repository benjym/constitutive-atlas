"""Post-observation source oracle on saved parent/strain increments only.
Cumulative-strain subtraction is not a claim of exact unrecorded de.
"""
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
import json,sys,hashlib
import independent_source as src
R=Path(sys.argv[1]);P=Path(__file__).parent;V=R/'catalogue/investigations/mc-laboratory-preview-v1';load=lambda p:json.loads(p.read_bytes());data=load(V/'source-input.json');res=[]
with localcontext()as ctx:
 ctx.prec=280;p=src.parameters(data['parameters']);E=p['E'];K,G,s,d=p['K'],p['G'],p['s'],p['d'];Dc=4*K*d*s+G*(3-s-d+s*d/3);De=4*K*d*s+G*(3+s+d+s*d/3);tangents={'elastic':3*G,'compression':12*K*G*d*s/Dc,'extension':12*K*G*d*s/De}
 for backend in('native','wasm'):
  journal=load(V/backend/'journal.json');o=json.loads(next(x['raw']for x in journal if x['id']=='protocol-3/cyclic'));maxstress=D(0);maxstrainuncertainty=D(0);rows=[]
  for i,(old,new)in enumerate(zip(o['points'],o['points'][1:]),1):
   H=lambda x:D.from_float(float(x));a,r=map(H,old['state'][:2]);ea=H(new['strain'][0])-H(old['strain'][0]);er=H(new['strain'][1])-H(old['strain'][1]);an,rn,g,b,t=src.return_step(a,r,ea,er,p);da=H(new['state'][0])-an;dr=H(new['state'][1])-rn;error=(da*da+2*dr*dr).sqrt();maxstress=max(maxstress,error)
   # Two accumulated additions may hide their rounded de. Bound with full eps per endpoint.
   strainuncertainty=(abs(H(new['strain'][0]))+abs(H(old['strain'][0]))+2*(abs(H(new['strain'][1]))+abs(H(old['strain'][1]))))*(D(2)**-52)*(3*K+2*G);maxstrainuncertainty=max(maxstrainuncertainty,strainuncertainty)
   rows.append({'point':i,'independent_source_branch':b,'gamma':str(g),'stress_norm_error_using_cumulative_strain_differences':str(error),'axial_stress_error':str(da),'radial_stress_error':str(dr),'conservative_unrecorded_increment_rounding_stress_scale':str(strainuncertainty),'actual_inner_error':new['error'],'actual_inner_iterations':new['iterations']})
  res.append({'backend':backend,'maximum_source_update_error_norm':str(maxstress),'maximum_cumulative_strain_subtraction_uncertainty_stress_scale':str(maxstrainuncertainty),'points':rows})
 out={'identity':'mc-cyclic-saved-increment-independent-source-diagnostic-v1','source_trigonometry':'canonical exact stored phi/psi highprecision','tangent_q_per_axial_strain':{k:str(v)for k,v in tangents.items()},'interpretation':'Uses observed cumulative-strain differences; does not recover exact original de or prove internal outer iterations. Source update consistency can discriminate constitutive mismatch from changed chosen strain only within the displayed rounding uncertainty.','new_candidate_calls':0,'new_compiled_calls':0,'backends':res}
 (P/'source-update-check.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'tangents':out['tangent_q_per_axial_strain'],'backends':[{k:v for k,v in x.items()if k!='points'}for x in res]},indent=2))
