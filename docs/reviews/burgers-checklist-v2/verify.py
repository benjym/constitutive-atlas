"""Check reconciliation integrity; optional original-source/calculation replay."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review, approval_entry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main(private=False):
    manifest=json.loads((HERE/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        assert sha(ROOT/name)==digest,name
    for name,digest in json.loads((HERE/'preserved-history.json').read_text()).items():
        assert sha(ROOT/name)==digest,('historical bytes changed',name)
    record=ROOT/'catalogue/agent-reviews/burgers-agent-v2.json'
    review=validate_review(record,for_approval=True)
    assert approval_entry(record)==json.loads((HERE/'generated-approval.json').read_text())
    assert len(review['checklist'])==9 and all(x['outcome']=='pass' for x in review['checklist'])
    if private:
        p=subprocess.run([sys.executable,'-B',str(HERE/'check_review.py')],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert json.loads(p.stdout)==json.loads((HERE/'check-results.json').read_text())
    return {'review':review['id'],'accepted':True,'checklist_passes':9,
            'historical_bytes_preserved':True,'private_source_replay':private,
            'generated_entry_matches':True,'compiled_calls':0,'registry_mutated':False,
            'browser_interface_qualified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-sources',action='store_true')
    print(json.dumps(main(p.parse_args().private_sources),indent=2))
