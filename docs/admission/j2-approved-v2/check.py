"""Verify agent-approved exact J2 identity and retained evidence; no backend calls."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.agent_review import approval_entry, validate_review
from atlas.dsl import ValidationError
BASE=Path(__file__).resolve().parent
REVIEW=ROOT/'catalogue/agent-reviews/j2-linear-hardening-agent-v2.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check(record):
    assert record==approval_entry(REVIEW)
    assert record['definition']['sha256']=='a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b'
    assert record['experimental_validation']=='not_assessed' and record['deployment_authorized'] is False
    assert record['approval_authority']['kind']=='independent-agent-review'

def main():
    record=json.loads((BASE/'approval.json').read_text());check(record)
    review=validate_review(REVIEW,for_approval=True)
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
    assert [r for r in registry['models'] if r['model_id']==record['model_id']]==[record]
    candidate=ROOT/'docs/ingestion/j2-linear-hardening/candidate-v03-v2.json'
    assert sha(candidate)==record['definition']['sha256']
    assert sha(ROOT/'docs/ingestion/j2-linear-hardening/candidate-v03.json')=='619ea20bf932247962675e56b785398c7457749aafd28e2bcab94ba0dcc24852'
    sources=json.loads((ROOT/'docs/ingestion/j2-linear-hardening/source-receipts.json').read_text())['sources']
    for s in sources:assert sha(Path(s['private_path']))==s['sha256']
    for manifest in ('docs/ingestion/j2-linear-hardening/manifest.json',
                     'docs/ingestion/j2-linear-hardening/execution-v1/manifest.json',
                     'docs/ingestion/j2-linear-hardening/execution-v2/manifest.json'):
        bound=json.loads((ROOT/manifest).read_text())['files']
        if isinstance(bound,dict):
            bound=[dict(path=str(Path(manifest).parent/p),sha256=h) for p,h in bound.items()]
        for f in bound:
            assert sha(ROOT/f['path'])==f['sha256'],f['path']
    negatives=[]
    for name,mutate in [('stale model',lambda r:r['definition'].update(sha256='0'*64)),
                        ('broadened scope',lambda r:r['scope'].update(use='arbitrary finite rotations'))]:
        bad=copy.deepcopy(record);mutate(bad)
        try:check(bad)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('accepted '+name)
    for name,mutate in [('self review',lambda r:r['reviewer'].update(run_id=r['author_run_ids'][0])),
                        ('failed checklist',lambda r:r['checklist'][0].update(outcome='fail')),
                        ('unresolved blocker',lambda r:r['blocking_findings'].append('unresolved'))]:
        bad=copy.deepcopy(review);mutate(bad)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'review.json';p.write_text(json.dumps(bad))
            try:validate_review(p,for_approval=True)
            except ValidationError:negatives.append(name)
            else:raise AssertionError('accepted '+name)
    out=dict(passed=True,status='approved',authority='independent-agent-review',
             checklist_items=len(review['checklist']),private_source_hashes=len(sources),
             corruptions_rejected=negatives,model_sha256=record['definition']['sha256'],compiled_calls=0)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
