from pathlib import Path
import shutil,subprocess,hashlib,json,runpy
repo=Path('/Users/bmar5496/code/constitutive-atlas')
base=Path('/private/tmp/barodesy2017-description-context-v1')
base.mkdir(exist_ok=True)
site=base/'site'
assert not site.exists()
shutil.copytree('/private/tmp/barodesy2017-ncl-browser-v1/site',site)
head=subprocess.check_output(['git','show','HEAD:web/app.js'],cwd=repo).decode()
transform=runpy.run_path('/private/tmp/transform_description_context_app.py')['transform']
(site/'app.js').write_text(transform(head))
(site/'formulation-view.mjs').write_bytes((repo/'web/formulation-view.mjs').read_bytes())
(site/'timed-route.mjs').write_bytes(subprocess.check_output(['git','show','HEAD:web/timed-route.mjs'],cwd=repo))
manifest={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
(base/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(base/'release-evidence').unlink(missing_ok=True)
print(json.dumps({'assets':len(manifest),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip(),'app_sha256':manifest['app.js']}))
