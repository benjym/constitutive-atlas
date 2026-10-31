from pathlib import Path
import shutil,json,struct,hashlib,subprocess
root=Path('/Users/bmar5496/code/constitutive-atlas');s=Path(__file__).parent
old=root/'catalogue/investigations/mc-laboratory-preview-v1';corrected=root/'catalogue/investigations/mc-preview-envelope-v2'
for name in ['models','reference']:
 shutil.copytree(old/name,s/name,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(root/'cpp',s/'frozen/cpp')
for directory,glob in [('atlas','*.py'),('schemas','*.json')]:
 for p in (root/directory).rglob(glob):
  out=s/'frozen'/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
for name in ['source-input.json']:
 shutil.copyfile(old/name,s/name)
shutil.copyfile(old/'CMakeLists.txt',s/'CMakeLists.txt')
shutil.copyfile(corrected/'assess_parity.py',s/'assess_parity.py')
inputs=json.loads((s/'source-input.json').read_text());paths={p['id']:p for p in inputs['paths']}
requests=json.loads((old/'requests.json').read_text())
for r in requests:
 p=paths[r['id']];controls=[0.]+[float.fromhex(x)for x in p['control_targets']]
 assert len(controls)==r['steps']+1 and p['protocol']==r['protocol']
 assert [(b-a).hex() for a,b in zip(controls,controls[1:])]==p['control_deltas']
 r['mode']='run-controls';r['loading_version']='laboratory-controls-0.1';r['controls_bits_csv']=','.join(struct.pack('>d',x).hex() for x in controls)
(s/'requests.json').write_text(json.dumps(requests,indent=2,sort_keys=True)+'\n')
policy=json.loads((old/'acceptance-paths.json').read_text());policy.update(identity='mc-explicit-controls-finite-path-policy-v1',control_uncertainty='Exact frozen independent caller bit patterns, including RN-subtracted original intended deltas. No backend waveform generation. Exact bit echo required in addition to unchanged source/control/parity bounds.',claims=policy['claims']+' Legacy cyclic browser behavior is not covered or silently reinterpreted.')
(s/'acceptance-paths.json').write_text(json.dumps(policy,indent=2,sort_keys=True)+'\n')
oldassess=(corrected/'assess_paths.py').read_text()
newassess=oldassess.replace('import json,math,sys,hashlib','import json,math,sys,hashlib,struct')
oldtext="  for k in ('protocol','steps','cycles'):assert type(r[k])is int and r[k]==req[k]\n  assert finite(r['target'])==req['target']"
newtext="""  for k in ('protocol','steps'):assert type(r[k])is int and r[k]==req[k]
  assert 'cycles'not in r and 'target'not in r
  assert r['api_version']=='experimental-laboratory-controls-0.1'
  assert r['loading']['version']==req['loading_version']=='laboratory-controls-0.1'
  assert r['loading']['encoding']=='ieee754-binary64-hex'
  expected_bits=req['controls_bits_csv'].split(',')
  assert len(expected_bits)==req['steps']+1
  assert r['loading']['controls_bits']==expected_bits
  assert [struct.pack('>d',finite(x)).hex() for x in vector(r['loading']['controls'],len(expected_bits))]==expected_bits
  assert [struct.pack('>d',finite(x['control'])).hex()for x in r['points']]==expected_bits"""
assert oldtext in newassess;newassess=newassess.replace(oldtext,newtext)
(s/'assess_paths.py').write_text(newassess)
# Freeze bindings to immutable earlier reference/policy/source/serializer bytes.
provenance={}
for p in [old/'source-input.json',old/'requests.json',old/'acceptance-paths.json',corrected/'assess_paths.py',corrected/'assess_parity.py',root/'cpp/main.cpp',root/'cpp/include/atlas/solver.hpp',old/'generated/models.hpp',old/'generated/models.json']:
 provenance[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
(s/'parent-provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
r=subprocess.run(['python3','-B','-m','atlas.compiler',str(s/'generated'),str(s/'models')],cwd=root,text=True,capture_output=True)
(s/'generation.json').write_text(json.dumps({'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
assert r.returncode==0,r.stderr
for name in ['models.hpp','models.json']:assert(s/'generated'/name).read_bytes()==(old/'generated'/name).read_bytes(),name
print('Prepared14 exact-input requests,834points, unchanged10-model generated catalogue and independent references.')
