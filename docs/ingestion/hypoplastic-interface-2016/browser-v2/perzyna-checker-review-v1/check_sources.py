"""Independent small source/memory checks; never call checker main or an engine."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=HERE.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sha(B/'perzyna-checker-freeze.json')=='3aed0dcf5814952f7fbccf8e4466ec47abe2ed252fc0749656ec11c339244a21'
 manifest=json.loads((B/'perzyna-checker-freeze.json').read_text())
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
 accepted=[]
 for mode,index in [('rate',2),('relaxation',2),('creep',0)]:
  bad=copy.deepcopy(runs);bad[mode]['result']['points'][index]['strain_rate']=[1e99]*6
  if mode=='relaxation':bad['reset']=copy.deepcopy(bad[mode]);bad['replay']=copy.deepcopy(bad[mode])
  C.assess(identity,bad,rev,policy,refs);accepted.append({'mode':mode,'point':index,'mutation':'strain_rate=[1e99]*6','accepted':True})
 report={'scope':'source and bounded Git-read historical bytes; memory-only synthetic revision/rate mutation; no new exports/browser/module/material/package/remote','manifest_sha256':sha(B/'perzyna-checker-freeze.json'),'checker_sha256':sha(B/'check_perzyna_exports.py'),'all_manifest_members_match':True,'historical_revision':historical_revision,'memory_only_revision':rev,'baseline_comparisons':342,'accepted_metadata_faults':accepted}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
