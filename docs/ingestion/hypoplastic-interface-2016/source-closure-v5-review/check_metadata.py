"""Independent Git/JSON/lstat-only review. Never read actual source-file bytes."""
from pathlib import Path
import collections,hashlib,json,os,stat,subprocess
HERE=Path(__file__).resolve().parent;P=HERE.parent/'source-closure-v5';REPO=HERE.parents[3]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 manifest=json.loads((P/'MANIFEST.json').read_text());assert sha(P/'MANIFEST.json')=='1e1e42c6ac7664f417835ac78f124108dd325fc8d21ff3bcd2b271892b662cc0'
 for n,h in manifest['files'].items():assert sha(P/n)==h,n
 policy=json.loads((P/'RESOURCE_POLICY.json').read_text());identity=json.loads((P/'full-tree-resource-identity.json').read_text());diagnostic=json.loads((P/'full-tree-diagnostic.json').read_text());paths=json.loads((P/'full-tree-paths.json').read_text())
 assert sha(P/'full-tree-resource-identity.json')==policy['metadata_identity_sha256']
 revision='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
 def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
 parents=git('rev-list','--parents','-n','1',revision).decode().split();tree=git('rev-parse',revision+'^{tree}').decode().strip()
 assert parents[0]==revision and parents[1:]==identity['parents']==policy['parents']
 assert tree==identity['tree']==policy['tree']=='2a68f30b0d56c481df548a79881e1029a9017a06'
 entries=[]
 for row in git('ls-tree','-r','-l','-z',revision).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t');mode,kind,oid,size=meta.decode().split();assert kind=='blob'
  entries.append({'path':name.decode(),'mode':mode,'git_blob':oid,'bytes':int(size)})
 assert entries==identity['entries']
 assert len(entries)==len({r['path'] for r in entries})==identity['files']==policy['exact_path_count']==40318
 total=sum(r['bytes'] for r in entries);assert total==identity['logical_bytes']==policy['exact_logical_bytes']==3605081558
 assert [{k:r[k] for k in ['path','mode','git_blob','bytes']} for r in paths['entries']]==entries
 assert diagnostic['projection_issues']==[]
 root=Path(diagnostic['root']);issues=[];ancestor_cache=set();links=[];aliases=collections.defaultdict(list)
 for r in entries:
  q=root/r['path']
  for parent in q.parents:
   if parent in ancestor_cache:break
   if parent==root.parent:break
   ancestor_cache.add(parent);assert stat.S_ISDIR(parent.lstat().st_mode) and not parent.is_symlink(),str(parent)
  st=q.lstat();actualmode='120000' if stat.S_ISLNK(st.st_mode) else '100755' if stat.S_ISREG(st.st_mode) and st.st_mode&stat.S_IXUSR else '100644' if stat.S_ISREG(st.st_mode) else 'other'
  if actualmode!=r['mode'] or st.st_size!=r['bytes']:issues.append({'path':r['path'],'actualmode':actualmode,'bytes':st.st_size})
  if actualmode=='120000':links.append({'path':r['path'],'payload':os.readlink(q),'bytes':st.st_size})
  aliases[r['path'].casefold()].append(r)
 assert not issues
 assert links==policy['known_symlink_policy']==diagnostic['symlinks_never_followed']
 actualaliases=[{'paths':[r['path'] for r in rs],'git_blob_identities':sorted({r['git_blob'] for r in rs}),'git_modes':sorted({r['mode'] for r in rs})} for rs in aliases.values() if len(rs)>1]
 assert actualaliases==policy['case_alias_policy'] and all(len(a['git_blob_identities'])==len(a['git_modes'])==1 for a in actualaliases)
 failure=json.loads((P/'v4-resource-failure.json').read_text());assert failure['selected_stat_total_bytes']==2904465794 and failure['unchanged_v4_guard_bytes']==786432000
 v4=P.parent/'package-v4';assert sha(v4/'manifest.json')=='59808fdc34ecfdbe257e7fac7ba0f701bf080770cafd0dbc6c081fba735e793e'
 report={'status':'passed-independent-metadata-resource-policy-check','manifest_sha256':sha(P/'MANIFEST.json'),'policy_sha256':sha(P/'RESOURCE_POLICY.json'),'metadata_identity_sha256':sha(P/'full-tree-resource-identity.json'),'all_14_manifest_members_match':True,'revision':revision,'tree':tree,'parents':parents[1:],'exact_git_path_mode_blob_size_equality':True,'paths':len(entries),'logical_bytes':total,'regular_file_bytes':total-12,'actual_lstat_issues':issues,'ancestor_symlinks_rejected':True,'symlinks_readlink_only':links,'case_aliases':actualaliases,'v4_guard_and_failure_preserved':True,'actual_source_bytes_read_or_hashed':0,'freeze_package_compiled_material_browser_remote_calls':0}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
