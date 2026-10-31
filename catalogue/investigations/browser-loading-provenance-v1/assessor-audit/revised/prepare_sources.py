from pathlib import Path
import shutil,subprocess,os
s=Path(__file__).parent;r=Path('/Users/bmar5496/code/constitutive-atlas');f=s/'frozen'
for folder in ['cpp','atlas','schemas']:
 shutil.copytree(r/folder,f/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(f/'models').mkdir()
for p in (r/'models').glob('*.json'):shutil.copyfile(p,f/'models'/p.name)
(s/'tools').mkdir();(s/'tests').mkdir()
for name in ['build_web.py','test_web_package.mjs','test_numerics.mjs','test_wasm.mjs']:
 shutil.copyfile(r/'tools'/name,s/'tools'/name)
shutil.copyfile(r/'tests/test_web_package.mjs',s/'tests/test_web_package.mjs')
shutil.copyfile(r/'tests/test_browser_numerics.py',s/'tests/test_browser_numerics.py')
subprocess.run(['python3','-B','-m','atlas.compiler',str(s/'generated')],cwd=f,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),check=True)
# Package/default smoke uses the same current loading choice as the browser.
p=s/'tools/build_web.py';t=p.read_text().replace("'numerics.mjs','recorded.mjs'","'numerics.mjs','loading.mjs','recorded.mjs'");p.write_text(t)
p=s/'tools/test_web_package.mjs';t=p.read_text().replace("'numerics.mjs','recorded.mjs'","'numerics.mjs','loading.mjs','recorded.mjs'")
t=t.replace(" const engine=await createAtlas();"," const {createLoading}=await import(pathToFileURL(join(directory,'loading.mjs')));\n const engine=await createAtlas();")
t=t.replace('  const result=runLaboratory(engine,specification);','  specification.loading=createLoading(specification);\n  const result=runLaboratory(engine,specification,metadata.sha256);');p.write_text(t)
p=s/'tests/test_web_package.mjs';t=p.read_text().replace("'numerics.mjs','recorded.mjs'","'numerics.mjs','loading.mjs','recorded.mjs'");p.write_text(t)
