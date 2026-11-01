"""Read-only pre/post receipt. Does not execute the planned command or any artifact."""
if not __debug__: raise RuntimeError("Unoptimized Python is required")
import argparse,hashlib,json,os,shutil,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def verify(env):
 if not __debug__: raise RuntimeError("Unoptimized Python is required")
 p=read(D/'plan.json');t=read(D/'toolchain.json');s=Path(p['source_directory']);f=read(Path(p['source_freeze']))['files']
 assert {str(x.relative_to(s)):sha(x)for x in s.rglob('*')if x.is_file()}==f,'source set/bytes changed'
 assert env['PATH']==t['PATH'],'PATH changed'
 for k,v in t['environment'].items():assert env.get(k)==v,k
 for k,v in t['ambient_exact'].items():assert env.get(k)==v,'ambient override '+k
 for n,v in t['commands'].items():
  found=shutil.which(n,path=env['PATH']);assert found==(v['path']if v else None),'tool resolution '+n
  if found:assert str(Path(found).resolve())==v['realpath'],'tool target '+n
 for n,v in t['files'].items():assert str(Path(n).resolve())==v['realpath'] and sha(Path(n))==v['sha256'],'tool bytes '+n
 for n,h in read(D/'input-pins.json').items():assert sha(Path(n))==h,n
 return dict(source_files=len(f),source_freeze_sha256=sha(Path(p['source_freeze'])),toolchain_sha256=sha(D/'toolchain.json'),tool_files=len(t['files']),plan_sha256=sha(D/'plan.json'))
def validate_pre(q, expected):
 if not __debug__: raise RuntimeError("Unoptimized Python is required")
 if q.get('passed') is not True:raise ValueError('pre passed must be literal true')
 for k,v in expected.items():
  if q.get(k)!=v:raise ValueError('pre identity mismatch '+k)
def finish_post(result, q, expected, status, stdout, stderr, pre_hash):
 if not __debug__: raise RuntimeError("Unoptimized Python is required")
 # Retain process outcome before any precondition or zero-exit rejection.
 result.update(exit_status=status,stdout=stdout,stderr=stderr,pre_receipt_sha256=pre_hash)
 validate_pre(q,expected)
 if type(status)is not int or status!=0:raise ValueError('stage exit status must be zero')
 result['passed']=True
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['pre','post'],required=True);ap.add_argument('--profile',required=True);ap.add_argument('--stage',required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--exit-status',type=int);ap.add_argument('--stdout-file',type=Path);ap.add_argument('--stderr-file',type=Path);a=ap.parse_args()
 p=read(D/'plan.json');row=next(x for x in p['profiles']if x['profile']==a.profile)
 if a.stage=='post-independent-build-review':st=next(x for x in p['post_independent_build_review_only']if x['profile']==a.profile)
 else:st=next(x for x in row['steps']if x['stage']==a.stage)
 expected=Path(row['output'])/'stage-receipts'/f'{a.stage}.{a.phase}.json'
 if a.output!=expected or expected.exists():raise ValueError('fresh exact receipt path required')
 result=dict(identity='current-profile-stage-receipt-v3',phase=a.phase,profile=a.profile,stage=a.stage,command=st,packet_manifest_sha256=sha(D/'manifest.json'),passed=False)
 try:
  if a.phase=='post':
   result['exit_status']=a.exit_status
   for key,path in [('stdout',a.stdout_file),('stderr',a.stderr_file)]:
    if path is None:raise ValueError('missing '+key+' file')
    result[key]=dict(path=str(path),sha256=sha(path))
  manifest=read(D/'manifest.json')
  for name,h in manifest['files'].items():assert sha(D/name)==h,'packet bytes '+name
  for k,v in st['env'].items():assert os.environ.get(k)==v,'stage env '+k
  assert Path.cwd()==Path(st['cwd']),'stage cwd'
  result.update(verify(os.environ))
  if a.phase=='post':
   pre=expected.with_name(a.stage+'.pre.json');q=read(pre)
   wanted={k:v for k,v in result.items()if k not in ['passed','exit_status','stdout','stderr']};wanted['phase']='pre'
   finish_post(result,q,wanted,a.exit_status,result['stdout'],result['stderr'],sha(pre))
  else:result['passed']=True
 except Exception as exc:result['error']=str(exc)
 expected.parent.mkdir(parents=True,exist_ok=True)
 with expected.open('x')as stream:stream.write(json.dumps(result,indent=2)+'\n')
 if result['passed']is not True:sys.exit(1)
if __name__=='__main__':main()
