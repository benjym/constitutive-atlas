from pathlib import Path
import json,copy,subprocess,tempfile
P=Path(__file__).parent;I=P/'initial';old=json.loads((I/'baseline/backend-results.json').read_text());old['status']='passed';results=[]
mutations=[('signed-zero-state',lambda d:d['pairs'][0]['native']['points'][0]['state'].__setitem__(3,-0.)),('bool-zero-state',lambda d:d['pairs'][0]['native']['points'][0]['state'].__setitem__(3,False)),('extra-nested-q',lambda d:d['pairs'][0]['native']['integration_settings'].update(q=123.))]
with tempfile.TemporaryDirectory(dir=P)as tmp:
 for label,change in mutations:
  data=copy.deepcopy(old);change(data);path=Path(tmp)/'synthetic.json';path.write_text(json.dumps(data))
  r=subprocess.run(['python3','-B',str(I/'assess_invariance.py'),str(path)],capture_output=True,text=True);results.append({'name':label,'original_assessor_false_pass':r.returncode==0,'stdout':r.stdout,'stderr':r.stderr})
assert all(x['original_assessor_false_pass']for x in results)
(P/'original-false-pass-checks.json').write_text(json.dumps({'candidate_calls':0,'method':'saved old baseline with source-only corruption, never backend execution','witnesses':results},indent=2)+'\n');print(len(results),'source-only original false passes retained')
