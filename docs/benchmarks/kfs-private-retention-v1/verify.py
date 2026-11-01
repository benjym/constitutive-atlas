"""Check retained private evidence without executing tools or interpreting data arrays."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def verify(base,records):
    base=Path(base).resolve()
    for item in records:
        name=Path(item['retained_path']);p=(base/name).resolve()
        if name.is_absolute() or '..' in name.parts or not p.is_relative_to(base):
            raise ValueError('unsafe retained path')
        raw=p.read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('retained bytes differ: '+str(name))
    return len(records)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root',type=Path)
    args=parser.parse_args()
    receipt=json.loads((HERE/'receipts.json').read_text())
    total=verify(args.private_root or ROOT/receipt['private_root'],receipt['files'])
    print(f'PASS: {total} exact retained private files; no compiled execution')
