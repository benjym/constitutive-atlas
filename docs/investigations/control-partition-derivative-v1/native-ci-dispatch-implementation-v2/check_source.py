"""Verify corrected source freeze and preservation without program invocation."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads((D/'manifest.json').read_text())
    assert {str(p.relative_to(D))for p in D.rglob('*')if p.is_file()}==set(manifest)|{'manifest.json'}
    assert all(h(D/n)==v for n,v in manifest.items())
    prep=json.loads((D/'preparation.json').read_text());old=Path(prep['prior_source_directory']);new=Path(prep['new_source_directory'])
    assert all(h(old/n)==v for n,v in prep['prior591'].items())
    freeze=json.loads((D/'source-freeze.json').read_text())
    actual={str(p.relative_to(new)):h(p)for p in new.rglob('*')if p.is_file()}
    assert actual==freeze['source_files']and len(actual)==592
    changed={n for n,v in prep['prior591'].items()if actual[n]!=v}
    assert changed==set(prep['authorized_changes'])
    assert set(actual)-set(prep['prior591'])=={'tools/test_scalar_functions.py'}
    overlay=json.loads((D/'authorized-scalar-support-overlay.json').read_text())
    assert h(new/overlay['path'])==overlay['sha256']
    assert not any(p.name=='__pycache__'or p.suffix=='.pyc'or p.is_symlink()for p in new.rglob('*'))
    for p in (D/'files').rglob('*'):
        if p.is_file():
            assert p.read_bytes()==(new/p.relative_to(D/'files')).read_bytes()
            if p.suffix=='.py':ast.parse(p.read_text())
    print(json.dumps({'status':'passed','source_files':len(actual),'v1_source591_unchanged':True,'changed':sorted(changed),'support_additions':1,'builds':0,'compiled_calls':0}))
if __name__=='__main__':main()
