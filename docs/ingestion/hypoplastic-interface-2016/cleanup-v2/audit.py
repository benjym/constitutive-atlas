"""Read-only owned-output inventory; writes only this new packet. No cleanup."""
from pathlib import Path
import os,stat,hashlib,json,time,collections
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');PACKET=ROOT/'docs/ingestion/hypoplastic-interface-2016';OUT=Path(__file__).resolve().parent;WORK=Path('/private/tmp/atlas-interface2016-delivery-v1')
assert OUT==PACKET/'cleanup-v2'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
rows=[];summaries=[]
for label in ['site-v1','source-guard-checks-v1']:
 base=WORK/label;items=[];inodes={};dirs=0
 for parent,ds,fs in os.walk(base,followlinks=False):
  for n in sorted(ds+fs):
   p=Path(parent)/n;s=p.lstat();rel=p.relative_to(WORK).as_posix();row={'path':rel,'mode':stat.S_IMODE(s.st_mode),'mtime_ns':s.st_mtime_ns}
   if stat.S_ISLNK(s.st_mode):row.update(kind='symlink',target=os.readlink(p))
   elif stat.S_ISDIR(s.st_mode):dirs+=1;row.update(kind='directory')
   elif stat.S_ISREG(s.st_mode):
    row.update(kind='file',size=s.st_size,sha256=sha(p),allocated_bytes=s.st_blocks*512,device=s.st_dev,inode=s.st_ino,links=s.st_nlink);inodes[(s.st_dev,s.st_ino)]=s.st_blocks*512
   else:raise AssertionError(('Unexpected special file',p))
   items.append(row)
 files=[r for r in items if r['kind']=='file'];total=sum(r['size'] for r in files)
 summaries.append({'root':str(base),'regular_files':len(files),'directories':dirs,'symlinks':sum(r['kind']=='symlink' for r in items),'logical_bytes':total,'allocated_bytes_unique_inodes':sum(inodes.values()),'largest_subtrees_logical':dict(collections.Counter({n:sum(r['size'] for r in files if r['path'].split('/')[1]==n) for n in {r['path'].split('/')[1] for r in files}}).most_common(8))})
 rows+=items
by_path={r['path']:r for r in rows};checks=[]
for receipt,key,prefix in [('package-v2/interface-source-guard.json','files','source-guard-checks-v1/interface2016/'),('package-v2/remaining-source-guards.json','output_pins','source-guard-checks-v1/')]:
 obj=json.loads((PACKET/receipt).read_text())
 for n,h in obj[key].items():assert by_path[prefix+n]['sha256']==h;checks.append({'receipt':receipt,'path':prefix+n,'sha256':h})
references=[]
for p in sorted(PACKET.rglob('*')):
 if not p.is_file() or 'cleanup-v2' in p.parts or p.suffix not in ['.json','.py','.md','.log']:continue
 try:txt=p.read_text()
 except (OSError,UnicodeError):continue
 matched=[n for n in ['site-v1','source-guard-checks-v1','site-v2'] if str(WORK/n) in txt]
 if matched:references.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'mentioned_roots':matched})
run=json.loads((PACKET/'package-v1/run.json').read_text());logs={}
for n,h in run['logs'].items():assert sha(PACKET/'package-v1'/n)==h;logs[n]=h
preflight=json.loads((PACKET/'package-v2/commit-source-preflight.json').read_text());removal=json.loads((PACKET/'cleanup-v1/removal-receipt.json').read_text())
unique={r['sha256']:r['size'] for r in rows if r['kind']=='file'}
report={'status':'source-only audit; no cleanup/archive performed','summaries':summaries,'combined_unique_file_payload_bytes':sum(unique.values()),'combined_unique_sha256_count':len(unique),'guard_pins_checked':len(checks),'checks':checks,'evidence_references':references,'failed_package':{'status':run['status'],'exit_code':run['exit_code'],'seconds':run['end']-run['start'],'source_revision':run['source_revision'],'logs_verified':logs,'browser_qualified':False,'failure':'missing immutable E5 review document registration in common source archive map; exact failure retained'},'source_preflight':preflight,'prior_completed_cleanup':removal,'execution_status':'MD preflight held per coordinator; package-v2 not launched by this audit; no slot inferred','calls':{'deletions':0,'process_stops':0,'git_mutations':0,'builds':0,'compiled_material':0,'browser':0},'limitations':['No process/open-file check performed; this audit is not absence-of-consumer proof.','Allocation is stat block accounting, not guaranteed APFS free-space recovery.','site-v2 not inspected or modified.','No other-task resource tree read or copied.']}
(OUT/'recovery-inventory.json').write_text(json.dumps({'version':'owned-output-recovery-inventory-1','root':str(WORK),'entries':rows},indent=2)+'\n');(OUT/'audit-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['summaries','combined_unique_file_payload_bytes','combined_unique_sha256_count','guard_pins_checked']},indent=2))
