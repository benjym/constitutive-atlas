"""Replay unchanged prior package checker in its exact historical source context."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
HERE=Path(__file__).resolve().parent
A='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
DOCUMENT=A+'actual-package-v2/EXECUTION_SOURCE_FREEZE.json'
REVIEW='docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/actual-package-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=json.loads((ROOT/DOCUMENT).read_text())['files']
    assert len(freeze)==8194
    redirected=[];baseline=[];absolute_prerequisites=[]
    with tempfile.TemporaryDirectory(prefix='atlas-lade-historical-') as directory:
        context=Path(directory)
        def copy(source,name):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts,name
            dest=context/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,dest)
        for name,digest in freeze.items():
            if Path(name).is_absolute():
                assert sha(Path(name))==digest,name
                absolute_prerequisites.append(name)
                continue
            live=ROOT/name
            if live.is_file() and sha(live)==digest:source=live
            else:
                baseline.append(name)
                source=checked_receipt(ROOT,DOCUMENT,name,digest)
                redirected.append(dict(path=name,sha256=digest,retained=source.relative_to(ROOT).as_posix()))
            copy(source,name)
        qualification=json.loads((ROOT/'.local/lade-main-atlas-v2/site/engine-implicit-path/qualification.json').read_text())
        for pin in qualification['binding']['ordered_inputs']:
            source=ROOT/pin['path']
            assert sha(source)==pin['sha256']
            copy(source,pin['path'])
        for relative in [A+'actual-package-v2',REVIEW]:
            for source in (ROOT/relative).rglob('*'):
                if source.is_file():copy(source,source.relative_to(ROOT))
        copy(ROOT/(A+'actual-package-v1/PACKAGE_MANIFEST.json'),A+'actual-package-v1/PACKAGE_MANIFEST.json')
        # Preserved site is copied, never rebuilt or executed.
        shutil.copytree(ROOT/'.local/lade-main-atlas-v2/site',context/'.local/lade-main-atlas-v2/site')
        assert all(sha(context/n)==h for n,h in freeze.items())
        proc=subprocess.run([sys.executable,'-B',str(context/REVIEW/'check.py')],cwd=context,capture_output=True,text=True)
        (HERE/'historical-package.stdout').write_text(proc.stdout)
        (HERE/'historical-package.stderr').write_text(proc.stderr)
        result={'returncode':proc.returncode,'source_files':len(freeze),'absolute_frozen_prerequisites':len(absolute_prerequisites),'live_root_drift':baseline,'exact_archive_redirects':redirected,'checker_sha256':sha(ROOT/REVIEW/'check.py'),'qualification':'Unchanged prior checker in exact historical source context; not new current-root/package/release qualification','compiled_calls':0,'local_prerequisites':['Retained .local/lade-main-atlas-v2/site package','Original absolute raw process logs named by saved records']}
        (HERE/'historical-package-result.json').write_text(json.dumps(result,indent=2)+'\n')
        assert proc.returncode==0,proc.stderr
        assert json.loads(proc.stdout)['source_files']==8194
        print(json.dumps(result,indent=2))
if __name__=='__main__':main()
