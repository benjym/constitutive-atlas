"""Post-run saved-only review supplement, separate from frozen prospective audit.

The original audit checks legacy range/controller/volume/domain/parity. This
additional review checks the requested legacy sine trajectory explicitly.
No old gate or result is changed, and no compiled case is executed.
"""
import json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
def review(data):
 rows=json.loads((HERE/'laboratory-requests.json').read_bytes());assert len(data['laboratory'])==len(rows);checked=0;worst=0.
 for got,row in zip(data['laboratory'],rows):
  assert got['id']==row['id']
  if row['loading_wire']!='legacy':continue
  s=row['specification'];points=got['call']['response']['points'];assert len(points)==s['steps']+1
  for i,p in enumerate(points):
   # Matches the unchanged C++ expression; allow libm backend rounding.
   expected=s['target']*math.sin(2*3.141592653589793*s['cycles']*i/s['steps'])if s['cycles']else s['target']*i/s['steps'];error=abs(p['control']-expected);worst=max(worst,error);assert error<=1e-18+1e-14*abs(s['target']),'legacy waveform differs';checked+=1
 return {'saved_review_pass':True,'legacy_control_points':checked,'maximum_control_error':worst,'timing':'supplement defined after original native/Wasm observations and passing frozen audits','new_compiled_calls':0,'scientific_admission':False}
