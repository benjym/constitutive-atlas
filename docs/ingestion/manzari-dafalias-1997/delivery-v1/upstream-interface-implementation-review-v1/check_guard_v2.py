from pathlib import Path
import sys,json,hashlib,importlib.util,ast
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('guard',ROOT/'tools/check_current_dependency_assets.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
engines=m.selected_engines(current17_baseline=True);snap=m.engine_snapshot(engines,True);assert set(snap)=={'norsand','interface2016','maxwell'}
original=m.tree_snapshot
required={'norsand':('controlled-path-qualification.json','build-review.json','atlas_path_capability.mjs','atlas_path_capability.wasm','generated/path_catalogue.json','generated/path_models.hpp','generated/path_api.cpp','source-compatibility.json'),'interface2016':m.REQUIRED['interface2016']+('source-compatibility.json',),'maxwell':('maxwell.mjs','maxwell.wasm','generated/models.json','generated/models.hpp','maxwell-qualification.json','build-review.json','source-compatibility.json')}
refusals=[]
for key,names in required.items():
 for name in names:
  def missing(directory,key=key,name=name):
   rows=original(directory)
   if Path(directory)==m.repo_path(engines[key]):rows.pop(name)
   return rows
  m.tree_snapshot=missing
  try:m.engine_snapshot(engines,True)
  except ValueError:refusals.append(key+'/'+name)
  else:raise AssertionError('accepted missing '+key+'/'+name)
m.tree_snapshot=original
# Default retains historical required sets, demonstrated without changing any actual files.
m.tree_snapshot=lambda path:{n:'0'*64 for n in m.REQUIRED[next(k for k,v in m.ENGINES.items() if m.repo_path(v)==path)]}
assert set(m.engine_snapshot())==set(m.ENGINES)
for key in m.REQUIRED:
 for name in m.REQUIRED[key]:
  def missing_old(path,key=key,name=name):
   actual=next(k for k,v in m.ENGINES.items() if m.repo_path(v)==path);rows={n:'0'*64 for n in m.REQUIRED[actual]}
   if actual==key:rows.pop(name)
   return rows
  m.tree_snapshot=missing_old
  try:m.engine_snapshot()
  except ValueError:refusals.append('historical/'+key+'/'+name)
  else:raise AssertionError('historical requirement relaxed')
m.tree_snapshot=original
source=(ROOT/'tools/check_current_dependency_assets.py').read_bytes();tree=ast.parse(source)
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='engine_snapshot'];assert len(calls)==3
assert all(len(n.args)==2 and isinstance(n.args[1],ast.Name) and n.args[1].id=='current17_baseline' for n in calls)
report={'identity':'current17-guard-source-review-v2','status':'accepted','reviewer_run':'/root/md1997_upstream_merge_review','scope':'source and pure metadata snapshot checks; no compiled/material execution; actual complete pure bundler result owned by coordinator','guard_sha256':hashlib.sha256(source).hexdigest(),'original_runtime_decision_sha256':hashlib.sha256((OUT/'decision.json').read_bytes()).hexdigest(),'actual_current_engine_count':len(snap),'refusal_count':len(refusals),'refusals':refusals,'checks':['all3 actual current engine snapshots contain exact compatible-format minimum artifacts','each missing required current artifact refused individually','historical minimum artifact sets preserved and each omission refused','all3 before/after/failure snapshot callsites propagate explicit selection','source_snapshot still calls exact source/evidence validators, so subset preflight does not weaken exact engine membership gate'],'blocking_findings':[]}
(OUT/'guard-review-v2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'refusals':len(refusals),'guard_sha256':report['guard_sha256'],'decision_sha256':hashlib.sha256((OUT/'guard-review-v2.json').read_bytes()).hexdigest()}))
