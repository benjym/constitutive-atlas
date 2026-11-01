"""One explicit target per serial stage; retain process evidence, no deployment."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,time,shutil,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2];STAGE=Path('/private/tmp/atlas-exact-range-runtime-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def process(name,cmd,stdin=None):
    t=time.monotonic()
    if stdin:
        with stdin.open('r')as src:out=subprocess.run(cmd,stdin=src,capture_output=True,text=True,timeout=60,cwd=ROOT)
    else:out=subprocess.run(cmd,capture_output=True,text=True,timeout=60,cwd=ROOT)
    (P/(name+'-process.json')).write_text(json.dumps({'command':cmd,'returncode':out.returncode,'stdout':out.stdout,'stderr':out.stderr,'elapsed_seconds':time.monotonic()-t},indent=2)+'\n')
    print(name,'returncode',out.returncode,flush=True)
    if out.returncode:print(out.stderr);raise SystemExit(out.returncode)
    return out.stdout
if __name__=='__main__':
    phase=sys.argv[1]
    if phase=='prepare':
        spec=importlib.util.spec_from_file_location('range_fixture',P/'prepare_fixtures.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.prepare(STAGE)
        (P/'generated').mkdir()
        for q in (STAGE/'generated').iterdir():shutil.copyfile(q,P/'generated'/q.name)
        for name in ['model.json','history.json']:shutil.copyfile(STAGE/name,P/name)
        # Oracle records are frozen earlier; verify Python runtime separately now.
        from atlas.dsl import evaluate,parse,Sym
        rows=json.loads((P/'requests.json').read_text())
        for row in rows:assert evaluate(parse('principal_range_le(A,Y)'),{'A':Sym(tuple(float.fromhex(v)for v in row['values'])),'Y':float.fromhex(row['width'])})==row['inside'],row['id']
        files={str(q.relative_to(ROOT)):sha(q)for q in [ROOT/'atlas/dsl.py',ROOT/'atlas/compiler.py',ROOT/'atlas/history_compiler.py',ROOT/'atlas/numerics/principal_range.py',*sorted((ROOT/'cpp/include').rglob('*.hpp'))]}
        files.update({str(q.relative_to(ROOT)):sha(q)for q in P.rglob('*')if q.is_file()and q.name!='prospective-freeze.json'})
        (P/'prospective-freeze.json').write_text(json.dumps({'version':'exact-range-runtime-prospective-0.1','files':files,'python_oracle_decisions':len(rows),'reference_inputs_sha256':sha(ROOT/'docs/reviews/certified-spectral-range-v1/inputs.json'),'reference_checks_sha256':sha(ROOT/'docs/reviews/certified-spectral-range-v1/checks.json')},indent=2)+'\n')
        print('frozen',len(files),'source/evidence files;',len(rows),'Python decisions pass')
    else:
        freeze=json.loads((P/'prospective-freeze.json').read_text())
        for n,h in freeze['files'].items():assert sha(ROOT/n)==h,n
        backend=phase;assert backend in ('native','wasm')
        config=(['emcmake']if backend=='wasm'else [])+['cmake','-S',str(STAGE),'-B',str(STAGE/backend),'-DCMAKE_BUILD_TYPE=Release']
        process(backend+'-configure',config)
        process(backend+'-build',['cmake','--build',str(STAGE/backend),'--target','atlas_exact_range','--parallel','1'])
        cmd=[str(STAGE/'native/atlas_exact_range')]if backend=='native'else ['node',str(STAGE/'wasm/exact-range.js')]
        stdout=process(backend+'-execution',cmd,STAGE/'requests.txt');(P/(backend+'-responses.txt')).write_text(stdout)
        artifacts=[STAGE/'native/atlas_exact_range']if backend=='native'else [STAGE/'wasm/exact-range.js',STAGE/'wasm/exact-range.wasm']
        (P/(backend+'-artifacts.json')).write_text(json.dumps({str(q):sha(q)for q in artifacts},indent=2)+'\n')
