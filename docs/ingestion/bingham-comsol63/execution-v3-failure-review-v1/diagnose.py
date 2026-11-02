"""Saved-output and local source-derived Newton-direction arithmetic only."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;EX=OUT.parent/'execution-v3'
# Preserve initial snapshot; never re-read growing source into this retained fixture.
raw=(OUT/'native-partial-snapshot.json').read_bytes();rows=json.loads(raw);cases=json.loads((EX/'cases.json').read_text())['cases']
G=1e7;Y=1e5;eta=2e7;c=math.sqrt(1.5);a=3*G/eta;results=[]
for channel in [3,4,5]:
 ident=f'radial-channel-{channel}-z100000-d-0.012';case=next(x for x in cases if x['id']==ident);row=next(x for x in rows if x['id']==ident)
 r=json.loads(row['calls'][0]['stdout']);assert not r['ok'] and len(r['points'])==2
 z=case['specification']['initial'];D=case['specification']['segments'][0]['controls'][channel]['value'];shear=2*G*(z[channel]-z[channel+6]);q=c*math.sqrt(shear*shear);lam=max(q-Y,0)/eta
 assert q>Y and z[12]==0
 # In the single-shear subspace, fp=c*lambda; q=c*2G*(eps-vp).
 # Newton at the incoming state gives de=hD, dp=c*da and:
 # (1+a*h) da = h*lambda0 + h*h*c*2G*D/eta.
 bound_h=lam/abs(c*2*G*D/eta);directions=[]
 for exponent in range(12,39):
  h=2.**(-exponent);da=(h*lam+h*h*c*2*G*D/eta)/(1+a*h)
  assert h>=1e-12 and da<0
  assert all(z[12]+fraction*da<0 for fraction in [2.**(-k) for k in range(12)])
  directions.append({'h':h,'delta_alpha':da,'smallest_line_search_alpha_candidate':da/2048})
 # Independent exact scalar reference: starts at yield, elastic until opposite yield.
 b=2*G*(-.012);entry=2*Y/abs(b);T=2.;active=T-entry;equilibrium=-Y+b/a
 zend=equilibrium+(-Y-equilibrium)*math.exp(-a*active);alpha=(-b*active+zend+Y)/(3*G)
 ref=case['references'][-1];Nshear=math.sqrt(2/3)
 assert abs(ref['stress'][channel]-Nshear*zend)<1e-8 and abs(ref['state'][12]-alpha)<1e-15
 results.append({'id':ident,'saved_ok':r['ok'],'saved_message':r['message'],'saved_points':len(r['points']),'unchanged_committed_initial':r['points'][0]['state']==r['points'][1]['state']==z,'repeat_stdout_identical':row['calls'][0]['stdout']==row['calls'][1]['stdout'],'initial_shear_stress':shear,'initial_q':q,'initial_lambda_per_second':lam,'initial_scaled_strain_residual':abs(D),'alpha_direction_negative_for_h_above':bound_h,'tested_permitted_dyadic_h_directions':directions,'independent_exact_final_z':zend,'independent_exact_final_alpha':alpha})
result={'reviewer':'/root/bingham_review','partial_snapshot_rows':len(rows),'partial_snapshot_sha256':hashlib.sha256(raw).hexdigest(),'compiled_calls':0,'material_calls':0,'analysis':'local analytic Newton direction; no material trajectory execution or assertion of observed internal Newton trace','cases':results}
(OUT/'DIAGNOSTICS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
