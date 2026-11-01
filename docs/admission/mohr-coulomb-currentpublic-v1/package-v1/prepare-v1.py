from pathlib import Path
import hashlib,json,subprocess,shutil,tempfile,sys
root=Path('/private/tmp/atlas-mc-admission-public-v1')
retained=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1')
packet=Path('/Users/bmar5496/code/constitutive-atlas/docs/admission/mohr-coulomb-currentpublic-v1/package-v1')
private=Path('/private/tmp/atlas-mc-package-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert git('rev-parse','HEAD')=='000ab5e79619038e0b56483e0146cf2e9ce4bd18'
assert not git('status','--porcelain','--untracked-files=no')
assert not packet.exists()
private.mkdir(exist_ok=True)
sls=private/'sls-engine';(sls/'generated').mkdir(parents=True,exist_ok=True)
for a,b in [('sls.mjs','sls.mjs'),('sls.wasm','sls.wasm'),('models.json','generated/models.json')]:
 source=retained/'package-v7/engine-sls'/a;target=sls/b
 assert not target.exists() or target.read_bytes()==source.read_bytes()
 shutil.copyfile(source,target)
main=private/'ordinary-engine';(main/'generated').mkdir(parents=True,exist_ok=True)
qualified=json.loads(Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/kelvin-voigt-comsol63/package-v7/freeze.json').read_text())['ordinary_engine']
for a,b in [('atlas.js','atlas.js'),('atlas.wasm','atlas.wasm'),('models.json','generated/models.json')]:
 source=retained/'package-v7'/a;target=main/b
 assert sha(source)==qualified[b]
 assert not target.exists() or target.read_bytes()==source.read_bytes()
 shutil.copyfile(source,target)
engines={
 '--wasm-dir':main,
 '--power-creep-wasm-dir':retained/'power-engine',
 '--sls-wasm-dir':sls,
 '--burgers-wasm-dir':retained/'burgers-engine',
 '--j2-wasm-dir':retained/'j2-engine',
 '--controlled-path-wasm-dir':Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/norsand-1993/shared-integration-v1/wasm-v2'),
 '--maxwell-wasm-dir':retained/'maxwell-engine',
 '--implicit-path-wasm-dir':retained/'implicit-engine',
 '--orthotropic-wasm-dir':retained/'orthotropic-engine',
 '--hill-wasm-dir':root/'web/engines/hill',
 '--kelvin-voigt-wasm-dir':retained/'wasm'}
# Freeze only engine inputs, excluding build products not consumed by packaging.
inputs={}
for flag,d in engines.items():
 files=[p for p in d.iterdir() if p.is_file() and p.suffix in {'.js','.mjs','.wasm','.json'}]
 for sub in ['generated','power-creep-generated']:
  if (d/sub).is_dir():files.extend(p for p in (d/sub).rglob('*') if p.is_file())
 inputs[flag]={'path':str(d),'files':{str(p.relative_to(d)):sha(p) for p in sorted(files)}}
for n in ['atlas.js','atlas.wasm']:
 assert sha(main/n)==sha(retained/'package-v7'/n)
sys.path.insert(0,str(root));from atlas.compiler import generate
with tempfile.TemporaryDirectory() as tmp:
 generate(tmp)
 assert (Path(tmp)/'models.json').read_bytes()==(main/'generated/models.json').read_bytes()
ordinary=json.loads((main/'generated/models.json').read_text())
assert any(m['id']=='mohr-coulomb' for m in ordinary['models'])
command=[sys.executable,'-B',str(root/'tools/build_web.py')]
for flag,d in engines.items():command.extend([flag,str(d)])
command.extend(['--output',str(private/'site')])
freeze={'id':'mohr-coulomb-current-public-package-v1','status':'prepared-source-only','source_commit':git('rev-parse','HEAD'),'source_tree':git('rev-parse','HEAD^{tree}'),'source_clean_tracked':True,'engines':inputs,'command':command,'preflight_failure':{'command':'prepare-mc-package-v1.py initial attempt','exit_code':1,'condition':'retained main-engine differs from qualified package-v7','main_engine_wasm_sha256':sha(retained/'main-engine/atlas.wasm'),'main_engine_catalogue_sha256':sha(retained/'main-engine/generated/models.json'),'resolution':'Use exact package-v7 ordinary bytes verified against prospective freeze, copied to dedicated input directory'},'execution':'NOT STARTED; waiting for explicit release and fresh serial claim','ordinary_catalogue_exact_generated_match':True,'ordinary_catalogue_contains_mohr_coulomb':True,'acceptance':['Unchanged complete standard builder and every mandatory profile gate','Unchanged supported-package ordinary and named-example gates','All prior approvals preserved; MC actual accepted/current/registered in full exports','Actual browser model profile, source and review hyperlinks, experiment run, export/import/replay/recovery and routing'],'no_claim':['Current package success','Real browser success','Scientific experimental validation','Live deployment']}
packet.mkdir(parents=True)
(packet/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
(packet/'PLAN.md').write_text('# Mohr–Coulomb current-public package qualification\n\nSource-only preparation uses local commit `000ab5e79619038e0b56483e0146cf2e9ce4bd18`, based on public `e32f8a86df44298f100394b34e084e313d48b195`. The source is clean. The normal generator produces exactly the retained ordinary engine catalogue, including Mohr–Coulomb. No model, runtime, gate or web source changes are needed.\n\n`freeze.json` records the complete standard builder command and exact retained engine inputs before execution. Ordinary and SLS inputs are byte-identical copies of the qualified Kelvin v7 package engine in the layout required by the unchanged builder. The initial preparation rejected the mutable main-engine directory because both Wasm and catalogue hashes differed. Its failure and resolution are retained in freeze.json; the ordinary replacement matches the original prospective Kelvin v7 freeze and current generated catalogue. Other inputs retain their original paths. No compiled call has run for this task.\n\nWait for the active regression owner to release the serial slot; freshly check the board and process state, claim this execution, verify all source and engine pins, then run the command once with a full exit receipt and log. Preserve any failures. Run the unchanged supported-package checks and actual browser qualification only after a successful complete package. Do not mark E7 or E8 complete from this preparation. No build, push, deployment or remote CI is authorized by this packet.\n')
board=packet.parents[3]/'IMPLEMENTATION_PLAN.md'
assert board==Path('/Users/bmar5496/code/constitutive-atlas/IMPLEMENTATION_PLAN.md'),board
s=board.read_text();line=next(x for x in s.splitlines() if '**PACKAGE-mohr-coulomb-currentpublic-v1**' in x)
new=line.replace('- [ ]','- [-]',1)+' Source-only preparation claimed /root 2026-11-02; exact immutable source commit and retained engine inputs/unchanged full command frozen in package-v1. No serial slot claimed, no compiled calls; queued behind active regressions.'
assert s.count(line)==1
board.write_text(s.replace(line,new,1))
print(json.dumps({'packet':str(packet),'engine_profiles':len(inputs),'engine_files':sum(len(v['files']) for v in inputs.values()),'source_commit':freeze['source_commit'],'catalogue_exact':True,'compiled_execution':False}))
