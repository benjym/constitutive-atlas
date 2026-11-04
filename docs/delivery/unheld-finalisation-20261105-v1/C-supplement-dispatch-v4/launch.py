from pathlib import Path
import sys,json,hashlib,importlib.util,subprocess,shutil,time
N=Path(__file__).resolve().parents[1];P=N/'rate-restoration-qualification-plan-v4';MANIFEST='50bc4648bc749bdac1c04313de861f6ea75fdec1cd954824198527c4b10f4f0e'
assert hashlib.sha256((P/'manifest.json').read_bytes()).hexdigest()==MANIFEST
phase=sys.argv[1];assert phase in ('extra-native','extra-wasm','extra-pair')
review=Path(sys.argv[2]).resolve();assert len(sys.argv)==4 and hashlib.sha256(review.read_bytes()).hexdigest()==sys.argv[3]
pin={'path':str(review),'sha256':sys.argv[3],'bytes':review.stat().st_size}
spec=importlib.util.spec_from_file_location('accepted_v4_commands',P/'commands.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
pre=json.loads((Path(c.PLAN['actual'])/'source-freeze.json').read_text());c.guard(pre,MANIFEST,pin)
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True);private=N.parents[2]/'.local/retained-evidence'/('baseline-five-C-v4-'+phase+'-preflight-20261105.raw');assert not private.exists();private.write_text(ps)
active=[]
for line in ps.splitlines():
 parts=line.strip().split(None,2)
 if len(parts)!=3:continue
 words=parts[2].split();base=Path(words[0]).name if words else ''
 if base.startswith('atlas_')or base in('clang','clang++','emcc','em++')or(base=='cmake'and'--build'in words)or(base in('node','nodejs')and any(s in parts[2]for s in('/wasm-cli.mjs','/extras.mjs'))):active.append({'pid':int(parts[0]),'executable':base})
assert not active,active
preflight={'identity':'coordinator-C-supplement-v4-preflight','phase':phase,'epoch':time.time(),'free_bytes':shutil.disk_usage('/private/tmp').free,'ram_bytes':int(subprocess.check_output(['/usr/sbin/sysctl','-n','hw.memsize'],text=True)),'private_process_inventory':str(private),'active_compiled':active,'plan_manifest_sha256':MANIFEST,'source_review':pin}
f=Path(__file__).parent/(phase+'-preflight.json');assert not f.exists();f.write_text(json.dumps(preflight,indent=2)+'\n')
result=c.observe(pre,phase,MANIFEST,pin)
print(json.dumps({'phase':phase,'returncode':result.returncode,'mandatory_reap':result.receipt['mandatory_reap'],'elapsed_seconds':result.receipt['elapsed_seconds']}));sys.exit(result.returncode)
