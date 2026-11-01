"""Source-only guard; never loads or executes a native/Wasm module."""
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('freeze',type=Path)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    record=json.loads(args.freeze.read_text())
    root=Path(record['command'][2]).parents[1]
    errors=[]
    def git(*words):
        return subprocess.check_output(['git',*words],cwd=root,text=True).strip()
    if git('rev-parse','HEAD')!=record['source_commit']:errors.append('Source commit changed')
    if git('rev-parse','HEAD^{tree}')!=record['source_tree']:errors.append('Source tree changed')
    if git('status','--porcelain','--untracked-files=no'):errors.append('Tracked source is dirty')
    for name,expected in record.get('source_support',{}).items():
        support=root/name
        if not support.is_file() or hashlib.sha256(support.read_bytes()).hexdigest()!=expected:errors.append('Source supporting input changed: '+name)
    count=0
    for flag,engine in record['engines'].items():
        base=Path(engine['path'])
        actual={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}
        if actual!=set(engine['files']):errors.append('Engine file set changed: '+flag)
        for name,expected in engine['files'].items():
            p=base/name
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Engine input changed: '+flag+'/'+name)
            count+=1
    if not errors:
        sys.path.insert(0,str(root))
        from atlas.compiler import generate
        with tempfile.TemporaryDirectory() as temporary:
            generate(temporary)
            if (Path(temporary)/'models.json').read_bytes()!=(Path(record['engines']['--wasm-dir']['path'])/'generated/models.json').read_bytes():errors.append('Ordinary generated catalogue differs')
    result={'status':'failed' if errors else 'passed','scope':'Source and input identity only; not compiled/package/browser qualification','source_commit':record['source_commit'],'freeze_sha256':hashlib.sha256(args.freeze.read_bytes()).hexdigest(),'engine_profiles':len(record['engines']),'engine_files':count,'errors':errors,'compiled_calls':0}
    args.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return bool(errors)
if __name__=='__main__':raise SystemExit(main())
