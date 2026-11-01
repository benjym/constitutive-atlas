from pathlib import Path
import json,hashlib,subprocess,tarfile,shutil
r=Path('/Users/bmar5496/code/constitutive-atlas');plan=r/'docs/reviews/mc-browser-plan-v3';stage=Path('/private/tmp/atlas-mc-private-package-v3-attempt4')
assert not stage.exists(),'Refuse overwrite'
stage.mkdir();src=stage/'source';src.mkdir();engine=stage/'engine';engine.mkdir();(engine/'generated').mkdir()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
base=json.loads((plan/'baseline.json').read_text())
archive=stage/'source.tar'
with archive.open('wb')as out:subprocess.run(['git','archive',base['source_commit']],cwd=r,stdout=out,check=True)
with tarfile.open(archive)as t:t.extractall(src,filter='data')
for f in (plan/'proposed').rglob('*'):
 if f.is_file():dest=src/f.relative_to(plan/'proposed');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
fix=r/'docs/reviews/gis-example-twelve-catalogue-v1'
fixmanifest=json.loads((fix/'manifest.json').read_text())
for rel,expected in fixmanifest['files'].items():assert sha(fix/rel)==expected
for f in (fix/'proposed').rglob('*'):
 if f.is_file():dest=src/f.relative_to(fix/'proposed');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
app=r/'docs/reviews/mc-applicability-entry-v1'
for rel,expected in json.loads((app/'manifest.json').read_text())['files'].items():assert sha(app/rel)==expected
for f in (app/'proposed').rglob('*'):
 if f.is_file():dest=src/f.relative_to(app/'proposed');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
display=r/'docs/reviews/matching-input-disclosure-v1'
for rel,expected in json.loads((display/'manifest.json').read_text())['files'].items():assert sha(display/rel)==expected
for f in (display/'proposed').rglob('*'):
 if f.is_file():dest=src/f.relative_to(display/'proposed');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
qualified=Path('/private/tmp/atlas-mc-execution-v3/wasm')
policy=json.loads((plan/'protocol.json').read_text())
for name,expected in policy['qualified_engine'].items():
 f=qualified/'build'/name;assert sha(f)==expected;shutil.copyfile(f,engine/name)
shutil.copyfile(qualified/'generated/models.json',engine/'generated/models.json')
receipt={'source_commit':base['source_commit'],'source_archive_sha256':sha(archive),'plan_manifest_sha256':sha(plan/'manifest.json'),'qualified_engine':policy['qualified_engine'],'generated_catalogue_sha256':sha(engine/'generated/models.json'),'overlays':{str(f.relative_to(plan/'proposed')):sha(f) for f in (plan/'proposed').rglob('*')if f.is_file()},'new_build':False}
receipt.update(example_fix_manifest_sha256=sha(fix/'manifest.json'),example_fix_overlays={str(f.relative_to(fix/'proposed')):sha(f) for f in (fix/'proposed').rglob('*')if f.is_file()})
receipt.update(applicability_manifest_sha256=sha(app/'manifest.json'),applicability_overlays={str(f.relative_to(app/'proposed')):sha(f) for f in (app/'proposed').rglob('*')if f.is_file()})
receipt.update(disclosure_manifest_sha256=sha(display/'manifest.json'),disclosure_overlays={str(f.relative_to(display/'proposed')):sha(f) for f in (display/'proposed').rglob('*')if f.is_file()})
(stage/'prepackage.json').write_text(json.dumps(receipt,indent=2)+'\n')
cmd=['python3','-B',str(src/'tools/build_web.py'),'--wasm-dir',str(engine),'--output',str(stage/'site/constitutive-atlas')]
with (stage/'package.stdout').open('w')as out,(stage/'package.stderr').open('w')as err:result=subprocess.run(cmd,cwd=src,stdout=out,stderr=err)
receipt.update(command=cmd,returncode=result.returncode)
(stage/'package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'returncode':result.returncode,'stdout':(stage/'package.stdout').read_text()[-3000:],'stderr':(stage/'package.stderr').read_text()[-4000:]}))
if result.returncode==0:
 site=stage/'site/constitutive-atlas';files={str(f.relative_to(site)):sha(f)for f in sorted(site.rglob('*'))if f.is_file()};(stage/'package-files.json').write_text(json.dumps({'files':files},indent=2)+'\n');print(f'Packaged {len(files)} files')
