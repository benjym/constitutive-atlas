from pathlib import Path
import json,gzip,re,tempfile,shutil,subprocess,sys,hashlib
P=Path(__file__).resolve().parent
original=(P/'generated-original/models.hpp').read_text();traced=(P/'generated/models.hpp').read_text()
s=traced
for line in ('inline thread_local int study_selected_branch=-1;\n','inline thread_local int study_failure_line=-1;\n','inline thread_local std::array<double,24> study_values{};\n'):
 assert s.count(line)==1;s=s.replace(line,'')
s=re.sub(r'^study_values\[\d+\]=atlas::value\(\w+\);\n','',s,flags=re.M)
s=s.replace('study_selected_branch=int(atlas::value(branch));\n','')
s=re.sub(r'\{ study_failure_line=\d+; return false; \}', 'return false;',s)
assert s==original,'instrumentation changed arithmetic/control'
rows=json.loads((P/'requests.json').read_text());names=json.loads((P/'wire.json').read_text())['parameters'];lines=gzip.decompress((P/'requests.txt.gz').read_bytes()).decode().splitlines();assert len(rows)==len(lines)==862
for row,line in zip(rows,lines):
 words=[row['id'],row['mode'],row['kind'],str(int(row['check_initial'])),str(row['max_iterations']),str(row['max_depth'])]+[row['parameters'][n]for n in names]+row['current']+row['parent']+row['loading']+[v for seed in row['seeds']for f in('current','parent','loading')for v in seed[f]]
 assert words==line.split();assert len(words)==714
# Recreate all generated model/transport artifacts from isolated copied source.
root=Path(tempfile.mkdtemp(prefix='mc-source-replay-',dir='/private/tmp'));capsule=root/'source';shutil.copytree(P/'frozen',capsule)
ref=capsule/'docs/reviews/mc-stored-reference-v1';ref.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(P/'reference',ref)
out=root/'generated';out.mkdir();shutil.copytree(P/'supplemental-reference',out/'supplemental-reference');env={'PYTHONDONTWRITEBYTECODE':'1'}
r=subprocess.run([sys.executable,'-B',str(P/'generate.py'),str(capsule),str(out)],capture_output=True)
assert r.returncode==0,r.stderr.decode()
files=['generated-original/models.hpp','generated-original/models.json','generated/models.hpp','generated/instrumentation.patch','requests.json','requests.txt.gz','wire.json','trace-fields.json','generation-results.json']
for name in files:assert (out/name).read_bytes()==(P/name).read_bytes(),name
result={'passed':True,'instrumentation_arithmetic_control_unchanged':True,'literal_request_count':len(rows),'wire_tokens_per_request':714,'exact_copied_source_generated_files':files,'candidate_calls':0,'compiled_observations':0}
print(json.dumps(result,indent=2))
