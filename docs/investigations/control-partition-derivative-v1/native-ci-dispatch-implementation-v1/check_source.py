"""Verify the isolated implementation freeze, without invoking any program."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    manifest=json.loads((D/'manifest.json').read_text())
    actual={str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()}
    assert actual==set(manifest)|{'manifest.json'},'packet inventory changed'
    for name,digest in manifest.items():assert sha((D/name).read_bytes())==digest,name
    freeze=json.loads((D/'source-freeze.json').read_text());source=Path(freeze['source_directory'])
    actual={str(p.relative_to(source)):sha(p.read_bytes())for p in source.rglob('*')if p.is_file()}
    assert actual==freeze['source_files'],'isolated source changed'
    assert len(actual)==591
    assert not any(p.is_symlink() or p.name=='__pycache__' or p.suffix=='.pyc'for p in source.rglob('*'))
    original=json.loads((D/'preparation.json').read_text());oldsource=Path(original['original_source'])
    assert all(sha((oldsource/n).read_bytes())==h for n,h in original['original582'].items())
    for p in (D/'files').rglob('*.py'):ast.parse(p.read_text())
    assert all((source/n).read_bytes()==(D/'files'/n).read_bytes()for n in actual if (D/'files'/n).is_file())
    print(json.dumps({'status':'passed','packet_files':len(manifest),'source_files':len(actual),'original582_unchanged':True,'compiled_calls':0,'builds':0}))
if __name__=='__main__':main()
