"""Verify exact bounded admission and retained evidence; no material execution."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
record=json.loads((BASE/'approval.json').read_text())
registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
assert [r for r in registry['models'] if r['model_id']==record['model_id']]==[record]
assert record['status']=='approved' and record['experimental_validation']=='not_assessed'
assert record['review']['human_scientific_signature'] is False
for binding in [record['definition'],*record['supporting_files']]:
    assert hashlib.sha256((ROOT/binding['path']).read_bytes()).hexdigest()==binding['sha256'],binding['path']
model=json.loads((ROOT/record['definition']['path']).read_text())
assert model['id']==record['model_id'] and model['status']=='draft'
assert len(record['limitations'])==6
assert (ROOT/record['dossier']).is_file()
for script,args in [('docs/ingestion/matsuoka-nakai/verify_packet.py',[]),('docs/ingestion/matsuoka-nakai/working-v1/verify.py',[]),('docs/reviews/nh2004-scientific-v1/verify_review.py',[])]:
    subprocess.run([sys.executable,str(ROOT/script),*args],cwd=ROOT,check=True)
print('PASS: bounded NH2004 approval, exact model/supporting hashes, retained source/working/review evidence; no compiled calls.')
