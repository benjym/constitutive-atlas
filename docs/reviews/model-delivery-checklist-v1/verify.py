"""Verify delivery instructions, phase coverage and original receipt identities."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def verify():
    packet=Path(__file__).resolve().parent
    manifest=json.loads((packet/'manifest.json').read_text())
    for name,pin in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,name
    plan=json.loads((packet/'archive-plan.json').read_text())
    for row in plan['references']:
        checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])
    for row in plan.get('legacy_references_preserved_by_snapshot',[]):
        assert hashlib.sha256((ROOT/row['document']).read_bytes()).hexdigest()==row['document_sha256']
        checked_receipt(ROOT,(packet/'archive-plan.json').relative_to(ROOT),row['original_path'],row['sha256'])
    checklist=(ROOT/'docs/MODEL_DELIVERY_CHECKLIST.md').read_text()
    ledger=(ROOT/'docs/ingestion/DELIVERY_TEMPLATE.md').read_text()
    for stage in range(9):
        assert len(re.findall(r'^## E'+str(stage)+r' — ',checklist,re.M))==1
        assert len(re.findall(r'^- \[ \] \*\*E'+str(stage)+r' — ',ledger,re.M))==1
    links=0
    for name in ('AGENTS.md','ROADMAP.md','docs/MODEL_DELIVERY_CHECKLIST.md','docs/ingestion/DELIVERY_TEMPLATE.md','docs/ingestion/TEMPLATE.md','docs/AGENT_REVIEW_POLICY.md'):
        path=ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' in target or target.startswith('#'):continue
            target=target.split('#')[0]
            if target:assert (path.parent/target).exists(),(name,target)
            links+=1
    return {'pass':True,'stages':9,'local_links':links,'original_receipt_edges':len(plan['references'])}

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
