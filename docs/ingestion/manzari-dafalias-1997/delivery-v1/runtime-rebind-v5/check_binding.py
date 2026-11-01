"""Read-only runtime/artifact/delegate identity verification, not source accuracy."""
from pathlib import Path
import argparse,json
from preflight import D,P,sha,check,build_binding

def verify(folder,study):
 folder=Path(folder).resolve();current=check();b=json.loads((folder/'runtime-binding.json').read_text());report=json.loads((folder/'report.json').read_text())
 for k in ['identity','source_freeze_sha256','source_directory','source_files','full_freeze_sha256','rebind_manifest_sha256']:assert b[k]==current[k],k
 assert b['study']==study and b['delegate_returncode']==0,'study/delegate outcome'
 assert b['report_sha256']==sha(folder/'report.json'),'raw report identity'
 receipt=folder/'coordinator-build-receipt.json';assert sha(receipt)==b['coordinator_build_receipt_sha256'],'saved external receipt'
 actual=build_binding(receipt,b['backend'],b['artifact_path'])
 for k in ['backend','artifact_path','artifact_sha256','generated_catalogue_sha256','wasm_sha256','build_log_sha256']:assert actual[k]==b[k],k
 delegate=P/('resolution-study-v4/run_native.py'if study=='md'else 'ordinary-regression-v7/run.py'if study=='ordinary'else 'execution-v3/run_native.py');assert b['delegate_sha256']==sha(delegate) and Path(b['delegate_path'])==delegate,'delegate identity'
 if study=='ordinary':
  policy=json.loads((P/'ordinary-regression-v7/policy.json').read_text());assert report['identity']=='md1997-ordinary-regression-v7' and report['backend']==b['backend'] and report['artifact_sha256']==b['artifact_sha256'];assert report['policy_sha256']==sha(P/'ordinary-regression-v7/policy.json') and report['manifest_sha256']==sha(P/'ordinary-regression-v7/manifest.json');assert [c['model']for c in report['cases']]==[c['model']for c in policy['cases']] and report['passed']is True and all(c['passed']is True for c in report['cases']);assert not b['subset']
 else:
  base=P/('resolution-study-v4'if study=='md'else 'execution-v3');identity=report['identity'];assert identity['backend']==b['backend'] and identity['artifact_sha256']==b['artifact_sha256']
  for k,n in [('requests_sha256','requests.json'),('policy_sha256','POLICY.md'),('manifest_sha256','manifest.json')]:assert identity[k]==sha(base/n),k
  assert identity['model_sha256']==json.loads((base/'requests.json').read_text())['model_sha256']
  if b['backend']=='wasm':assert identity['wasm_binary_sha256']==b['wasm_sha256']
  expected=[c['id']for c in json.loads((base/'requests.json').read_text())['cases']] if study=='md'else [json.loads((D/'coarse-diagnostic-policy.json').read_text())['case']['id']]
  assert list(report['cases'])==expected,'complete exact study case order';assert b['subset']==([]if study=='md'else expected)
 return {'identity':'md1997-control-runtime-saved-binding-v5','passed':True,'study':study,'backend':b['backend'],'source_freeze_sha256':b['source_freeze_sha256'],'runtime_binding_sha256':sha(folder/'runtime-binding.json'),'report_sha256':sha(folder/'report.json'),'scope':'identity and complete case coverage; MD/coarse numerical/operational checkers remain separately mandatory'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--study',choices=['md','ordinary','coarse'],required=True);p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output);assert not out.exists(),'preserve prior evidence';r=verify(a.folder,a.study);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
