from pathlib import Path
import json,hashlib,shutil,subprocess,sys,tempfile
packet=Path('/Users/bmar5496/code/constitutive-atlas/docs/admission/mohr-coulomb-currentpublic-v1/package-v1')
root=Path('/private/tmp/atlas-mc-admission-public-v1');qualified=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/package-v7')
old=json.loads((packet/'freeze.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs={
 '--wasm-dir':('',{'atlas.js':'atlas.js','atlas.wasm':'atlas.wasm','generated/models.json':'models.json'}),
 '--power-creep-wasm-dir':('engine',{'power-creep.js':'power-creep.js','power-creep.wasm':'power-creep.wasm','power-creep-generated/models.json':'models.json','generated/models.json':'models.json'}),
 '--sls-wasm-dir':('engine-sls',{'sls.mjs':'sls.mjs','sls.wasm':'sls.wasm','generated/models.json':'models.json'}),
 '--burgers-wasm-dir':('engine-burgers',{'burgers.mjs':'burgers.mjs','burgers.wasm':'burgers.wasm','generated/models.json':'models.json'}),
 '--j2-wasm-dir':('material-point-j2',{'j2.js':'j2.js','j2.wasm':'j2.wasm','generated/models.json':'models.json'}),
 '--controlled-path-wasm-dir':('engine-path',{'atlas_path_capability.mjs':'engine.mjs','atlas_path_capability.wasm':'engine.wasm','generated/path_catalogue.json':'catalogue.json'}),
 '--maxwell-wasm-dir':('engine-maxwell',{'maxwell.js':'maxwell.mjs','maxwell.wasm':'maxwell.wasm','generated/models.json':'models.json'}),
 '--implicit-path-wasm-dir':('engine-implicit-path',{'lade-domain.mjs':'lade-domain.mjs','lade-domain.wasm':'lade-domain.wasm','generated/models.json':'models.json'}),
 '--orthotropic-wasm-dir':('material-point-orthotropic',{'orthotropic.js':'orthotropic.js','orthotropic.wasm':'orthotropic.wasm','generated/models.json':'models.json'}),
 '--hill-wasm-dir':('material-point-hill',{'hill.js':'hill.js','hill.wasm':'hill.wasm','generated/models.json':'models.json'}),
 '--kelvin-voigt-wasm-dir':('engine-kelvin-voigt',{'kv.mjs':'kv.mjs','kv.wasm':'kv.wasm','generated/models.json':'models.json'})}
new={k:v for k,v in old.items() if k not in ['engines','command','preflight_failure']};new['id']='mohr-coulomb-current-public-package-v2';new['supersedes_preparation_only']='freeze.json';new['engine_provenance']=[];new['engines']={};mismatches=[]
for flag,entry in old['engines'].items():
 d=Path('/private/tmp/atlas-mc-package-v1/engines-v2')/flag[2:];assert not d.exists();d.mkdir(parents=True)
 for name,h in entry['files'].items():
  src=Path(entry['path'])/name
  assert sha(src)==h,src
  target=d/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 sub,mapping=pairs[flag]
 for target_name,source_name in mapping.items():
  source=qualified/sub/source_name;target=d/target_name
  previous=sha(target) if target.exists() else None
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  assert target.read_bytes()==source.read_bytes()
  row={'flag':flag,'target':target_name,'qualified_package_file':str(source),'sha256':sha(source),'previous_sha256':previous}
  new['engine_provenance'].append(row)
  if previous!=sha(source):mismatches.append(row)
 new['engines'][flag]={'path':str(d),'files':{str(p.relative_to(d)):sha(p) for p in sorted(d.rglob('*')) if p.is_file()}}
new['preparation_mismatches']=mismatches
new['command']=[sys.executable,'-B',str(root/'tools/build_web.py')]
for flag,e in new['engines'].items():new['command'].extend([flag,e['path']])
new['command'].extend(['--output','/private/tmp/atlas-mc-package-v1/site'])
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==new['source_commit']
sys.path.insert(0,str(root));from atlas.compiler import generate
with tempfile.TemporaryDirectory() as tmp:
 generate(tmp);assert (Path(tmp)/'models.json').read_bytes()==(Path(new['engines']['--wasm-dir']['path'])/'generated/models.json').read_bytes()
new['preparation_checks']={'all_11_engines_snapshotted':True,'every_module_wasm_and_catalogue_exact_qualified_package_bytes':True,'ordinary_current_generation_exact':True,'profile_source_checker':'47/47 passed, exit0; source-only'}
(packet/'freeze-v2.json').write_text(json.dumps(new,indent=2)+'\n')
(packet/'PREPARATION.md').write_text('# Qualification inputs prepared, execution pending\n\nThe first preparation is retained as `freeze.json`. A complete cross-check then found that the retained controlled-path and Kelvin module/Wasm pairs also differed from the qualified Kelvin v7 package. No compiled result was observed and no gate changed.\n\n`freeze-v2.json` supersedes those execution inputs. Every engine now has its own private snapshot. All eleven module/Wasm/catalogue sets are byte-identical to the qualified full package; copied supporting generated source and qualification receipts remain hash-pinned. The normal current catalogue generation matches the retained ordinary catalogue exactly. The public-profile source checker passes all 47 catalogue entries.\n\nThis is preparation, not current package or browser qualification. Run the recorded unchanged complete builder only after a fresh execution-slot handoff and a passing preflight. Its own exact-source and qualification guards remain mandatory. Keep any failure; do not edit the model, references, tolerances or admission requirements to make packaging pass.\n')
shutil.copyfile('/private/tmp/prepare-mc-package-v1.py',packet/'prepare-v1.py');shutil.copyfile(__file__,packet/'snapshot-v2.py')
print(json.dumps({'engine_profiles':len(new['engines']),'qualified_asset_comparisons':len(new['engine_provenance']),'preparation_mismatches':len(mismatches),'compiled_execution':False}))
