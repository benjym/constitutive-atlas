import importlib.util,io,json,tempfile,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4]
spec=importlib.util.spec_from_file_location('proposed_markup',B/'test_browser_numerics.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def run(root):
 m.ROOT=root;stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromModule(m));return result.wasSuccessful(),stream.getvalue()
passed,log=run(R);assert passed,log
results={'unchanged_app_passes':passed,'mutation_rejections':{}}
for name in ['missing_creation','mandatory_cleanup','missing_static_control']:
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp);(root/'web').mkdir();app=(R/'web/app.js').read_text();html=(R/'web/index.html').read_text()
  if name=='missing_creation':app=app.replace("link.id='model-profile-link';",'')
  if name=='mandatory_cleanup':app=app.replace("$('model-profile-link')?.remove()","$('model-profile-link').remove()")
  if name=='missing_static_control':html=html.replace('id="result-note"','')
  (root/'web/app.js').write_text(app);(root/'web/index.html').write_text(html);ok,detail=run(root);assert not ok,name
  results['mutation_rejections'][name]=True
(B/'check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results));print(log)
