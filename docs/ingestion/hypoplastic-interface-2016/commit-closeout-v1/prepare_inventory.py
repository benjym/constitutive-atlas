"""Read-only source inventory against own base commit; writes only this new prep packet."""
from pathlib import Path
import argparse,subprocess,hashlib,json,stat
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');PACKET=ROOT/'docs/ingestion/hypoplastic-interface-2016';OUT=Path(__file__).resolve().parent;BASE='dcc645785faa3c83d791fdad92e7f3a20cab9721'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--revision',default='');p.add_argument('--final-ledgers',action='store_true');a=p.parse_args();assert not a.revision or a.revision.replace('-','').isalnum();suffix='-'+a.revision if a.revision else ''
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
head=git('rev-parse','HEAD').decode().strip();index=Path(git('rev-parse','--git-path','index').decode().strip());index=ROOT/index if not index.is_absolute() else index;index_before=sha(index)
archives=[ROOT/'catalogue/source-snapshots'/h/'docs/ingestion/hypoplastic-interface-2016'/n for n,h in [('DELIVERY.md','df2e994393a7432e51eac291a22342499ee8d68b6379b8ab62678fbc0bea4e43'),('CHECKLIST.md','2f1c25d91362a61ddcdcf0e2696303952ef09b723ba77d2f78cded9cb439574e')]]
raw=git('ls-tree','-r','-z',BASE,'--',str(PACKET.relative_to(ROOT)),*[str(q.relative_to(ROOT)) for q in archives]);base={}
for item in raw.split(b'\0'):
 if item:
  meta,name=item.split(b'\t');mode,kind,oid=meta.decode().split();assert kind=='blob';base[name.decode()]={'mode':mode,'git_blob':oid}
rows=[];excluded=[];pending=[]
for q in sorted(list(PACKET.rglob('*'))+archives):
 if not q.is_file() and not q.is_symlink():continue
 rel=q.relative_to(ROOT).as_posix();parts=q.relative_to(PACKET).parts if q.is_relative_to(PACKET) else ('canonical-old-ledger-archive',)
 if parts[0] in ['publication-composition-v1','commit-closeout-v1'] or '__pycache__' in parts or any(n.startswith('.') for n in parts) or q.suffix in ['.pyc','.pdf','.dll','.dylib','.exe']:
  excluded.append({'path':rel,'reason':'working publication composition/control metadata or private/cache/binary disallowed'});continue
 assert not q.is_symlink(),('Symlink not admitted',rel)
 data=q.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();mode='100755' if q.stat().st_mode&stat.S_IXUSR else '100644';prior=base.get(rel);status='added' if prior is None else ('unchanged' if prior=={'mode':mode,'git_blob':blob} else 'modified')
 row={'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':blob,'mode':mode,'delta':status,'base':prior,'public_classification':'project-authored evidence/code, public source citation/receipt, numerical output or public-atlas screenshot; no raw private source/binary'}
 if q.parent==PACKET and q.name in ['DELIVERY.md','CHECKLIST.md'] and not a.final_ledgers:
  row['final_hash_status']='pending coordinator confirmation; observed live hash only';pending.append(rel)
 rows.append(row)
by={r['path']:r for r in rows};closure=[]
# New reviewed ledger manifests use exact paths relative to their packet. Preserve every pinned simulation/proposal byte.
for directory in ['ledger-update-v1','ledger-update-v2','ledger-update-v3','cleanup-v2']:
 m=PACKET/directory/'manifest.json';obj=json.loads(m.read_text())
 for n,h in obj['files'].items():
  target=(m.parent/n).relative_to(ROOT).as_posix();assert target in by and by[target]['sha256']==h,('Manifest closure missing/drift',target);closure.append({'manifest':m.relative_to(ROOT).as_posix(),'path':target,'sha256':h})
# Retain the reviewed44-file real-browser closure in full.
m=PACKET/'browser-v1/manifest.json';obj=json.loads(m.read_text())
for e in obj['entries']:
 target=(m.parent/e['path']).relative_to(ROOT).as_posix();assert target in by and by[target]['sha256']==e['sha256'];closure.append({'manifest':m.relative_to(ROOT).as_posix(),'path':target,'sha256':e['sha256']})
delta=[r for r in rows if r['delta']!='unchanged'];missing=[n for n in base if n not in by and not any(n==e['path'] for e in excluded)];assert not missing,('Unexpected deletion from own base',missing)
assert git('rev-parse','HEAD').decode().strip()==head and sha(index)==index_before
report={'status':'read-only public closeout inventory; not a commit','base_commit':BASE,'root_head_preserved':head,'root_index_sha256_preserved':index_before,'rows':rows,'summary':{'public_packet_files':len(rows),'logical_bytes':sum(r['bytes'] for r in rows),'added':sum(r['delta']=='added' for r in rows),'modified':sum(r['delta']=='modified' for r in rows),'unchanged':sum(r['delta']=='unchanged' for r in rows),'reviewed_manifest_entries_verified':len(closure)},'pending_final_ledger_hashes':pending,'final_ledgers_coordinator_confirmed':a.final_ledgers,'outside_packet_exact_archive_exceptions':[q.relative_to(ROOT).as_posix() for q in archives],'excluded':excluded,'deletions':[],'reviewed_manifest_closure':closure,'calls':{'git_mutations':0,'build_material_browser_remote':0},'notes':['Observed live ledger hashes require coordinator confirmation; --final-ledgers records that confirmation after reviewed installation.','Working publication composition is excluded until frozen separate handoff. Root/shared/private/download files are outside this whitelist.','This prep directory is control metadata excluded to avoid recursive self-hashes; its separate manifest preserves exact author deliverables for later explicit addition.']}
outputs={f'inventory{suffix}.json':(json.dumps(report,indent=2)+'\n').encode(),f'paths{suffix}.txt':(''.join(r['path']+'\n' for r in rows)).encode(),f'paths{suffix}.nul':b''.join(r['path'].encode()+b'\0' for r in rows),f'delta-paths{suffix}.txt':(''.join(r['path']+'\n' for r in delta)).encode(),f'delta-paths{suffix}.nul':b''.join(r['path'].encode()+b'\0' for r in delta)}
for name in outputs:assert not (OUT/name).exists(),('Retain old inventory; use --revision',name)
for name,data in outputs.items():(OUT/name).write_bytes(data)
print(json.dumps(report['summary']|{'pending_final_ledgers':pending,'excluded_files':len(excluded),'root_head_index_unchanged':True},indent=2))
