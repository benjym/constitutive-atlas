"""Read-only pre/post receipt. Does not execute the planned command or any artifact."""
import argparse,hashlib,json,os,shutil,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def verify(env):
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
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['pre','post'],required=True);ap.add_argument('--profile',required=True);ap.add_argument('--stage',required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--exit-status',type=int);ap.add_argument('--stdout-file',type=Path);ap.add_argument('--stderr-file',type=Path);a=ap.parse_args()
 manifest=read(D/'manifest.json')
 for name,h in manifest['files'].items():assert sha(D/name)==h,'packet bytes '+name
 p=read(D/'plan.json');row=next(x for x in p['profiles']if x['profile']==a.profile)
 if a.stage=='post-independent-build-review':st=next(x for x in p['post_independent_build_review_only']if x['profile']==a.profile)
 else:st=next(x for x in row['steps']if x['stage']==a.stage)
 expected=Path(row['output'])/'stage-receipts'/f'{a.stage}.{a.phase}.json';assert a.output==expected and not expected.exists(),'fresh exact receipt path required'
 for k,v in st['env'].items():assert os.environ.get(k)==v,'stage env '+k
 assert Path.cwd()==Path(st['cwd']),'stage cwd'
 result=dict(identity='current-profile-stage-receipt-v2',phase=a.phase,profile=a.profile,stage=a.stage,command=st,packet_manifest_sha256=sha(D/'manifest.json'),passed=False)
 try:
  result.update(verify(os.environ))
  if a.phase=='post':
   pre=expected.with_name(a.stage+'.pre.json');q=read(pre);assert q['passed'] and q['command']==st
   assert a.exit_status is not None and a.stdout_file and a.stderr_file
   result.update(pre_receipt_sha256=sha(pre),exit_status=a.exit_status,stdout=dict(path=str(a.stdout_file),sha256=sha(a.stdout_file)),stderr=dict(path=str(a.stderr_file),sha256=sha(a.stderr_file)))
  result['passed']=True
 except Exception as exc:result['error']=str(exc)
 expected.parent.mkdir(parents=True,exist_ok=True);expected.write_text(json.dumps(result,indent=2)+'\n')
 if not result['passed']:sys.exit(1)
if __name__=='__main__':main()
