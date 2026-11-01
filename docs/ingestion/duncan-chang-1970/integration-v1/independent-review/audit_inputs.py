"""Independent prospective atlas input/identity audit; no compiled execution."""
from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[3];sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model='duncan-chang-1970-endpoint-average';digest='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
assert sha(ROOT/'models'/f'{model}.json')==digest
review=ROOT/'catalogue/agent-reviews'/f'{model}-agent-v1.json';r=validate_review(review,for_approval=True)
assert review.read_bytes()==(B.parent/'material-v1/independent-review/e5-v1/proposed-agent-review.json').read_bytes()
entry=approval_entry(review);assert entry==read(B/'approval-entry.json')
registry=read(ROOT/'catalogue/approved-models.json');assert next(x for x in registry['models'] if x['model_id']==model)==entry
package=read(ROOT/'catalogue/laboratory-package-policy.json');profile=read(ROOT/'catalogue/laboratory-profile-policy.json')
old=read(ROOT/'catalogue/source-snapshots/84fe14c4cf8c7bcb36f9edf3ad0d4e5423b8ff5d312e57938794a863ec3b7d4b/catalogue/laboratory-package-policy.json')
assert len(package['models'])==14 and package['models'].pop(model)==digest
assert package['models']==old['models'] and package['declared_failures']==old['declared_failures']
for name,h in old['models'].items():assert sha(ROOT/'models'/f'{name}.json')==h
cases=read(B/'scoped-cases.json');previous=read(ROOT/'docs/ingestion/original-cam-clay/integration-v1/scoped-cases.json')
assert len(previous)==35 and cases[:-1]==previous and len(cases)==36
last=cases[-1];spec=last['specification'];assert last['expected_ok'] and last['expected_points']==5 and spec['model']==model and spec['target']==0
assert spec['initial']==[100000,100000,100000,0,0,0,0] and spec['loading']['controls_bits']==['0000000000000000']*5
assert profile['parity_relative_tolerance']==1e-10 and profile['case_count']==36
assert profile['supported_policy']['sha256']==sha(ROOT/'catalogue/laboratory-package-policy.json') and profile['cases']['sha256']==sha(B/'scoped-cases.json')
presets=read(B/'preset-inputs.json');assert presets==read(B.parent/'material-v1/execution-v2/requests.json')['presets'] and len(presets)==2
assert all('loading' not in row for row in presets)
manifest=read(ROOT/'catalogue/manifest.json')['models'];assert len([x for x in manifest if x['id']==model])==1
new=next(x for x in manifest if x['id']==model);family=next(x for x in manifest if x['id']=='duncan-chang-1970')
assert new['executable'] and new['dossier']==f'docs/models/{model}.md' and not family.get('executable',False)
preservation=read(B/'preservation.json');replaced_inventory=[]
for row in preservation['bindings']:
 archived=ROOT/row['archived_path'];assert sha(archived)==row['sha256']
 if row['document']=='catalogue/laboratory-profile-policy.json':
  assert row['original_path']=='catalogue/laboratory-package-policy.json'
  archived_profile=read(ROOT/'catalogue/source-snapshots/440ae4a548113880a7c3618c5cc54435e7c1593a923e0756a98f6d1fe7e01ccf/catalogue/laboratory-profile-policy.json')
  assert archived_profile['supported_policy']==dict(path=row['original_path'],sha256=row['sha256'])
  replaced_inventory.append(row['document'])
 else:
  resolved=checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']);assert sha(resolved)==row['sha256']
freeze=read(B/'freeze.json')
for path,h in freeze['files'].items():assert sha(ROOT/freeze['source_root']/path)==h,path
for path,h in freeze['generated'].items():assert sha(B/path)==h,path
generated=read(B/'frozen/generated/models.json')
print(json.dumps({'pass':True,'exact_installed_model_and_e5_approval_valid':True,'old_definition_hashes_preserved':13,'old_scoped_case_data_preserved':35,'added_exact_zero_hold_cases':1,'unchanged_strict_parity_budget':1e-10,'e4_presets_unchanged_legacy_loading':2,'preservation_bindings_checked':len(preservation['bindings']),'intentional_current_inventory_replacements_checked_via_archived_original':replaced_inventory,'frozen_source_inputs_verified':len(freeze['files']),'generated_files_verified':len(freeze['generated']),'catalogue_hash':freeze['catalogue_hash'],'compiled_calls':0},indent=2))
