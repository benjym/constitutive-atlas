import importlib.util,json,hashlib,sys,subprocess,time,shutil
from pathlib import Path
N=Path(__file__).resolve().parents[1]; PLAN=N/'current17-derivative-trace-plan-v1'; OUT=Path(__file__).resolve().parent
recipe=json.loads((PLAN/'recipe.json').read_text()); phase=sys.argv[1]; assert phase in ('configure','build','run')
spec=importlib.util.spec_from_file_location('observer',N.parent/'unheld-finalisation-20261102-v1/baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py'); observer=importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
env=json.loads((N/'current17-runtime-actual-v1/plan.json').read_text())['environment']
pins=recipe['source_inputs']+list(recipe['tools'].values())+[recipe['parent_case'],recipe['case_wire']]
def verify():
 for pin in pins:
  p=Path(pin['path']); assert len(p.read_bytes())==pin['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'],str(p)
verify()
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True)
private=N.parents[2]/'.local/retained-evidence'/('baseline-five-derivative-trace-'+phase+'-20261105.raw'); private.write_text(ps)
active=[r for r in ps.splitlines() if any(v in r for v in ('/atlas_solver ','/atlas_derivative_trace ','cmake --build','emcc.py','clang -','clang++ -')) and not any(v in r for v in ('/bin/zsh -','python3 -B - <<','launch.py'))]
assert not active,active
pre={'epoch':time.time(),'free_bytes':shutil.disk_usage('/private/tmp').free,'process_inventory':str(private),'active_compiled':active,'phase':phase}
(OUT/(phase+'-preflight.json')).write_text(json.dumps(pre,indent=2)+'\n')
r=observer.observe(recipe[phase+'_argv'],str(N.parents[2]),OUT/('outer-'+phase),env=env,timeout=1800)
verify(); print(json.dumps({'phase':phase,'returncode':r.returncode,'mandatory_reap':r.receipt['mandatory_reap'],'receipt':str(OUT/('outer-'+phase)/'receipt.json')})); sys.exit(r.returncode)
