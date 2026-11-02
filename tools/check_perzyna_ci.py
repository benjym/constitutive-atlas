"""Serial CI reproduction of the independently reviewed Perzyna schedule study."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
STUDY='docs/ingestion/perzyna-comsol63/execution-v2'
PROOF='tools/record_cmake_profile_build_v2.py'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paired',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if Path(shutil.which('python3') or '').resolve()!=Path(sys.executable).resolve():raise ValueError('python3 consumer identity differs from executing interpreter')
    operations=[]
    def run(name,argv):
        log=out/(name+'.log');receipt=out/(name+'.json')
        if log.exists() or receipt.exists():raise ValueError('Fresh operation outputs required: '+name)
        start=time.time()
        with log.open('xb') as stream:result=subprocess.run([str(x) for x in argv],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        data=dict(name=name,argv=[str(x) for x in argv],returncode=result.returncode,elapsed_seconds=time.time()-start,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
        receipt.write_text(json.dumps(data,indent=2)+'\n');operations.append(data)
        print(name+': exit '+str(result.returncode),flush=True)
        if result.returncode:raise subprocess.CalledProcessError(result.returncode,argv)
    def backend(kind):
        build='build-perzyna-ci-'+kind;folder=ROOT/build
        configure=['cmake','-S','cmake/perzyna','-B',build,'-G','Unix Makefiles','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_BUILD_TYPE=Release']
        if kind=='wasm':configure.insert(0,'emcmake')
        run(kind+'-configure',configure)
        run(kind+'-build',['cmake','--build',build,'--target','atlas_perzyna_solver','--parallel','1'])
        if (folder/'generated/models.json').read_bytes()!=(ROOT/STUDY/'expected-catalogue.json').read_bytes():raise ValueError('Normal generated catalogue differs from frozen Perzyna model')
        artifacts=['atlas_perzyna_solver']
        if kind=='wasm':
            shutil.copyfile(folder/'perzyna.js',folder/'perzyna.mjs');artifacts=['perzyna.js','perzyna.mjs','perzyna.wasm']
        pre=out/(kind+'-pre.json');post=out/(kind+'-post.json')
        capture=[sys.executable,'-B',PROOF,'capture','--root',ROOT,'--build',build,'--target','atlas_perzyna_solver','--entrypoint','cpp/main.cpp','--models','models/research/perzyna','--recipe','cmake/perzyna/CMakeLists.txt','--schedule','required','--kind',kind,'--receipt',pre,'--consumer-tool','python3','--consumer-tool','node']
        for item in artifacts:capture+=['--artifact',item]
        for item in ['study.py','oracle.py','cases.json','expected-catalogue.json','reference-convergence.json','collect_wasm.mjs','parity.py','FREEZE.json']:capture+=['--consumer-source',STUDY+'/'+item]
        capture+=['--consumer-source','tools/check_perzyna_ci.py']
        run(kind+'-capture',capture)
        pre_sha=hashlib.sha256(pre.read_bytes()).hexdigest();raw=out/(kind+'-raw.json')
        consumer=[sys.executable,'-B',STUDY+'/study.py','native','--solver',folder/'atlas_perzyna_solver','--raw',raw] if kind=='native' else ['node',STUDY+'/collect_wasm.mjs',folder/'perzyna.mjs',ROOT/STUDY/'cases.json',raw]
        # Verify identity after both successful and failed consumers; retain each genuine exit.
        failure=None
        try:run(kind+'-consumer',consumer)
        except subprocess.CalledProcessError as error:failure=error
        run(kind+'-verify',[sys.executable,'-B',PROOF,'verify','--receipt',pre,'--receipt-sha256',pre_sha,'--output',post])
        if failure:raise failure
        if kind=='wasm':run('wasm-assessment',[sys.executable,'-B',STUDY+'/study.py','assess','--raw',raw])
        return raw
    passed=False
    try:
        native=backend('native')
        if args.paired:
            wasm=backend('wasm');run('physical-parity',[sys.executable,'-B',STUDY+'/parity.py',native,wasm])
        passed=True
    finally:
        (out/'summary.json').write_text(json.dumps(dict(passed=passed,paired=args.paired,operations=operations,scope='Frozen107case BE schedules; exact build identity checks; no experimental or browser claim'),indent=2)+'\n')

if __name__=='__main__':main()
