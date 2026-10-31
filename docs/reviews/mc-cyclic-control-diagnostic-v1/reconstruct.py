"""Post-observation diagnostic from saved bytes only; no model/candidate calls."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import json,hashlib,sys
R=Path(sys.argv[1]);P=Path(sys.argv[2]);V=R/'catalogue/investigations/mc-laboratory-preview-v1';E=R/'catalogue/investigations/mc-preview-envelope-v2'
load=lambda p:json.loads(p.read_bytes());ff=lambda v:F.from_float(float(v))
raw={k:load(V/k/'journal.json')for k in('native','wasm')};obs={k:json.loads(next(x['raw']for x in rows if x['id']=='protocol-3/cyclic'))for k,rows in raw.items()};ref=next(x for x in load(V/'reference/reference-p360.json')['paths']if x['id']=='protocol-3/cyclic');inputs=next(x for x in load(V/'source-input.json')['paths']if x['id']=='protocol-3/cyclic')
def numeric(x):
 if isinstance(x,F):return {'fraction':str(x),'decimal':str(D(x.numerator)/D(x.denominator))}
 return x
rows=[];summaries={};all_fail=[];first=None
with localcontext()as ctx:
 ctx.prec=100
 # Independently inventory all parity failures using frozen scalar budget; no original assessor execution.
 for xn,xw in zip(raw['native'][1:],raw['wasm'][1:]):
  assert xn['id']==xw['id'];n,w=json.loads(xn['raw']),json.loads(xw['raw'])
  for i,(a,b)in enumerate(zip(n['points'],w['points'])):
   for key in('control','state','strain','p','q','q_signed','u'):
    av,bv=(a[key],b[key])if key in('state','strain')else([a[key]],[b[key]])
    for j,(u,v)in enumerate(zip(av,bv)):
     error=abs(u-v);budget=1e-10*max(1,abs(u),abs(v))
     if error>budget:all_fail.append(dict(id=xn['id'],point=i,field=key,component=j,difference=error,budget=budget,fraction=error/budget))
 for backend,o in obs.items():
  maxres=(0.,0);maxerror=(F(0),0);sres=F(0);sumdelta=F(0);backendrows=[];qinitial=ff(o['points'][0]['state'][0])-(ff(o['points'][0]['state'][1])+ff(o['points'][0]['state'][2]))/2
  for i,(point,source)in enumerate(zip(o['points'],ref['points'])):
   state=point['state'];qexact=ff(state[0])-(ff(state[1])+ff(state[2]))/2;qeval=state[0]-.5*(state[1]+state[2]);control=point['control'];qe=qexact-ff(control)
   row={'point':i,'control':control,'control_hex':float(control).hex(),'q_from_serialized_state_exact':numeric(qexact),'q_state_minus_displayed_control_exact':numeric(qe),'source_q_error':str(D(qexact.numerator)/D(qexact.denominator)-D(source['q'])),'source_p_error':str(D.from_float(float(point['p']))-D(source['mean_stress'])),'inner_iterations':point['iterations'],'inner_error':point['error'],'source_branch':source['branch']}
   if i:
    prev=o['points'][i-1];qprev=prev['state'][0]-.5*(prev['state'][1]+prev['state'][2]);delta=control-prev['control'];residual=(qeval-qprev)-delta
    residual_exact=(qexact-(ff(prev['state'][0])-(ff(prev['state'][1])+ff(prev['state'][2]))/2))-ff(delta);sres+=residual_exact;sumdelta+=ff(delta)
    assert qexact-qinitial==sumdelta+sres
    intended=float.fromhex(inputs['control_deltas'][i-1]);row.update(control_delta=delta,control_delta_hex=delta.hex(),control_delta_minus_intended_exact=numeric(ff(delta)-ff(intended)),outer_residual_reconstructed=residual,outer_residual_exact=numeric(residual_exact),outer_stopping_threshold=.001,outer_stopping_fraction=abs(residual)/.001,cumulative_outer_residual_exact=numeric(sres),cumulative_delta_minus_displayed_control_exact=numeric(sumdelta-ff(control)))
    if abs(residual)>maxres[0]:maxres=(abs(residual),i)
    if abs(qe)>maxerror[0]:maxerror=(abs(qe),i)
   backendrows.append(row)
  summaries[backend]={'maximum_reconstructed_outer_residual':maxres[0],'maximum_residual_point':maxres[1],'maximum_q_state_minus_control':numeric(maxerror[0]),'maximum_q_error_point':maxerror[1],'final_cumulative_outer_residual':numeric(sres),'all_outer_residuals_within_source_threshold':maxres[0]<.001,'journal_inner_error_is_not_outer_control_error':True};rows.append({'backend':backend,'points':backendrows})
 differences=[]
 for i,(n,w)in enumerate(zip(obs['native']['points'],obs['wasm']['points'])):
  dr=[float(a)-float(b)for a,b in zip(n['state'],w['state'])];dc=n['control']-w['control'];ds=[float(a)-float(b)for a,b in zip(n['strain'],w['strain'])]
  if first is None and any(v!=0 for v in dr+ds+[dc]):first=i
  differences.append({'point':i,'control_native_minus_wasm':dc,'state_native_minus_wasm':dr,'strain_native_minus_wasm':ds,'q_signed_native_minus_wasm':n['q_signed']-w['q_signed'],'u_native_minus_wasm':n['u']-w['u'],'source_branch':ref['points'][i]['branch']})
 result={'identity':'mc-cyclic-control-saved-evidence-reconstruction-v1','new_candidate_calls':0,'new_compiled_calls':0,'acceptance_bounds_changed':False,'parity_failures':all_fail,'failure_count':len(all_fail),'first_any_recorded_divergence_point':first,'summaries':summaries,'differences':differences,'backends':rows}
 P.mkdir(parents=True,exist_ok=True);(P/'reconstruction.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'failures':len(all_fail),'firstdivergence':first,'summaries':summaries,'control_differences':[(x['point'],x['control_native_minus_wasm'])for x in differences if x['control_native_minus_wasm']]},indent=2))
