"""Portable source-only capsule prototype, not a build or security sandbox.
Explicit trusted Python entrypoints only. No source discovery or pin substitution.
"""
import base64,hashlib,json,os,pathlib,subprocess,sys,tempfile
VERSION='atlas-source-replay-capsule-0.1'

def digest(blob):return hashlib.sha256(blob).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def relative(name):
 require(type(name)is str and '\\' not in name and name!='','relative POSIX path required')
 p=pathlib.PurePosixPath(name)
 require(not p.is_absolute() and all(x not in ('.','..','') for x in name.split('/')),'unsafe source path')
 return name

def export(root,pins,entry,args=(),expected_exit=0,overrides=None):
 """overrides supply historically resolved source bytes, checked against original pins.
 In production resolve overrides via document-bound checked_receipt, not current hashes.
 """
 root=pathlib.Path(root).resolve();overrides=overrides or {};require(type(pins)is dict and pins,'explicit closure required')
 files={}
 for name,pin in sorted(pins.items()):
  relative(name);target=(root/name).resolve();require(target.is_relative_to(root),'source escape')
  blob=overrides[name] if name in overrides else target.read_bytes()
  require(type(blob)is bytes and digest(blob)==pin,'original source pin mismatch: '+name)
  files[name]={'sha256':pin,'bytes':len(blob),'base64':base64.b64encode(blob).decode('ascii')}
 c={'version':VERSION,'closure':'explicit source/data files, stdlib Python interpreter external','entrypoint':entry,'args':list(args),'expected_exit':expected_exit,'files':files,'claims':{'compiled_rebuild':False,'scientific_rerun':False,'environment_bit_reproduction':False}}
 validate(c);return c

def validate(c):
 require(type(c)is dict and c.get('version')==VERSION,'capsule version')
 require(type(c.get('files'))is dict and 0<len(c['files'])<=1024,'bounded closure')
 total=0
 for name,pin in c['files'].items():
  relative(name);require(type(pin)is dict and set(pin)=={'sha256','bytes','base64'},'source blob shape')
  require(type(pin['sha256'])is str and len(pin['sha256'])==64 and all(x in '0123456789abcdef' for x in pin['sha256']),'source digest')
  require(type(pin['bytes'])is int and 0<=pin['bytes']<=16*1024*1024,'source size')
  require(type(pin['base64'])is str,'source encoding')
  b=base64.b64decode(pin['base64'],validate=True);require(len(b)==pin['bytes'] and digest(b)==pin['sha256'],'source blob integrity')
  total+=len(b);require(total<=64*1024*1024,'capsule total size')
  for parent in pathlib.PurePosixPath(name).parents:
   require(parent.as_posix() not in c['files'],'file/directory collision')
 require(relative(c['entrypoint']) in c['files'] and c['entrypoint'].endswith('.py'),'archived Python entrypoint required')
 require(type(c['args'])is list and all(type(x)is str and '\x00' not in x for x in c['args']),'literal command args')
 require(type(c['expected_exit'])is int and 0<=c['expected_exit']<=255,'expected process exit')
 return c

def materialize(c,destination):
 validate(c);d=pathlib.Path(destination).resolve();require(not d.exists(),'fresh capsule tree required');d.mkdir(parents=True)
 for name,pin in c['files'].items():
  p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(pin['base64'],validate=True))
 return d

def replay(c,timeout=30):
 """Re-audit original source bytes in a fresh process/tree; no ambient repo fallback.
 Runtime/library version is recorded. Caller interprets output against frozen gates.
 """
 validate(c)
 with tempfile.TemporaryDirectory(prefix='atlas-frozen-replay-') as tmp:
  root=materialize(c,pathlib.Path(tmp)/'repo')
  args=[x.replace('{root}',str(root)) for x in c['args']]
  bootstrap='import os,sys,runpy; root=sys.argv[1]; entry=sys.argv[2]; sys.path.insert(0,root); os.chdir(root); sys.argv=[entry]+sys.argv[3:]; runpy.run_path(entry,run_name="__main__")'
  env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','ATLAS_'))};env['PYTHONDONTWRITEBYTECODE']='1'
  process=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,str(root),str(root/c['entrypoint']),*args],cwd=root,env=env,capture_output=True,timeout=timeout)
  for name,pin in c['files'].items():require(digest((root/name).read_bytes())==pin['sha256'],'archived input changed during replay: '+name)
  return {'version':'atlas-source-replay-result-0.1','capsule_sha256':digest(json.dumps(c,sort_keys=True,separators=(',',':')).encode()),'returncode':process.returncode,'expected_exit':c['expected_exit'],'expected_exit_matched':process.returncode==c['expected_exit'],'stdout':process.stdout.decode(errors='strict'),'stderr':process.stderr.decode(errors='strict'),'stdout_sha256':digest(process.stdout),'stderr_sha256':digest(process.stderr),'python':sys.version,'execution_scope':'trusted Python entrypoint; side effects are not sandboxed','note':'Runs the trusted archived Python entrypoint. Not a sandbox or compiled/scientific rerun.'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('capsule',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
 c=json.loads(a.capsule.read_text());r=replay(c)
 text=json.dumps(r,indent=2,allow_nan=False)+'\n'
 if a.output:require(not a.output.exists(),'fresh replay output required');a.output.write_text(text)
 else:print(text,end='')
 raise SystemExit(0 if r['expected_exit_matched'] else 1)
