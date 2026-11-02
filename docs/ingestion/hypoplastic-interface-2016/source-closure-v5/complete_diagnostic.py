"""Complete first bounded diagnostic via streaming committed JSON metadata only."""
import json,subprocess,io,collections
from pathlib import Path
from stream_references import references
HERE=Path(__file__).resolve().parent;ROOT=Path('/Users/bmar5496/code/constitutive-atlas');WORK=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v3')
d=json.loads((HERE/'diagnostic.json').read_text());base=json.loads((HERE/'selection-paths.json').read_text());rows={r['path']:r for r in base['entries']};rev=d['revision']
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
tracked={}
for x in git('ls-tree','-r','-l','-z',rev).split(b'\0'):
 if x:
  head,name=x.split(b'\t');mode,kind,oid,size=head.decode().split();assert kind=='blob';tracked[name.decode()]={'mode':mode,'git_blob':oid,'bytes':int(size)}
queue=[r['path'] for r in d['large_json_not_read']];parsed=set(rows)-set(queue);cache={};count=0
while queue:
 n=queue.pop(0)
 if n in parsed:continue
 parsed.add(n);oid=tracked[n]['git_blob']
 if oid not in cache:
  p=subprocess.Popen(['git','cat-file','blob',oid],cwd=ROOT,stdout=subprocess.PIPE)
  try:cache[oid]=references(io.TextIOWrapper(p.stdout,encoding='utf-8'))
  finally:p.stdout.close();assert p.wait()==0
  count+=1
  if count%10==0:print('JSON metadata blobs parsed',count,flush=True)
 for target in cache[oid]:
  if target in tracked and target not in rows:
   rows[target]={'path':target,**tracked[target],'actual_stat_bytes':(WORK/target).stat().st_size,'reasons':[{'kind':'recursive-json-hash-reference','document':n}]}
   if target.endswith('.json'):queue.append(target)
entries=sorted(rows.values(),key=lambda r:r['path']);total=sum(r['bytes'] for r in entries);actual=sum(r['actual_stat_bytes'] for r in entries);groups=collections.Counter();extensions=collections.Counter()
for r in entries:groups['/'.join(r['path'].split('/')[:3])]+=r['bytes'];extensions[Path(r['path']).suffix]+=r['bytes']
report={'status':'complete committed-metadata selection; no actual source hash/freeze or package','revision':rev,'parents':d['parents'],'source_files':len(entries),'source_bytes':total,'actual_stat_bytes_total':actual,'all_sizes_equal':all(r['bytes']==r['actual_stat_bytes'] for r in entries),'expected_v4_failure_total':2904465794,'exact_failed_total_reproduced':actual==2904465794,'selection_complete':True,'additional_paths_beyond_bounded_study':len(rows)-len(base['entries']),'large_and_new_json_blobs_streamed':len(cache),'stream_block_characters':1048576,'groups_top30':groups.most_common(30),'extensions':extensions.most_common(),'largest_files':sorted(entries,key=lambda r:r['bytes'],reverse=True)[:30]}
for name,obj in [('selection-paths-complete.json',{'revision':rev,'parents':d['parents'],'entries':entries}),('diagnostic-complete.json',report)]:
 with (HERE/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['groups_top30','extensions','largest_files']},indent=2))
