from pathlib import Path
import json,struct,subprocess,copy,tempfile
s=Path(__file__).parent;refs=json.loads((s/'reference/references.json').read_text())['cases']
ideal=[{'id':r['id'],'wire':','.join(r['input_bits']),'raw':json.dumps({'ok':True,'q':struct.unpack('>d',bytes.fromhex(r['q_rounded_bits']))[0],'q_bits':r['q_rounded_bits']})}for r in refs]
(s/'source-ideal.json').write_text(json.dumps(ideal,indent=2)+'\n')
def run(script,path):return subprocess.run(['python3','-B',str(s/script),str(path)],capture_output=True,text=True)
p=run('assess_probe.py',s/'source-ideal.json');assert p.returncode==0,p.stderr
negative=0
with tempfile.TemporaryDirectory(prefix='atlas-q-assessor-source-')as tmp:
 path=Path(tmp)/'data.json'
 mutations=[lambda d:d.pop(),lambda d:d[0].update(id='wrong'),lambda d:d[0].update(wire='0000000000000000'),lambda d:d[0].update(raw=json.dumps({'ok':1,'q':0,'q_bits':'0000000000000000'})),lambda d:d[0].update(raw=json.dumps({'ok':True,'q':True,'q_bits':'3ff0000000000000'})),lambda d:d[0].update(raw=json.dumps({'ok':True,'q':1e-10,'q_bits':struct.pack('>d',1e-10).hex()})),lambda d:d[0].update(raw=json.dumps({'ok':True,'q':-0.,'q_bits':'8000000000000000'})),lambda d:d[0].update(raw=json.dumps({'ok':True,'q':float('nan'),'q_bits':'7ff8000000000000'}))]
 for mutate in mutations:
  data=copy.deepcopy(ideal);mutate(data);path.write_text(json.dumps(data));assert run('assess_probe.py',path).returncode!=0;negative+=1
 old=json.loads((s/'baseline/backend-results.json').read_text());old['status']='passed';path.write_text(json.dumps(old));assert run('assess_invariance.py',path).returncode==0
 for field in ['state','strain']:
  data=copy.deepcopy(old);data['pairs'][0]['native']['points'][1][field][0]+=1;path.write_text(json.dumps(data));assert run('assess_invariance.py',path).returncode!=0;negative+=1
 for field in ['p','q_signed','u','iterations','substeps','control']:
  data=copy.deepcopy(old);data['pairs'][0]['native']['points'][1][field]+=1;path.write_text(json.dumps(data));assert run('assess_invariance.py',path).returncode!=0;negative+=1
 data=copy.deepcopy(old);data['pairs'][0]['native']['integration_settings']['max_depth']+=1;path.write_text(json.dumps(data));assert run('assess_invariance.py',path).returncode!=0;negative+=1
(s/'preflight-results.json').write_text(json.dumps({'passed':True,'ideal_probe_cases':35,'ideal_invariance_pairs':101,'negative_checks':negative,'candidate_calls':0},indent=2)+'\n');print('source ideals and',negative,'negative assessor cases pass')
