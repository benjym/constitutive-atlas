from pathlib import Path
import sys,subprocess,tempfile,json,hashlib
P=Path(__file__).resolve().parent
out=Path(tempfile.mkdtemp(prefix='mc-policy-source-replay-',dir='/private/tmp'))
manifest=json.loads((P/'policy-audit/manifest.json').read_text())
for name,r in manifest['files'].items():
 b=(P/'policy-audit'/name).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],name
for name,h in json.loads((P/'policy-audit/supplemental/prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((P/'policy-audit'/name).read_bytes()).hexdigest()==h,name
commands=[('manufacture',[str(P/'policy-audit/supplement.py'),str(P/'reference'),str(out/'supplement')]),('classify',[str(P/'policy-audit/classify.py'),str(P/'reference/corpus/inputs.json'),str(P/'reference/reference-p360.json.gz')]),('selfcheck',[str(P/'policy-audit/selfcheck.py')])]
for label,args in commands:
 result=subprocess.run([sys.executable,'-B',*args],capture_output=True);(out/(label+'.stdout')).write_bytes(result.stdout);(out/(label+'.stderr')).write_bytes(result.stderr);assert result.returncode==0,(label,result.stderr)
 if label=='classify':assert json.loads(result.stdout)==json.loads((P/'policy-audit/policy-table.json').read_text())
 if label=='selfcheck':assert json.loads(result.stdout)==json.loads((P/'policy-audit/selfcheck-results.json').read_text())
assert (out/'supplement/inputs.json').read_bytes()==(P/'supplemental-reference/inputs.json').read_bytes()
for precision in(280,360):
 name=f'reference-p{precision}.json.gz'
 cmd=[sys.executable,'-B',str(P/'supplemental-reference/reference-source/generate.py'),str(out/'supplement/inputs.json'),str(precision),str(out/name)]
 r=subprocess.run(cmd,capture_output=True);(out/(str(precision)+'.stdout')).write_bytes(r.stdout);(out/(str(precision)+'.stderr')).write_bytes(r.stderr);assert r.returncode==0
 assert (out/name).read_bytes()==(P/'supplemental-reference'/name).read_bytes(),name
r=subprocess.run([sys.executable,'-B',str(P/'supplemental-reference/reference-source/check.py'),str(out/'supplement/inputs.json'),str(out/'reference-p280.json.gz'),str(out/'reference-p360.json.gz'),str(P/'supplemental-reference/reference-source/reference-policy.json')],capture_output=True)
assert r.returncode==0,r.stderr
assert json.loads(r.stdout)==json.loads((P/'supplemental-reference/check-results.json').read_text())
print(json.dumps({'passed':True,'policy_manifest_entries':len(manifest['files']),'source_manufacture_exact':True,'supplemental_both_gzip_byte_exact':True,'classification_and8397selfchecks_exact':True,'candidate_calls':0,'compiled_observations':0,'logs':str(out)},indent=2))
