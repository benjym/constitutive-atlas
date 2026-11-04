"""Archive-aware current-context verification; original historical helper unchanged."""
import hashlib,json
from pathlib import Path
from atlas.model import ROOT
from atlas.evidence import checked_receipt
from tests.historical_generation import contexts, public_models, public_paths, catalogue, generate
LEDGER=ROOT/'docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/historical-test-contexts.json'
LEDGER_SHA='910758a62e5e77f02c96f7a615ac14b6497ea3198e0c9a4e372656a03572d6db'

def verified(item):
    if hashlib.sha256(LEDGER.read_bytes()).hexdigest()!=LEDGER_SHA:
        raise ValueError('original historical ledger changed')
    path=(ROOT/item['path']).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('historical context path escapes root')
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
        path=checked_receipt(ROOT,LEDGER.relative_to(ROOT),item['path'],item['sha256'])
    if 'receipt' in item:
        document=json.loads(verified(item['receipt']).read_text())
        for key in item.get('receipt_keys',[item.get('receipt_key')]):document=document[key]
        if document!=item['sha256']:
            raise ValueError('historical source is not bound by its original receipt')
    return path
