"""Verify explicit bounded approval and retained identity; no material execution."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(record):
    assert record['status']=='approved'
    assert record['approval_authority']['kind']=='explicit-user-instruction'
    assert record['approval_authority']['instruction']=="Ok let's add it as an approved model"
    assert record['review']['human_scientific_signature'] is False
    assert record['experimental_validation']=='not_assessed'
    assert record['deployment_authorized'] is False
    definition=record['definition'];assert digest(ROOT/definition['path'])==definition['sha256']
    assert definition['sha256']=='dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f'
    model=json.loads((ROOT/definition['path']).read_text())
    assert model['status']=='draft' and model['id']==record['model_id']
    scope=record['scope'];f=model['formulation']
    assert scope['kinematics']==f['kinematics']=='small_strain_3d'
    assert scope['frame']==f['frame']=='fixed_spatial'
    assert scope['objective_rate']==f['objective_rate']=='none'
    assert scope['stress_scope']==f['stress']['scope']=='total'
    assert scope['material_assumption']=='dry uncoupled material point'
    assert len(record['limitations'])==6
    for p in record['supporting_files']:assert digest(ROOT/p['path'])==p['sha256']
    for p in scope['examples']:assert (ROOT/p).is_file()
    assert (ROOT/record['dossier']).is_file()

record=json.loads((BASE/'approval.json').read_text());validate(record)
registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
entries=[r for r in registry['models'] if r['model_id']==record['model_id']]
assert entries==[record]
retention=json.loads((BASE/'source-retention.json').read_text());assert len(retention['sources'])==4
for source in retention['sources']:assert digest(Path(source['durable_private_path']))==source['sha256']
counts={}
for label,p in [('ingestion','docs/ingestion/maxwell-itasca900/manifest.json'),('execution','docs/ingestion/maxwell-itasca900/integration-v1/manifest.json'),('agent_review','docs/reviews/maxwell-scientific-agent-v1/manifest.json')]:
    manifest=json.loads((ROOT/p).read_text())
    for x in manifest['files']:assert digest(ROOT/x['path'])==x['sha256']
    counts[label]=len(manifest['files'])
corruptions=[]
for label,mutate in [('stale definition',lambda r:r['definition'].update(sha256='0'*64)),('fabricated signature',lambda r:r['review'].update(human_scientific_signature=True)),('widened rotation scope',lambda r:r['scope'].update(objective_rate='jaumann')),('changed evidence',lambda r:r['supporting_files'][0].update(sha256='0'*64))]:
    bad=copy.deepcopy(record);mutate(bad)
    try:validate(bad)
    except AssertionError:corruptions.append(label)
    else:raise AssertionError('accepted '+label)
result={'passed':True,'approval':'approved','model_sha256':record['definition']['sha256'],'retained_manifest_bindings':counts,'durable_private_sources_verified':4,'manufactured_corruptions_rejected':corruptions,'model_bytes_changed':False,'compiled_calls':0,'human_signature_inferred':False,'experimental_validation':'not_assessed'}
(BASE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
