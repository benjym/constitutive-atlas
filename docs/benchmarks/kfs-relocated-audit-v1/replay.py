"""Replay exact historical Python audits using frozen read relocation, never a solver.

This is a compatibility harness for trusted, hash-checked auditors, not a Python
security sandbox. Historical filenames and command strings remain unchanged.
"""
import argparse,builtins,contextlib,hashlib,importlib.abc,importlib.machinery,importlib.util,io,json,os,runpy,sys,tempfile
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot-root',type=Path)
    ap.add_argument('--freeze',type=Path,default=HERE/'freeze-v2.json')
    ap.add_argument('--private-root',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if not __debug__:raise RuntimeError('Optimized Python is unsupported: integrity assertions must remain enabled')
    freeze=json.loads(args.freeze.read_text())
    snapshot=(args.snapshot_root or ROOT/freeze['public_root']).resolve()
    receipt_path=ROOT/freeze['private_receipts_path'];raw=receipt_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==freeze['private_receipts_sha256']
    receipt=json.loads(raw);private=(args.private_root or ROOT/receipt['private_root']).resolve()
    historical=freeze['historical_repository_root'];original_private=Path(historical)/receipt['private_root']
    mapping={}
    for item in freeze['public_files']:
        mapping[item['original_path']]=(snapshot/item['retained_path'],item['sha256'])
    for item in receipt['files']:
        mapping[item['origin']]=(private/item['retained_path'],item['sha256'])
    # Verify all bytes before executing any audit source, even if that source is never read.
    for name,(p,h) in mapping.items():
        assert p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==h,name
    dirs={historical:str(snapshot/'public')}
    for old,dest in freeze['directory_map'].items():dirs[old]=str(private/Path(dest).relative_to(original_private))
    direct=[str(snapshot),str(private)]
    retained_files={str(p.resolve()) for p,h in mapping.values()}
    raw_open=builtins.open;raw_io=io.open;raw_stat=os.stat;raw_scandir=os.scandir
    reads=set();denied=[]
    def relocate(path,*,metadata=False):
        if isinstance(path,int):return path
        text=os.fsdecode(path);key=os.path.abspath(text)
        if any(key==d or key.startswith(d+'/') for d in direct):
            if metadata or key in retained_files:return key
            raise FileNotFoundError('Unlisted retained input: '+key)
        candidates=[key,os.path.realpath(key)]
        for candidate in candidates:
            if any(candidate==d or candidate.startswith(d+'/') for d in direct):
                if metadata or candidate in retained_files:return candidate
                raise FileNotFoundError('Unlisted retained input: '+candidate)
            if candidate in mapping:reads.add(candidate);return str(mapping[candidate][0])
            for origin in sorted(dirs,key=len,reverse=True):
                if candidate==origin or candidate.startswith(origin+'/'):
                    if metadata:return dirs[origin]+candidate[len(origin):]
                    raise FileNotFoundError('Unmapped historical input: '+candidate)
        return path
    def open_with(fn,path,mode='r',*a,**kw):
        moved=relocate(path)
        if any(c in mode for c in 'wax+'):
            if moved!=path or any(os.path.abspath(os.fsdecode(path)).startswith(d+'/') for d in direct):
                raise PermissionError('Cannot write frozen input')
        return fn(moved,mode,*a,**kw)
    def source_data(loader,path):
        if str(path).endswith(('.pyc','.pyo')):raise OSError('Frozen source only')
        with raw_open(relocate(path),'rb') as stream:return stream.read()
    class Finder(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            parents=path if path is not None else [historical]
            leaf=fullname.rsplit('.',1)[-1]
            for parent in parents:
                for suffix,package in [(leaf+'/__init__.py',True),(leaf+'.py',False)]:
                    key=str(Path(parent)/suffix)
                    if key in mapping:
                        loader=importlib.machinery.SourceFileLoader(fullname,key)
                        return importlib.util.spec_from_file_location(fullname,key,loader=loader,submodule_search_locations=[str(Path(key).parent)] if package else None)
                folder=str(Path(parent)/leaf)
                if any(k.startswith(folder+'/') for k in mapping):
                    spec=importlib.machinery.ModuleSpec(fullname,loader=None,is_package=True);spec.submodule_search_locations=[folder];return spec
            return None
    def guard(event,values):
        if event in ('subprocess.Popen','os.system','os.posix_spawn','os.exec','socket.__new__'):
            denied.append(event);raise PermissionError('Saved replay forbids processes and network')
        if event=='open' and not isinstance(values[0],int):
            p=os.path.abspath(os.fsdecode(values[0]))
            # Actual reads must use listed retained files; directory mapping alone cannot authorize a read.
            if any(p==d or p.startswith(d+'/') for d in direct) and p not in retained_files:
                denied.append('unlisted_retained_read:'+p);raise PermissionError('Unlisted retained input')
            # Never fall back to original private/repository files.
            if not any(p==d or p.startswith(d+'/') for d in direct) and (p in mapping or any(p==o or p.startswith(o+'/') for o in dirs)):
                denied.append('original_read:'+p);raise PermissionError('Original input access forbidden')
    output=args.output.resolve();assert not output.exists()
    original_cwd=Path.cwd()
    finder=Finder();sys.meta_path.insert(0,finder);sys.dont_write_bytecode=True;sys.addaudithook(guard)
    log=io.StringIO();errors=io.StringIO();entry=historical+'/docs/benchmarks/kfs-development-agent-v1/check.py'
    try:
        with tempfile.TemporaryDirectory(prefix='kfs-relocated-results-') as temp:
            os.chdir(temp)
            result_path=Path(temp)/'review.json';prior=sys.argv;sys.argv=[entry,'--repo',historical,'--output',str(result_path)]
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch('builtins.open',lambda p,m='r',*a,**k:open_with(raw_open,p,m,*a,**k)))
                stack.enter_context(patch('io.open',lambda p,m='r',*a,**k:open_with(raw_io,p,m,*a,**k)))
                stack.enter_context(patch('io.open_code',lambda p:raw_io(relocate(p),'rb')))
                stack.enter_context(patch('os.stat',lambda p,*a,**k:raw_stat(relocate(p,metadata=True),*a,**k)))
                stack.enter_context(patch('os.scandir',lambda p='.':raw_scandir(relocate(p,metadata=True))))
                stack.enter_context(patch.object(importlib.machinery.SourceFileLoader,'get_data',source_data))
                with contextlib.redirect_stdout(log),contextlib.redirect_stderr(errors):runpy.run_path(entry,run_name='__main__')
            sys.argv=prior
            result=json.loads(result_path.read_text())
            expected=json.loads((snapshot/'public/docs/benchmarks/kfs-development-agent-v1/check-results.json').read_text())
            assert result==expected,'Original review result changed'
            assert len(result['independent_checks'])==freeze['expected_groups'] and len(result['saved_auditors'])==freeze['expected_saved_auditors']
            out={'result':'pass','original_review_result_exact':True,'independent_groups':len(result['independent_checks']),'saved_auditors':len(result['saved_auditors']),'mapped_files_read':len(reads),'guard_denials':denied,'stdout':log.getvalue(),'stderr':errors.getvalue(),'new_material_calls':0,'new_builds':0,'new_fits':0,'review_result':result}
    except Exception as exc:
        output.write_text(json.dumps({'result':'fail','error':type(exc).__name__+': '+str(exc),'stdout':log.getvalue(),'stderr':errors.getvalue(),'mapped_files_read':len(reads),'guard_denials':denied},indent=2)+'\n');raise
    finally:
        os.chdir(original_cwd);sys.meta_path.remove(finder)
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('review_result','stdout','stderr')}))
if __name__=='__main__':main()
