"""Read-only cleanup audit for owned temporary roots; never deletes or executes models."""
from pathlib import Path
import collections,hashlib,json,os,re,stat,subprocess,time
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');WORK=Path('/private/tmp/atlas-interface2016-delivery-v1');OUT=Path(__file__).resolve().parent
NAMES=['release','source','em-cache','native','wasm']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.time();inode=collections.defaultdict(list);rows={};largest={}
for name in NAMES:
 base=WORK/name;counts=collections.Counter();top=collections.Counter();large=[]
 for current,dirs,files in os.walk(base,followlinks=False):
  dirs[:]=[n for n in dirs if not (Path(current)/n).is_symlink()]
  counts['directories']+=1
  for filename in files:
   p=Path(current)/filename;s=p.lstat();relative=p.relative_to(base).as_posix()
   if stat.S_ISLNK(s.st_mode):counts['symlinks']+=1;continue
   if not stat.S_ISREG(s.st_mode):counts['other_nodes']+=1;continue
   counts['files']+=1;counts['logical_bytes']+=s.st_size;counts['allocated_bytes_counting_links']+=s.st_blocks*512
   if s.st_nlink>1:counts['hardlinked_file_names']+=1
   key=(s.st_dev,s.st_ino);inode[key].append((name,relative,s.st_size,s.st_blocks*512,s.st_nlink))
   top[relative.split('/')[0]]+=s.st_size;large.append((s.st_size,relative,s.st_nlink))
 rows[name]=dict(counts);rows[name]['top_level_logical_bytes']=dict(top.most_common());largest[name]=[{'bytes':n,'path':p,'nlink':links} for n,p,links in sorted(large,reverse=True)[:12]]
for name in NAMES:
 unique=[values for values in inode.values() if any(v[0]==name for v in values)]
 rows[name]['unique_inode_allocated_bytes']=sum(v[0][3] for v in unique)
 rows[name]['conservative_reclaimable_allocated_bytes_if_only_this_root_unlinked']=sum(v[0][3] for v in unique if sum(x[0]==name for x in v)==v[0][4])
 rows[name]['allocated_bytes_with_other_hardlinks']=rows[name]['unique_inode_allocated_bytes']-rows[name]['conservative_reclaimable_allocated_bytes_if_only_this_root_unlinked']
# Content hashes only for the six small qualified artifacts and their durable copies.
retention=json.loads((ROOT/'docs/ingestion/hypoplastic-interface-2016/execution-v1/artifact-retention.json').read_text());durable=Path(retention['retention']);retained=[]
for original,digest in retention['originals'].items():
 source=Path(original);relative=source.relative_to(WORK);copy=durable/relative
 retained.append({'temporary':original,'durable':str(copy),'expected_sha256':digest,'temporary_sha256':sha(source),'durable_sha256':sha(copy),'exact':sha(source)==digest==sha(copy),'durable_bytes':copy.stat().st_size})
assert all(r['exact'] for r in retained)
freeze=json.loads((ROOT/'docs/ingestion/hypoplastic-interface-2016/execution-v1/source-freeze-v2.json').read_text())
source_checks=[{'path':p,'sha256':digest,'snapshot_exact':sha(WORK/'source'/p)==digest} for p,digest in freeze['source_closure'].items()]
assert all(r['snapshot_exact'] for r in source_checks)
commit=subprocess.check_output(['git','rev-parse','e6f734d'],cwd=ROOT,text=True).strip()
commit_source=[]
for row in source_checks:
 p=subprocess.run(['git','show',commit+':'+row['path']],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 commit_source.append({'path':row['path'],'expected_sha256':row['sha256'],'commit_exact':p.returncode==0 and hashlib.sha256(p.stdout).hexdigest()==row['sha256']})
# Report references only within the owned evidence packet; no full-repository content sweep.
references=collections.defaultdict(list)
for p in (ROOT/'docs/ingestion/hypoplastic-interface-2016').rglob('*'):
 if not p.is_file() or p.is_symlink() or 'cleanup-v1' in p.parts or p.suffix not in {'.json','.md','.py','.mjs','.log','.txt'}:continue
 try:text=p.read_text()
 except (UnicodeError,OSError):continue
 for name in NAMES:
  if re.search(re.escape(str(WORK/name))+r'''(?=$|[/\"'\s),;])''', text):references[name].append(p.relative_to(ROOT).as_posix())
try:
 ps=subprocess.run(['ps','-axo','pid,ppid,command'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=False)
 processes={'available':ps.returncode==0,'matching_commands':[line for line in ps.stdout.splitlines() if str(WORK) in line and 'ps -axo' not in line] if ps.returncode==0 else [],'error':ps.stderr.strip() if ps.returncode else None,'limitation':'One-time process command-line snapshot does not prove absence of open files, workers, cwd users or later consumers.'}
except OSError as e:processes={'available':False,'error':str(e)}
report={'audit_time_epoch':time.time(),'seconds':time.time()-start,'owned_work_root':str(WORK),'roots':rows,'largest_files':largest,'qualified_artifact_retention':retained,'source_snapshot_checks':source_checks,'source_commit':commit,'source_commit_closure_checks':commit_source,'all_source_snapshot_inputs_in_own_commit':all(r['commit_exact'] for r in commit_source),'evidence_path_references':dict(references),'process_snapshot':processes,'never_touch':['release-v2','site-v1',str(durable),'.local/private-sources','other-task assets'],'mutations_or_deletions_or_stops':False,'compiled_material_browser_calls':0}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'roots':rows,'durable_artifacts_exact':len(retained),'source_files':len(source_checks),'all_source_inputs_in_own_commit':report['all_source_snapshot_inputs_in_own_commit'],'process_snapshot':processes},indent=2))
