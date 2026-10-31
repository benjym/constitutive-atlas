"""Map literal requests to independently frozen high-precision endpoint references."""
import json
from pathlib import Path
def read(p):return json.loads(p.read_text())
def expected_endpoint(study,request):
 packet=Path(study)/'reference';freeze=read(packet/'prospective-freeze.json');refs=read(packet/'references.json')
 assert refs['all_checks_passed']is True and refs['compiled_calls']==0 and refs['Atlas_imports']is False
 model=read(Path(study)/'models/hypoplastic-clay-2005.json')
 parameters=dict(zip(model['parameters'],map(float,request['parameters'].split(','))))
 for key,value in freeze['parameters'].items():assert parameters[key].hex()==value['hex'],key
 initial=list(map(float,request['initial'].split(',')));assert initial==[float(freeze['initial']['p']['literal'])]*3+[0.]*3+[float(freeze['initial']['e']['literal'])]
 if request['mode']=='integrate':
  assert list(map(float,request['strain'].split(',')))==[0.]*6;target=0.
 else:assert request['protocol']==4 and request['cycles']==0;target=float(request['target'])
 cases=refs['precision_results']['160']['cases'];matched=[c for c in cases if float(c['axial_target'])==target]
 assert len(matched)==1,'exact frozen endpoint target mapping'
 case=matched[0];return {'p':float(case['p']),'e':float(case['e']),'reference_id':case['id']}
