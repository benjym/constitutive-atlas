"""Independent small source/memory checks; never call checker main or an engine."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(B/'freeze.json')=='4762cf7ec408e1868f227eef970fe2fbb12b07144836a45200f4d09aeb3792a0'
 manifest=json.loads((B/'freeze.json').read_text())
 for item in manifest['files']:assert sha(B/item['path'])==item['sha256']
 spec=importlib.util.spec_from_file_location('read_only_perzyna_checker',B/'check_perzyna_exports.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
 rev=C.REVISION
 def read(n):return subprocess.check_output(['git','show',rev+':'+n],cwd=ROOT)
 policyraw=read(str(C.POLICY.relative_to(C.ROOT)));caseraw=read(str(C.CASES.relative_to(C.ROOT)))
 assert hashlib.sha256(policyraw).hexdigest()==C.POLICY_SHA and hashlib.sha256(caseraw).hexdigest()==C.CASES_SHA
 policy=json.loads(policyraw);cases=json.loads(caseraw)['cases'];refs={m:next(c for c in cases if c['id']=='public-'+m) for m in ['relaxation','creep','rate']}
 runs={m:json.loads(read('docs/ingestion/perzyna-comsol63/browser-v1/artifacts/'+m+'.json')) for m in refs}
 historical_revision=runs['relaxation']['provenance']['release_revision']
 for run in runs.values():run['provenance']['release_revision']=rev
 runs['reset']=copy.deepcopy(runs['relaxation']);runs['replay']=copy.deepcopy(runs['relaxation']);identity=copy.deepcopy(runs['relaxation']['provenance'])
 base=C.assess(identity,runs,rev,policy,refs);assert base['frozen_component_comparisons']==342
 rejected=[]
 for mode,index in [('rate',2),('relaxation',2),('creep',0)]:
  bad=copy.deepcopy(runs);bad[mode]['result']['points'][index]['strain_rate']=[1e99]*6
  if mode=='relaxation':bad['reset']=copy.deepcopy(bad[mode]);bad['replay']=copy.deepcopy(bad[mode])
  try:C.assess(identity,bad,rev,policy,refs)
  except ValueError as e:rejected.append({'mode':mode,'point':index,'mutation':'strain_rate=[1e99]*6','rejected':True,'reason':str(e)})
  else:raise AssertionError('Original fault still accepted')
 proof=json.loads((B/'perzyna-checker-proof.json').read_text());assert proof['rejected_faults']==276
 old=B.parent;oldfreeze=json.loads((old/'perzyna-checker-freeze.json').read_text());assert all(sha(old/i['path'])==i['sha256'] for i in oldfreeze['files'])
 report={'retained_author_fault_rejections':276,'v1_all_pins_unchanged':True,'scope':'source and bounded Git-read historical bytes; memory-only synthetic revision/rate mutation; no new exports/browser/module/material/package/remote','manifest_sha256':sha(B/'freeze.json'),'checker_sha256':sha(B/'check_perzyna_exports.py'),'all_manifest_members_match':True,'historical_revision':historical_revision,'memory_only_revision':rev,'baseline_comparisons':342,'rejected_original_metadata_faults':rejected}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
