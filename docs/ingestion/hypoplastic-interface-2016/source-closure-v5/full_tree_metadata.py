"""Read-only full Git-tree metadata and physical projection; no source-byte hashing."""
from pathlib import Path
import subprocess,json,stat,os,collections
HERE=Path(__file__).resolve().parent;REPO=Path('/Users/bmar5496/code/constitutive-atlas');ROOT=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v3');REV='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
entries=[];issues=[];symlinks=[];inodes=collections.defaultdict(list);groups=collections.Counter();ext=collections.Counter()
for line in git('ls-tree','-r','-l','-z',REV).split(b'\0'):
 if not line:continue
 head,name=line.split(b'\t');mode,kind,oid,size=head.decode().split();assert kind=='blob';n=name.decode();size=int(size);q=ROOT/n;r={'path':n,'mode':mode,'git_blob':oid,'bytes':size};groups['/'.join(n.split('/')[:3])]+=size;ext[q.suffix]+=size
 try:
  st=q.lstat();r['physical']={'kind':'symlink' if stat.S_ISLNK(st.st_mode) else 'file' if stat.S_ISREG(st.st_mode) else 'other','bytes':st.st_size,'permissions':stat.S_IMODE(st.st_mode)};inodes[(st.st_dev,st.st_ino)].append(n)
  actualmode='120000' if stat.S_ISLNK(st.st_mode) else '100755' if stat.S_ISREG(st.st_mode) and st.st_mode&stat.S_IXUSR else '100644' if stat.S_ISREG(st.st_mode) else 'other'
  if mode!=actualmode:issues.append({'path':n,'issue':'mode mismatch','expected':mode,'actual':actualmode})
  if mode=='120000':r['link_payload']=os.readlink(q);symlinks.append({'path':n,'payload':r['link_payload'],'bytes':size})
  if st.st_size!=size:issues.append({'path':n,'issue':'size mismatch','expected':size,'actual':st.st_size})
 except FileNotFoundError:r['physical']={'kind':'missing'};issues.append({'path':n,'issue':'missing'})
 entries.append(r)
parents=git('rev-list','--parents','-n','1',REV).decode().split()[1:];tree=git('rev-parse',REV+'^{tree}').decode().strip();casegroups=collections.defaultdict(list)
for r in entries:casegroups[r['path'].casefold()].append(r)
casealiases=[{'paths':[r['path'] for r in rs],'git_blob_identities':sorted({r['git_blob'] for r in rs}),'git_modes':sorted({r['mode'] for r in rs})} for rs in casegroups.values() if len(rs)>1]
report={'status':'metadata-only full tracked Git projection; not source freeze, no source-byte hashes','revision':REV,'tree':tree,'parents':parents,'root':str(ROOT),'tracked_files':len(entries),'logical_bytes':sum(r['bytes'] for r in entries),'projection_issues':issues,'symlinks_never_followed':symlinks,'case_aliases':casealiases,'physical_inode_alias_groups':[names for names in inodes.values() if len(names)>1],'groups_top30':groups.most_common(30),'extensions':ext.most_common(),'largest_files':sorted(entries,key=lambda r:r['bytes'],reverse=True)[:30]}
for name,obj in [('full-tree-paths.json',{'revision':REV,'tree':tree,'parents':parents,'entries':entries}),('full-tree-diagnostic.json',report)]:
 with (HERE/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ['revision','tree','tracked_files','logical_bytes','projection_issues','symlinks_never_followed','case_aliases']},indent=2))
