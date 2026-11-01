"""One serial explicit build/backend, two frozen modes, retained receipts."""
from pathlib import Path
import json,hashlib,subprocess,sys,time
P=Path(__file__).parent;ROOT=P.parents[2];STAGE=Path('/private/tmp/atlas-tresca-certified-corners-v5')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def process(name,cmd,stdin=None):
    t=time.monotonic()
    if stdin:
        with stdin.open()as src:result=subprocess.run(cmd,stdin=src,capture_output=True,text=True,cwd=ROOT,timeout=60)
    else:result=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=60)
    (P/(name+'-process.json')).write_text(json.dumps({'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'elapsed_seconds':time.monotonic()-t},indent=2)+'\n')
    print(name,'returncode',result.returncode,flush=True)
    if result.returncode:print(result.stderr);raise SystemExit(result.returncode)
    return result.stdout
if __name__=='__main__':
    phase=sys.argv[1]
    if phase=='freeze':
        assert not (P/'prospective-freeze.json').exists()
        files={str(q.relative_to(ROOT)):sha(q)for q in P.rglob('*')if q.is_file()}
        (P/'prospective-freeze.json').write_text(json.dumps({'version':'tresca-certified-corners-v5-prospective-0.1','files':files,'wire_sha256':{name:sha(STAGE/(name+'-requests.txt'))for name in ['corpus','history','laboratory']},'no_candidate_build_or_execution_before_freeze':True},indent=2)+'\n');print('frozen',len(files),'files')
        import shutil
        for q in P.rglob('*'):
            if q.is_file() and '__pycache__' not in q.parts:
                dest=STAGE/q.relative_to(P);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,dest)
    else:
        assert phase in ('native','wasm');freeze=json.loads((P/'prospective-freeze.json').read_text())
        for n,h in freeze['files'].items():assert sha(ROOT/n)==h,n
        for n,h in json.loads((P/'source-pins.json').read_text()).items():assert sha(ROOT/n)==h,n
        for folder in ['frozen','generated','generated-original']:
            for q in (P/folder).rglob('*'):
                if q.is_file():assert q.read_bytes()==(STAGE/q.relative_to(P)).read_bytes()
        for name,h in freeze['wire_sha256'].items():assert sha(STAGE/(name+'-requests.txt'))==h
        prefix=['emcmake']if phase=='wasm'else []
        process(phase+'-configure',prefix+['cmake','-S',str(STAGE),'-B',str(STAGE/phase),'-DCMAKE_BUILD_TYPE=Release'])
        process(phase+'-build',['cmake','--build',str(STAGE/phase),'--target','atlas_tresca_certified_corners','--parallel','1'])
        cmd=[str(STAGE/'native/atlas_tresca_certified_corners')]if phase=='native'else ['node',str(STAGE/'wasm/tresca-certified-corners.js')]
        for mode in ['corpus','history','checks','laboratory','reversal']:
            text=process(phase+'-'+mode+'-execution',cmd+[mode],STAGE/(mode+'-requests.txt') if mode in ['corpus','history','laboratory'] else None);(P/(phase+'-'+mode+'-responses.jsonl')).write_text(text)
        binaries=[STAGE/'native/atlas_tresca_certified_corners']if phase=='native'else [STAGE/'wasm/tresca-certified-corners.js',STAGE/'wasm/tresca-certified-corners.wasm']
        (P/(phase+'-artifacts.json')).write_text(json.dumps({str(q):sha(q)for q in binaries},indent=2)+'\n')
