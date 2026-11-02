"""Independent prospective checks; no compiled invocation and no author-file writes."""
from pathlib import Path
import hashlib,json,sys,zipfile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];V2=OUT.parent/'execution-v2';V1=OUT.parent/'execution-v1';sys.path.insert(0,str(V2));sha=lambda b:hashlib.sha256(b).hexdigest();pins={}
def read(p):
 p=Path(p);b=p.read_bytes();pins[str(p.relative_to(ROOT))]=sha(b);return b
def load(p):return json.loads(read(p))
f=load(V2/'freeze-v1.json');assert sha(read(V2/'freeze-v1.json'))=='2aa8e5e4b3ed4dce7fc74fd290cbf5adf2fef96a6afc344fbf7e13da598b9f0a'
for n,h in f['files'].items():assert sha(read(ROOT/n))==h
s=load(V2/'source-bindings.json')
for group in ['source_files','prior_v1_evidence']:
 for n,h in s[group].items():assert sha(read(ROOT/n))==h
old=load(V1/'cases.json')['cases'];new=load(V2/'cases.json')['cases'];assert len(old)==len(new)==136 and [x['id'] for x in old]==[x['id'] for x in new];radial=0
for a,b in zip(old,new):
 if a['kind']=='schedule':
  for k in ['specification','argv','args','types','call','references']:assert a[k]==b[k]
 else:
  spec=b['specification'];parse=lambda x:[float(z) for z in x.split(',')] if x else [];assert spec['parameters']==parse(a['args'][1]);assert spec['initial']==parse(a['args'][2]);assert spec['initial_strain_rate']==parse(a['args'][3]);assert spec['start_time']==a['args'][4];assert sum(x['duration'] for x in spec['segments'])==a['args'][5]
  for seg in spec['segments']:assert [c['value'] for c in seg['controls']]==parse(a['args'][3])
  if a['ok']:assert b['references'][-1]['state']==a['expected'] and b['references'][-1]['stress']==a['expected_stress']
  if a['id'].startswith('radial-'):radial+=1
for n in ['oracle.py','parity.py','expected-catalogue.json','reference-convergence.json']:assert read(V2/n)==read(V1/n)
closure=load(V1/'build-inputs-v1.json');assert len(closure['files'])==138
for n,h in closure['files'].items():assert sha(read(ROOT/n))==h
archive=load(V1/'frozen-source-archive-v1/INDEX.json');assert archive['files']==closure['files'];assert sha(read(ROOT/archive['build_input_manifest']))==archive['build_input_manifest_sha256'];assert sha(read(ROOT/archive['archive']))==archive['archive_sha256']
with zipfile.ZipFile(ROOT/archive['archive']) as z:
 assert set(z.namelist())==set(closure['files']) and len(z.namelist())==138
 for n,h in closure['files'].items():assert sha(z.read(n))==h
# Preserve original synthetic source exactly, but route its single output to this owned directory.
code=read(V2/'synthetic_checks.py').decode().replace("(BASE/'synthetic-checks.json').write_text", "(OUT/'synthetic-results.json').write_text")
exec(compile(code,str(V2/'synthetic_checks.py'),'exec'),{'OUT':OUT,'__name__':'reviewer_synthetic_checks'})
synthetic=load(OUT/'synthetic-results.json');assert synthetic['positive_synthetic_cases']==136 and synthetic['negative_mutations_rejected']==25
result=dict(compiled_calls=0,builds=0,freeze_verified=True,new_case_count=136,original_radial_histories_exact=radial,source_bindings_verified=len(s['source_files']),old_full_build_source_pins_verified=138,old_durable_archive_all_entries_verified=138,synthetic_cases_pass=136,synthetic_mutations_rejected=25,scope='Prospective BE schedule only; original failed midpoint excluded')
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'BINDINGS.json').write_text(json.dumps(dict(reviewer='/root/bingham_review',files=pins),indent=2)+'\n');print(json.dumps(result,indent=2))
