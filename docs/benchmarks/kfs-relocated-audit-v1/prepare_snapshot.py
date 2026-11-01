"""Reconstruct exact public audit-source snapshot from repository/archive bytes."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze',type=Path,default=HERE/'freeze-v2.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();freeze=json.loads(args.freeze.read_text());historical=Path(freeze['historical_repository_root'])
    if args.output.exists():raise FileExistsError('Snapshot output must be new')
    sources=[];review='docs/benchmarks/kfs-development-agent-v1/manifest.json'
    for item in freeze['public_files']:
        relative=Path(item['original_path']).relative_to(historical)
        retained=Path(item['retained_path'])
        if retained.is_absolute() or '..' in retained.parts or retained==Path('.'):
            raise ValueError('Unsafe snapshot destination')
        try:source=checked_receipt(ROOT,review,relative,item['sha256'])
        except ValueError:
            source=ROOT/'catalogue/source-snapshots'/item['sha256']/relative
            if not source.is_file():source=ROOT/relative
        if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Frozen source mismatch: '+str(relative))
        sources.append((source,item))
    args.output.mkdir(parents=True)
    for source,item in sources:
        dest=args.output/item['retained_path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o600)
        if hashlib.sha256(dest.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Copied source mismatch')
    print(json.dumps({'public_files':len(sources),'result':'pass','private_arrays_copied':False}))
if __name__=='__main__':main()
