"""Source-only proposal check; never builds or executes a material driver."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.evidence import checked_receipt
from atlas.model import load, validate
from atlas.structure import check
P=Path(__file__).resolve().parent

def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(condition,message):
    if not condition: raise ValueError(message)

def check_contract(qualified, proposal, review, decision):
    validate(proposal)
    require(set(qualified)==set(proposal), 'definition keys changed')
    require({k for k in proposal if proposal[k]!=qualified[k]}=={'id','name','description'}, 'implementation changed')
    require(proposal['id']=='tresca-associated-perfect-bk2022v1-be' and proposal['status']=='draft', 'proposal identity/status')
    check(review,read(ROOT/'schemas/review.schema.json'))
    require(review['model']=={'id':proposal['id'],'definition_sha256':decision['proposed_definition_sha256']}, 'review definition binding')
    require(review['status']=='pending' and review['independent'] is False and review['unresolved'], 'review promotion')
    require('reviewer' not in review and 'reviewed_at' not in review, 'unsigned review has signature')
    require(review['evidence_ids']==[], 'unregistered numerical evidence')
    require(review['dossier']=='docs/models/'+proposal['id']+'.md' and (ROOT/review['dossier']).is_file(), 'canonical dossier')
    require(decision['decision']=='prepare-separate-local-draft-integration' and decision['retain_status']=='draft' and decision['source_review']=='pending', 'decision changed')
    require(all(decision[k] is False for k in ('independent','scientific_admission','experimental_validation','public_installation_this_task','deployment_authorized')), 'unsupported admission or deployment')

def numeric_sections(header):
    # All numerical text, excluding only Model identity rows and catalogue metadata.
    return (header[header.index('inline bool solution_constraints_0'):header.index('inline const std::vector<Model>& models()')],
            header[header.index('template<class T> bool generated_solution_constraints'):header.index('inline const char* catalogue_hash')])

def verify():
    if (P/'manifest.json').exists():
        for item in read(P/'manifest.json')['files']:
            checked_receipt(ROOT,(P/'manifest.json').relative_to(ROOT),item['path'],item['sha256'])
    pins=read(P/'source-pins.json')
    resolved={path:checked_receipt(ROOT,(P/'source-pins.json').relative_to(ROOT),path,h) for path,h in pins.items()}
    baseline=read(P/'baseline-public-models.json')
    require(len(baseline['models'])==9 and baseline['registered_review_count']==18,'historical baseline identity')
    for item in baseline['models']:
        checked_receipt(ROOT,(P/'baseline-public-models.json').relative_to(ROOT),item['path'],item['sha256'])
    qualified_path=resolved['catalogue/investigations/tresca-certified-corners-v5/frozen/model.json']
    qualified=load(qualified_path)
    proposal=load(P/'public-model.json'); review=read(P/'pending-review.json'); decision=read(P/'decision.json')
    require(sha(qualified_path)==decision['qualified_definition_sha256'], 'qualified hash')
    require(sha(P/'public-model.json')==decision['proposed_definition_sha256'], 'proposal hash')
    check_contract(qualified,proposal,review,decision)
    with tempfile.TemporaryDirectory() as td:
        a=Path(td)/'qualified'; b=Path(td)/'proposed'
        generate(a,[qualified_path]); generate(b,[P/'public-model.json'])
        require(numeric_sections((a/'models.hpp').read_text())==numeric_sections((b/'models.hpp').read_text()),'generated numerical code changed')
    return {'version':'tresca-source-integration-checks-0.1','source_receipts':len(pins),'baseline_models':9,'baseline_registered_pending_reviews':18,'changed_definition_keys':['description','id','name'],'generated_numerical_sections_identical':True,'review_pending_unsigned':True,'material_execution':False,'public_installation':False,'overall_pass':True}

if __name__=='__main__': print(json.dumps(verify(),indent=2))
