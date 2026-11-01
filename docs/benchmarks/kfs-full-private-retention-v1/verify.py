"""Verify private retained bytes without originals, data imports or process execution."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def verify(base,records):
    base=Path(base).resolve();seen=set();total=0
    for item in records:
        name=Path(item['retained_path'])
        if name.is_absolute() or '..' in name.parts or name==Path('.') or name in seen:
            raise ValueError('unsafe or duplicate retained path')
        seen.add(name);p=base/name
        if any(q.is_symlink() for q in [p,*p.parents] if q!=base and q.is_relative_to(base)):
            raise ValueError('retained symlink')
        if not p.resolve().is_relative_to(base):raise ValueError('retained path escapes root')
        raw=p.read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('retained bytes differ: '+str(name))
        if p.stat().st_mode&0o111:raise ValueError('retained file is executable: '+str(name))
        total+=len(raw)
    return {'files':len(seen),'bytes':total}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--private-root',type=Path);args=parser.parse_args()
    receipt=json.loads((HERE/'receipts.json').read_text())
    result=verify(args.private_root or ROOT/receipt['private_root'],receipt['files'])
    print(json.dumps({'result':'pass',**result,'original_paths_required':False,'compiled_execution':False}))
