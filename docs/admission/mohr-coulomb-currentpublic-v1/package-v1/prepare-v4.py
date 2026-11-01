from pathlib import Path
import json,hashlib,shutil,sys,subprocess
p=Path('/Users/bmar5496/code/constitutive-atlas/docs/admission/mohr-coulomb-currentpublic-v1/package-v1');root=Path('/private/tmp/atlas-mc-admission-public-v1');retained=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((p/'freeze-v3.json').read_text());assert json.loads((p/'build-attempt2-status.json').read_text())['exit_code']==1
interface=json.loads((Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/package-v7/engine-implicit-path/interface-review.json')).read_text());restored={}
for n,h in interface['files'].items():
 target=root/n
 if target.is_file():assert sha(target)==h,n
 else:
  source=retained/n;assert sha(source)==h,n
  assert n.startswith('.local/') and '..' not in Path(n).parts
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);restored[n]=h
assert len(restored)==1
f['id']='mohr-coulomb-current-public-package-v4';f['supersedes_preparation_only']='freeze-v3.json; full retry failure preserved';f['source_support']=restored
f['source_support_provenance']={'interface_review_sha256':sha(Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/package-v7/engine-implicit-path/interface-review.json')),'retained_root':str(retained),'reason':'Fresh worktree lacks one git-ignored authored numerical request required by unchanged interface evidence guard; exact receipt-pinned bytes restored, no request/reference/guard edits'}
f['command']=[x.replace('/private/tmp/atlas-mc-package-v1/site-v2','/private/tmp/atlas-mc-package-v1/site-v3') for x in f['command']]
(p/'freeze-v4.json').write_text(json.dumps(f,indent=2)+'\n')
# Same identity preflight, with explicit additional ignored support-file guard.
s=(p/'preflight.py').read_text();s=s.replace("    count=0", "    for name,expected in record.get('source_support',{}).items():\n        support=root/name\n        if not support.is_file() or hashlib.sha256(support.read_bytes()).hexdigest()!=expected:errors.append('Source supporting input changed: '+name)\n    count=0")
(p/'preflight-v4.py').write_text(s)
plan=json.loads((p/'execution-plan-v3.json').read_text());plan['freeze']='freeze-v4.json';plan['freeze_sha256']=sha(p/'freeze-v4.json');plan['commands']['preflight']=['python3','-B',str(p/'preflight-v4.py'),str(p/'freeze-v4.json'),'--report',str(p/'attempt3-preflight.json')];plan['commands']['standard_package']=f['command'];plan['commands']['supported_package']=[x.replace('/private/tmp/atlas-mc-package-v1/site-v2','/private/tmp/atlas-mc-package-v1/site-v3') for x in plan['commands']['supported_package']];(p/'execution-plan-v4.json').write_text(json.dumps(plan,indent=2)+'\n')
# Remaining bundle routines contain no material execution. Run exact source guards
# into a separate destination, preserving both incomplete failed packages.
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'tools'))
from tools.build_implicit_path_laboratory import bundle as implicit
from tools.build_orthotropic_laboratory import bundle as orthotropic
from tools.build_hill_laboratory import bundle as hill
out=Path('/private/tmp/atlas-mc-package-v1/remaining-source-preflight');assert not out.exists();out.mkdir()
results={}
for name,fun,flag in [('implicit_path',implicit,'--implicit-path-wasm-dir'),('orthotropic',orthotropic,'--orthotropic-wasm-dir'),('hill',hill,'--hill-wasm-dir')]:
 fun(out,Path(f['engines'][flag]['path']));results[name]='passed exact unchanged source/qualification/interface guards; no material call'
(p/'remaining-source-preflight.json').write_text(json.dumps({'status':'passed','compiled_calls':0,'restored_source_support':restored,'bundlers':results},indent=2)+'\n')
shutil.copyfile(__file__,p/'prepare-v4.py');shutil.copyfile('/private/tmp/check-mc-package-database.py',p/'check-database.py')
(p/'ATTEMPT2.md').write_text('# Attempt2 retained; exact support restoration\n\nThe second full build passed earlier mandatory gates, packaged NorSand and Maxwell, then exited1 at the implicit-path interface guard because one ignored `.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json` request was absent from the fresh worktree. The existing accepted interface receipt pins its exact hash. The original retained release source supplies matching bytes. No numerical request, reference, source, model, interface guard or tolerance changed.\n\n`freeze-v4.json` pins the restored supporting file explicitly in addition to the clean source commit and43engine inputs. A new source-only preflight ran all remaining implicit-path/orthotropic/Hill bundle guards successfully in a separate directory, without executing any material module. The third full builder must still run unchanged into a new `site-v3`; attempts1/2 are preserved.\n')
print(json.dumps({'restored_support_files':len(restored),'remaining_bundle_source_guards':results,'compiled_calls':0}))
