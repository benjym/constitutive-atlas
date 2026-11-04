from pathlib import Path
import sys,json,hashlib,importlib.util,subprocess,shutil,time,os
N=Path(__file__).resolve().parents[1]; PLAN=N/'rate-restoration-qualification-plan-v3'; MANIFEST='4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812'
assert hashlib.sha256((PLAN/'manifest.json').read_bytes()).hexdigest()==MANIFEST
spec=importlib.util.spec_from_file_location('commands',PLAN/'commands.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
phase=sys.argv[1];phases=json.loads((PLAN/'plan.json').read_text())['phases'];assert phase in phases
launch=N/'control-restoration-C-launch-binding-v3.json';binding=json.loads(launch.read_text());assert binding['ready_for_actual'] is True and binding['plan_manifest_sha256']==MANIFEST
review=json.loads(Path(binding['plan_review']['path']).read_text());assert review['accepted'] is True and review['proposal_manifest_sha256']==MANIFEST
index=phases.index(phase)
if index:
 previous=phases[index-1];prev=(c.ACTUAL.parent/(c.ACTUAL.name+'-outer-source-freeze')/'receipt.json')if previous=='source-freeze'else c.ACTUAL/('outer-'+previous)/'receipt.json'
 prior=json.loads(prev.read_text());assert prior['returncode']==0 and prior['mandatory_reap'] is True,(previous,prior['returncode'])
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True);private=N.parents[2]/'.local/retained-evidence'/('baseline-five-C-v3-'+phase+'-preflight-20261105.raw');assert not private.exists();private.write_text(ps)
active=[]
for line in ps.splitlines():
 parts=line.strip().split(None,2)
 if len(parts)!=3:continue
 words=parts[2].split();base=Path(words[0]).name if words else ''
 if base.startswith('atlas_')or base in('clang','clang++','emcc','em++')or(base=='cmake'and'--build'in words)or(base in('node','nodejs')and any(s in parts[2]for s in('/wasm-cli.mjs','/extras.mjs'))):active.append({'pid':int(parts[0]),'executable':base})
assert not active,active
preflight={'identity':'coordinator-fresh-serial-C-phase-preflight-v3','phase':phase,'epoch':time.time(),'free_bytes':shutil.disk_usage('/private/tmp').free,'ram_bytes':int(subprocess.check_output(['/usr/sbin/sysctl','-n','hw.memsize'],text=True)),'private_process_inventory':str(private),'active_compiled':active,'plan_manifest_sha256':MANIFEST,'launch_binding_sha256':hashlib.sha256(launch.read_bytes()).hexdigest()}
(Path(__file__).parent/(phase+'-preflight.json')).write_text(json.dumps(preflight,indent=2)+'\n')
for key in ('HOME','XDG_CONFIG_HOME','TMPDIR'):Path(c.closed_environment()[key]).mkdir(parents=True,exist_ok=True)
if phase=='source-freeze':
 old=json.loads((N/'current16-qualification-plan-v1/source-freeze-v1.json').read_text());tools={k:v['path']for k,v in old['build_tools'].items()}
 for row in [*old['build_tools'].values(),old['node'],old['python']]:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
 result=c.observe_source_freeze(old['python']['path'],old['node']['path'],tools,MANIFEST,launch)
else:
 pre=json.loads((c.ACTUAL/'source-freeze.json').read_text());result=c.observe_phase(pre,phase,MANIFEST)
print(json.dumps({'phase':phase,'returncode':result.returncode,'mandatory_reap':result.receipt['mandatory_reap'],'elapsed_seconds':result.receipt['elapsed_seconds']}));sys.exit(result.returncode)
