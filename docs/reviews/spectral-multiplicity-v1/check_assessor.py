"""Independent ideal-frame/corruption probes before compiled observations."""
import copy,json,sys
from pathlib import Path
from decimal import Decimal as D
from assess import assess
P=Path(__file__).parent
refs=json.loads((P/'references.json').read_text())
rows=[]
for i,case in enumerate(refs['cases']):
 row={'index':i,'classifier_ok':1,'repeated':list(map(int,case['repeated'])),'double_jet_parity':1,'model_structure':1,'history_structure':1,'history_rollback':1,'history_recovery':1}
 for name,expected in zip(('hi','lo'),case['extremes']):
  row[name]={'value':float(expected['value']),'derivatives':list(map(float,expected['derivatives']))} if expected['ok'] else None
 hi,lo=case['extremes'];both=hi['ok'] and lo['ok']
 gap=D(hi['value'])-D(lo['value']) if both else D(0)
 good=both and abs(gap)<=D.from_float(sys.float_info.max)
 row['model_ok']=int(good);row['history_ok']=int(good)
 row['model']={'value':float(gap),'derivatives':[float(D(a)-D(b)) for a,b in zip(hi['derivatives'],lo['derivatives'])]} if good else None
 row['history_value']=float(gap) if good else None
 rows.append(row)
rows.append({'summary':True,'cases':len(refs['cases']),'nonfinite_checks':1404,'controls_pass':1})
wire=lambda r:'\n'.join(json.dumps(x) for x in r)+'\n'
assess(wire(rows),refs)
changes=[]
for key in ('classifier_ok','double_jet_parity','model_structure','history_structure','history_rollback','history_recovery','model_ok','history_ok'):
 changes.append((key,lambda r,k=key:r[0].update({k:0})))
changes += [('repeated',lambda r:r[0].update(repeated=[0,0])),('value',lambda r:r[4]['hi'].update(value=12345)),('seed38',lambda r:r[4]['hi']['derivatives'].__setitem__(37,12345)),('model_value',lambda r:r[4]['model'].update(value=12345)),('history_value',lambda r:r[4].update(history_value=12345)),('missing',lambda r:r.pop(4)),('order',lambda r:r[4].update(index=999)),('summary',lambda r:r[-1].update(nonfinite_checks=0))]
failed=next((i,k) for i,row in enumerate(rows[:-1]) for k in ('hi','lo') if row[k] is None)
changes.append(('expected_failure_masked',lambda r:r[failed[0]].update({failed[1]:{'value':0.,'derivatives':[0.]*38}})))
for name,change in changes:
 bad=copy.deepcopy(rows);change(bad)
 try:assess(wire(bad),refs)
 except (AssertionError,KeyError):pass
 else:raise AssertionError('corruption not rejected: '+name)
print(json.dumps({'ideal_frame_pass':True,'corruptions_rejected':len(changes),'names':[x[0] for x in changes]},indent=2))
