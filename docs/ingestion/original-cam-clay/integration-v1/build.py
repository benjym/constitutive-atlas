"""Coordinator serial normal-root targets; preserve every build receipt."""
from pathlib import Path
import argparse,os,json,shutil,subprocess,hashlib
B=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-occ-integration-v1');a=argparse.ArgumentParser();a.add_argument('backend',choices=['native','wasm']);x=a.parse_args();env=os.environ.copy()
cmd=['cmake','-S',str(S/'source'),'-B',str(S/f'build-{x.backend}'),'-DCMAKE_BUILD_TYPE=Release']
if x.backend=='wasm':
 cache=S/'em-cache';shutil.copytree('/private/tmp/atlas-occ-execution-v2/em-cache',cache,ignore=shutil.ignore_patterns('*.lock'));env['EM_CACHE']=str(cache);cmd=['emcmake']+cmd
commands=[cmd]
for target in (['atlas_solver','atlas_numerical_tests','atlas_recorded_tests'] if x.backend=='native' else ['atlas_solver']):commands.append(['cmake','--build',str(S/f'build-{x.backend}'),'--target',target,'--parallel','1'])
rows=[]
for cmd in commands:
 r=subprocess.run(cmd,env=env,capture_output=True,text=True);rows.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));(B/f'{x.backend}-build.json').write_text(json.dumps(dict(backend=x.backend,environment_overrides={'EM_CACHE':env['EM_CACHE']} if 'EM_CACHE'in env else {},commands=rows),indent=2)+'\n');print(' '.join(cmd),'exit',r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
