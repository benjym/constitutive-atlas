"""Frozen private candidate: serial explicit targets, regular-file stdin."""
from pathlib import Path
import json,hashlib,gzip,subprocess,sys,time
P=Path(__file__).parent;ROOT=P.parents[2];STAGE=Path('/private/tmp/atlas-tresca-continuous-history-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def process(name,cmd,stdin=None):
    t=time.monotonic()
    if stdin:
        with stdin.open()as source:result=subprocess.run(cmd,stdin=source,capture_output=True,text=True,cwd=ROOT,timeout=60)
    else:result=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=60)
    (P/(name+'-process.json')).write_text(json.dumps({'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'elapsed_seconds':time.monotonic()-t},indent=2)+'\n')
    print(name,'returncode',result.returncode,flush=True)
    if result.returncode:print(result.stderr);raise SystemExit(result.returncode)
    return result.stdout
if __name__=='__main__':
    phase=sys.argv[1]
    if phase=='freeze':
        assert not (P/'prospective-freeze.json').exists()
        (STAGE/'requests.txt').write_bytes((P/'requests.txt').read_bytes())
        files={str(q.relative_to(ROOT)):sha(q)for q in P.rglob('*')if q.is_file()}
        (P/'prospective-freeze.json').write_text(json.dumps({'version':'tresca-continuous-history-prospective-0.1','files':files,'wire_sha256':sha(STAGE/'requests.txt'),'instrumentation':'none; unchanged original generated candidate header','no_candidate_build_or_execution_before_freeze':True},indent=2)+'\n')
        print('frozen',len(files),'files')
    else:
        assert phase in ('native','wasm');freeze=json.loads((P/'prospective-freeze.json').read_text())
        for n,h in freeze['files'].items():assert sha(ROOT/n)==h,n
        for n,h in json.loads((P/'source-pins.json').read_text()).items():assert sha(ROOT/n)==h,n
        for folder in ('frozen','generated'):
            for q in (P/folder).rglob('*'):
                if q.is_file():assert q.read_bytes()==(STAGE/q.relative_to(P)).read_bytes()
        assert sha(STAGE/'requests.txt')==freeze['wire_sha256']
        prefix=['emcmake']if phase=='wasm'else []
        process(phase+'-configure',prefix+['cmake','-S',str(STAGE),'-B',str(STAGE/phase),'-DCMAKE_BUILD_TYPE=Release'])
        process(phase+'-build',['cmake','--build',str(STAGE/phase),'--target','atlas_tresca_history','--parallel','1'])
        cmd=[str(STAGE/'native/atlas_tresca_history')]if phase=='native'else ['node',str(STAGE/'wasm/tresca-history.js')]
        output=process(phase+'-execution',cmd,STAGE/'requests.txt');(P/(phase+'-responses.jsonl')).write_text(output)
        artifacts=[STAGE/'native/atlas_tresca_history']if phase=='native'else [STAGE/'wasm/tresca-history.js',STAGE/'wasm/tresca-history.wasm']
        (P/(phase+'-artifacts.json')).write_text(json.dumps({str(q):sha(q)for q in artifacts},indent=2)+'\n')
