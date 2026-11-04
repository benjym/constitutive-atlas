from pathlib import Path
import subprocess,json,hashlib,importlib.util,datetime,re,os
root=Path('/Users/bmar5496/code/constitutive-atlas');n=root/'docs/delivery/unheld-finalisation-20261105-v1';out=n/'recorded-explicit-state-actual-v1';source=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source/'tools/test_recorded.mjs')=='64ce5390fedda14aaff03a44ee6794ced587be4359e7ae6b4fb92457eec0a459'
launch=json.loads((n/'numerics-explicit-state-actual-v2/launch.json').read_text())
for p in launch['runtime_artifacts']:assert sha(root/p['retained'])==p['sha256']
ps=subprocess.check_output(['ps','-axo','pid,ppid,pgid,stat,command'],text=True);(out/'pre-processes.raw').write_text(ps)
conflicts=[];unrelated=[]
for row in ps.splitlines()[1:]:
 fields=row.strip().split(None,4)
 if len(fields)!=5:continue
 cmd=fields[4];exe=cmd.split()[0]
 if re.search(r'(^|/)(cmake|emcc|em\+\+|clang|clang\+\+|gcc|g\+\+|cc1|ninja|atlas_solver|atlas_path_capability)$',exe) or (exe.endswith('/node') and re.search(r'(tools/test_|collect.*\.mjs)',cmd)):conflicts.append(row)
 if exe.endswith('/make'):
  cwd=subprocess.run(['lsof','-a','-p',fields[0],'-d','cwd','-Fn'],text=True,capture_output=True)
  (out/('make-'+fields[0]+'-cwd.raw')).write_text(cwd.stdout+cwd.stderr)
  if cmd.endswith('make pdf') and '\nn/Users/bmar5496/code/civl2410/book\n' in cwd.stdout:unrelated.append(row)
  else:conflicts.append(row)
assert not conflicts,conflicts
observer=root/'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py'
assert sha(observer)=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e'
argv=[launch['argv'][0],str(source/'tools/test_recorded.mjs'),'--native',str(root/launch['runtime_artifacts'][0]['retained']),'--wasm',str(root/launch['runtime_artifacts'][1]['retained']),'--output',str(out/'report.json')]
receipt={'argv':argv,'env':launch['env'],'source_sha256':sha(source/'tools/test_recorded.mjs'),'observer_sha256':sha(observer),'runtime_artifacts':launch['runtime_artifacts'],'active_compiler_or_material_processes_observed':conflicts,'unrelated_documentation_processes_preserved':unrelated,'fresh_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout':1800}
(out/'launch.json').write_text(json.dumps(receipt,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('observer',observer);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
r=mod.observe(argv,str(source),out/'observer',env=launch['env'],timeout=1800);print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
