"""Replay both actual old/new assessor bytes from public source capsules, no git."""
import hashlib,json,pathlib
import capsule
HERE=pathlib.Path(__file__).resolve().parent

def run():
 records=[]
 for label in ('preliminary','fixed'):
  path=HERE/(label+'-capsule.json');c=json.loads(path.read_text());r=capsule.replay(c)
  assert r['returncode']==0 and r['stderr']=='',r
  result=json.loads(r['stdout']);assert result['input_sha256']==c['files']['tools/research_rate_observations.py']['sha256']
  flags=[row['vulnerable'] for row in result['witnesses']]
  assert len(flags)==5 and (all(flags) if label=='preliminary' else not any(flags)),flags
  records.append({'id':label,'capsule_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_assessor_sha256':result['input_sha256'],'source_files':len(c['files']),'returncode':r['returncode'],'witnesses':result['witnesses'],'retained_vulnerability_count':sum(flags),'stdout_sha256':r['stdout_sha256'],'stderr_sha256':r['stderr_sha256']})
 return {'version':'source-evolution-actual-audit-replay-0.1','records':records,'compiled_execution':False,'claims':{'scientific_validation':False,'compiled_rebuild':False,'git_required':False},'limitations':['Python interpreter/stdlib remain external; no exact environment or cross-version bit reproduction claimed.','Explicit import/data closure covers these actual five synthetic witness groups, not every future study or code branch.']}
if __name__=='__main__':print(json.dumps(run(),indent=2,allow_nan=False))
