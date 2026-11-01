"""Restore the exact E5-reviewed generated Bingham public engine; never build it."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import approval_entry,validate_review
MODEL='bingham-comsol63-mises-perfect-zero-spin-ode'
REVIEW='catalogue/agent-reviews/bingham-comsol63-agent-v1.json'
PACKET='docs/ingestion/bingham-comsol63/asset-provision-v1/'
INDEX=PACKET+'INDEX.json'
ARCHIVE=PACKET+'qualified-assets.zip'
MEMBERS={'bingham.mjs','bingham.wasm','generated/models.json'}
LIMIT=16*1024*1024

def sha(data):return hashlib.sha256(data).hexdigest()
def provision(destination):
    review=validate_review(ROOT/REVIEW,root=ROOT,for_approval=True)
    approval=approval_entry(ROOT/REVIEW,root=ROOT)
    registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    matches=[r for r in registry if r['model_id']==MODEL]
    if matches!=[approval] or review['model']['id']!=MODEL:raise ValueError('Exact Bingham approval required')
    pins={r['path']:r['sha256'] for r in review['artifacts']}
    raw_index=(ROOT/INDEX).read_bytes();raw_archive=(ROOT/ARCHIVE).read_bytes()
    if sha(raw_index)!=pins.get(INDEX) or sha(raw_archive)!=pins.get(ARCHIVE):raise ValueError('Asset index/archive not E5-bound')
    index=json.loads(raw_index)
    if index.get('model')!=MODEL or index.get('status')!='passed' or set(index.get('files',{}))!=MEMBERS or index.get('archive')!={'path':ARCHIVE,'sha256':sha(raw_archive)}:raise ValueError('Invalid exact asset index')
    if len(raw_archive)>LIMIT:raise ValueError('Archive exceeds limit')
    files={}
    with zipfile.ZipFile(io.BytesIO(raw_archive)) as z:
        entries=z.infolist()
        if len(entries)!=len(MEMBERS) or {x.filename for x in entries}!=MEMBERS:raise ValueError('Unexpected archive members')
        for info in entries:
            if info.file_size>LIMIT or info.is_dir() or (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Invalid archive member')
            data=z.read(info)
            if sha(data)!=index['files'][info.filename]:raise ValueError('Changed qualified asset')
            files[info.filename]=data
    destination=Path(destination)
    for name,data in files.items():
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print('Restored exact reviewed Bingham engine:',destination)
    return index
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'build-bingham-public');a=ap.parse_args();provision(a.output)
