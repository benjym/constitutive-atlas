"""Nonexecuting interface probes plus exact frozen/saved-result verification."""
import argparse, ast, hashlib, importlib, importlib.abc, importlib.machinery, importlib.util, json, os, pathlib, tempfile
from pathlib import Path

def require(x,m):
 if not x:raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--candidate-result',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();root=a.repo.resolve();packet=root/'docs/benchmarks/kfs-relocated-audit-v1';source=(packet/'replay.py').read_text();require(sha(packet/'replay.py')=='04e56165edc3a991db4582914901ebea83e367151cafa4f3de3c4784a97b6150','reviewed candidate changed');tree=ast.parse(source);body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main').body;checks=[]
 def passcheck(i,detail):checks.append({'id':i,'result':'pass','detail':detail})
 one=json.loads((packet/'freeze.json').read_text());two=json.loads((packet/'freeze-v2.json').read_text());require(one['public_files']==two['public_files'][:248] and len(two['public_files'])==249,'original248/supplemental249');require(two['public_files'][-1]['original_path'].endswith('/atlas/data.py'),'supplemental source');require(sha(packet/'freeze.json')==two['prior_freeze_sha256'],'freeze ancestry');passcheck('freeze_ancestry','248 original frozen inputs unchanged; exactly one supplemental atlas/data.py import dependency')
 recovery=json.loads((packet/'map-recovery.json').read_text());expanded_path=packet/'map-recovery-source.json';require(sha(expanded_path)==recovery['source_sha256'],'exact expanded recovery source');expanded=json.loads(expanded_path.read_text());expected=dict(expanded);expected['entries']=expected['entries'][:17];raw=(json.dumps(expected,indent=2)+'\n').encode();require(len(expected['documents'])==3,'three documents');require(hashlib.sha256(raw).hexdigest()==recovery['expected_sha256']==recovery['recovered_sha256'],'map exact recovery');require((root/recovery['snapshot']).read_bytes()==raw,'recovered bytes');passcheck('map_recovery','three documents/first17entries of expanded19 map recover exact original fc0e1bfc SHA; no repinning')
 receipt_path=root/two['private_receipts_path'];require(sha(receipt_path)==two['private_receipts_sha256'],'receipt frozen');receipt=json.loads(receipt_path.read_text());require(len(receipt['files'])==len(two['private_files'])==9423,'9423 bindings');require(len({x['origin'] for x in receipt['files']})==9423,'unique origins'); frozen_private={x['original_path']:x['sha256'] for x in two['private_files']};require(frozen_private=={x['origin']:x['sha256'] for x in receipt['files']},'freeze and receipt exact private binding equality');snapshot=root/two['public_root'];private=root/receipt['private_root'];pub={x['original_path']:x for x in two['public_files']};overlap=0
 for x in two['public_files']:require(sha(snapshot/x['retained_path'])==x['sha256'],'public retained bytes')
 for x in receipt['files']:
  p=private/x['retained_path'];require(p.is_file() and not p.is_symlink() and sha(p)==x['sha256'],'private retained bytes')
  if x['origin'] in pub:require(x['sha256']==pub[x['origin']]['sha256'],'overlap same bytes');overlap+=1
 require(overlap==4,'four identical overlaps');passcheck('all_retained_bytes',{'public':249,'private':9423,'identical_public_private_origin_overlaps':4})
 # Execute only actual helper definitions, with a small private synthetic fixture.
 names=['relocate','open_with','source_data','guard'];nodes=[n for n in body if isinstance(n,ast.FunctionDef) and n.name in names]
 with tempfile.TemporaryDirectory(prefix='kfs-relocation-independent-') as d:
  base=Path(d).resolve();retained=base/'retained';retained.mkdir();listed=retained/'listed.py';listed.write_text('sentinel = 1\n');extra=retained/'extra.txt';extra.write_text('not frozen');mapping={'/old/repo/listed.py':(listed,sha(listed)),'/old-download/source.pdf':(listed,sha(listed))};dirs={'/old/repo':str(retained)};direct=[str(retained)];env={'os':os,'Path':Path,'mapping':mapping,'dirs':dirs,'direct':direct,'retained_files':{str(listed.resolve())},'reads':set(),'denied':[],'raw_open':open}
  exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual-candidate-helpers>','exec'),env)
  require(env['relocate']('/old/repo/listed.py')==str(listed),'listed historical');require(env['relocate'](listed)==str(listed),'listed direct');require(env['relocate']('/old/repo/folder',metadata=True)==str(retained/'folder'),'metadata-only prefix')
  for p in ['/old/repo/extra.txt',extra]:
   try:env['relocate'](p)
   except FileNotFoundError:pass
   else:raise AssertionError('unlisted read accepted')
  require(env['source_data'](None,'/old/repo/listed.py')==listed.read_bytes(),'source exact bytes')
  for p in ['/old/repo/extra.txt','/old/repo/listed.pyc']:
   try:env['source_data'](None,p)
   except (FileNotFoundError,OSError):pass
   else:raise AssertionError('unlisted/cached source accepted')
  before=listed.read_bytes()
  try:env['open_with'](open,'/old/repo/listed.py','w')
  except PermissionError:pass
  else:raise AssertionError('frozen write allowed')
  require(listed.read_bytes()==before,'write rollback');passcheck('read_and_source_membership','listed reads exact; existing unlisted historical/direct reads reject; metadata prefix separate; source cache/unlisted reject; frozen write rejects')
  for event in ['subprocess.Popen','os.system','os.posix_spawn','os.exec','socket.__new__']:
   try:env['guard'](event,())
   except PermissionError:pass
   else:raise AssertionError('execution/network event not rejected: '+event)
  for p in ['/old/repo/listed.py','/old-download/source.pdf',str(extra)]:
   try:env['guard']('open',(p,'r',0))
   except PermissionError:pass
   else:raise AssertionError('raw original/unlisted input not rejected: '+p)
  env['guard']('open',(str(listed),'r',0));env['guard']('open',(str(base/'scratch.txt'),'w',0));passcheck('audit_guards','synthetic process/network events reject without launches; raw historical and out-of-root original source opens reject; listed retained/scratch events permitted')
  # Actual preflight expression rejects same-length corruption before audit execution.
  loop=next(n for n in body if isinstance(n,ast.For) and ast.unparse(n.target)=='(name, (p, h))')
  pe={'mapping':{'/old/repo/listed.py':(listed,sha(listed))},'hashlib':hashlib};exec(compile(ast.Module(body=[loop],type_ignores=[]),'<candidate-preflight>','exec'),pe);listed.write_text('sentinel = 2\n')
  try:exec(compile(ast.Module(body=[loop],type_ignores=[]),'<candidate-preflight>','exec'),pe)
  except AssertionError:pass
  else:raise AssertionError('same-length corrupt byte accepted')
  passcheck('integrity_preflight','actual candidate hash-check loop passes exact fixture and rejects same-length corruption')
 debug=next(n for n in body if isinstance(n,ast.If) and ast.unparse(n.test)=='not __debug__')
 try:exec(compile(ast.Module(body=[debug],type_ignores=[]),'<optimized-candidate-precheck>','exec',optimize=1),{})
 except RuntimeError:pass
 else:raise AssertionError('optimized integrity precheck not rejected')
 passcheck('optimized_interpreter','actual debug precheck raises under optimized compilation before assertions can be bypassed')
 result=json.loads(a.candidate_result.read_text());original=json.loads((snapshot/'public/docs/benchmarks/kfs-development-agent-v1/check-results.json').read_text());require(result['result']=='pass' and result['original_review_result_exact'] is True,'authoritative result');require(result['review_result']==original,'full exact original result');require(len(original['independent_checks'])==8 and len(original['saved_auditors'])==8,'8+8');require(result['new_material_calls']==result['new_builds']==result['new_fits']==0,'no campaigns');require(sha(snapshot/'public/docs/benchmarks/kfs-development-agent-v1/check-results.json')==two['expected_results_sha256'],'original result SHA');passcheck('unchanged_review_outcome',{'groups':8,'saved_auditors':8,'mapped_files_read':result['mapped_files_read'],'exact_negative_reasons':True,'scientific_decision_unchanged':True})
 output={'review':'REVIEW-kfs-relocated-audit-v1','candidate_sha256':sha(packet/'replay.py'),'candidate_result_sha256':sha(a.candidate_result),'checks':checks,'new_material_calls':0,'new_builds':0,'new_fits':0,'harness_not_security_sandbox':True};a.output.write_text(json.dumps(output,indent=2)+'\n');print('PASS',len(checks),'nonexecuting review groups')
if __name__=='__main__':main()
