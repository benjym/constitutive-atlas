"""Read-only correction/source closure verification, no subprocesses."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,ast
D=Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=json.loads((D/'manifest.json').read_text())
    assert {str(p.relative_to(D))for p in D.rglob('*')if p.is_file()}==set(manifest)|{'manifest.json'}
    assert all(h(D/n)==v for n,v in manifest.items())
    prep=json.loads((D/'preparation.json').read_text());old=Path(prep['prior_source_directory']);new=Path(prep['source_directory'])
    assert all(h(old/n)==v for n,v in prep['prior592'].items())
    source=json.loads((D/'source-freeze.json').read_text())['source_files']
    assert {str(p.relative_to(new)):h(p)for p in new.rglob('*')if p.is_file()}==source and len(source)==592
    assert {n for n,v in prep['prior592'].items()if source[n]!=v}==set(prep['authorized_changes'])
    assert not any(p.is_symlink()or p.name=='__pycache__'or p.suffix=='.pyc'for p in new.rglob('*'))
    assert all(h(Path(p))==v for p,v in json.loads((D/'inputs.json').read_text()).items())
    for p in (D/'files').rglob('*.py'):
        assert p.read_bytes()==(new/p.relative_to(D/'files')).read_bytes();ast.parse(p.read_text())
    proof=json.loads((D/'legitimate-format-proof.json').read_text())
    assert h(D/'legitimate-CTestTestfile.cmake')==proof['original_sha256']
    print(json.dumps({'status':'passed','source_files':len(source),'v2_source592_unchanged':True,'changed':prep['authorized_changes'],'builds':0,'compiled_calls':0}))
if __name__=='__main__':main()
