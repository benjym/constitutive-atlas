"""Independent source-oracle diagnosis; no compiled artifact calls or shared edits."""
from pathlib import Path
import importlib.util,json,math
HERE=Path(__file__).resolve().parent
source=HERE.parent/'control-selection-v1/independent-review/candidate-v3-check.py'
spec=importlib.util.spec_from_file_location('occ_source_oracle',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
z=(100000.,100000.,100000.,0.,0.,0.,1.7389659628023817)
def lateral(e):return m.expected(z,[.0001,e,e,0.,0.,0.])[1]-100000.
lo,hi=-.0001,0.
assert lateral(lo)<0<lateral(hi)
for _ in range(60):
 mid=(lo+hi)/2
 if lateral(mid)>0:hi=mid
 else:lo=mid
e=(lo+hi)/2
probes=[]
for d in [[.0001,0,0,0,0,0],[.0001,1e-8,0,0,0,0],[.0001,0,1e-8,0,0,0],[.0001,e,e,0,0,0]]:
 out=m.expected(z,d);probes.append(dict(increment=d,state=out,lateral_residual=[out[1]-100000.,out[2]-100000.]))
assert max(abs(x) for x in probes[-1]['lateral_residual'])<1e-8
r={'compiled_calls':0,'oracle_path':str(source),'initial':z,'probes':probes,'root_lateral_strain':e,'interpretation':'Initial particular trial lies in the isotropic cone: nearby independent lateral probes remain isotropic and have dependent lateral stress rows. A source-admissible drained endpoint exists after a finite lateral move. This is a globalization/interface issue, not proof of absent source solution. Existing opt-in bounded recorded restart is a candidate for separately frozen qualification; no pass or gate change claimed.'}
(HERE/'recorded-source-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'root_lateral_strain':e,'lateral_residual':probes[-1]['lateral_residual'],'compiled_calls':0}))
