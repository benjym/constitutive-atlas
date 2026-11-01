"""Verify current policy sources and retained historical policy receipts."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def verify():
    packet=Path(__file__).resolve().parent
    manifest=json.loads((packet/'manifest.json').read_text())
    for name,pin in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,name
    edges=legacy=0
    for folder in (packet,packet/'reviewer-guide-archive'):
        plan=json.loads((folder/'archive-plan.json').read_text())
        for row in plan['references']:
            checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']);edges+=1
        for row in plan.get('legacy_references_preserved_by_snapshot',[]):
            assert hashlib.sha256((ROOT/row['document']).read_bytes()).hexdigest()==row['document_sha256']
            checked_receipt(ROOT,(folder/'archive-plan.json').relative_to(ROOT),row['original_path'],row['sha256']);legacy+=1
    return {'pass':True,'original_receipt_edges':edges,'preserved_legacy_references':legacy}

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
