"""Close two remote-overlay predecessor-map pins without rewriting receipts."""
import hashlib,io,json,tarfile,gzip
from pathlib import Path
C=Path(__file__).resolve().parent;B=C.parent;R=B.parents[4];D=Path('docs/ingestion/kelvin-voigt-comsol63');sha=lambda x:hashlib.sha256(x).hexdigest();payload={};changes={}
def archive(path,data):
 h=sha(data);name='catalogue/source-snapshots/'+h+'/'+path;payload[name]=data;return {'original_path':path,'sha256':h,'archived_path':name}
def mapping(doc):
 name=str(Path(doc).parent/'source-archive-map.json')
 if name not in changes:
  target=R/name;changes[name]=json.loads(target.read_text())if target.exists()else{'version':'immutable-source-archive-map-0.1','documents':{str(f.relative_to(R)):sha(f.read_bytes())for f in target.parent.glob('*.json')if f.name!='source-archive-map.json'},'entries':[]}
 return changes[name]
def bind(doc,entry):
 m=mapping(doc);m['documents'][doc]=sha((R/doc).read_bytes())
 if entry not in m['entries']:m['entries'].append(entry)
old_receipt=str(D/'integration-v1/archive-installation.json');n=json.loads((R/old_receipt).read_text());wanted={p:h for p,h in n['files'].items()if p in ['docs/ingestion/duncan-chang-1970/release-v1/independent-review/source-archive-map.json','docs/ingestion/duncan-chang-1970/release-v2/staging-v3/source-archive-map.json']}
with tarfile.open(R/D/'release-bindings-v1/packaging-v2/audit-v1.tar.gz','r:gz')as t:
 for member in t.getmembers():
  if member.isfile():
   data=t.extractfile(member).read();h=sha(data)
   for path,expected in wanted.items():
    if h==expected:bind(old_receipt,archive(path,data))
assert len(payload)==2
map1=str(D/'integration-v1/source-archive-map.json');prior1=(R/map1).read_bytes();entry1=archive(map1,prior1)
bind(str(D/'integration-v2/installation.json'),entry1)
# The first installation receipt remains exact and replays its two updated maps.
core=str((B/'installation.json').relative_to(R));bind(core,entry1)
map2=str(D/'integration-v2/source-archive-map.json');bind(core,archive(map2,(R/map2).read_bytes()))
# Freeze all additive payload before installation.
for path,m in changes.items():payload['maps/'+path]=(json.dumps(m,indent=2)+'\n').encode()
with(C/'closure-payload.tar.gz').open('wb')as f:
 with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as gz:
  with tarfile.open(fileobj=gz,mode='w')as t:
   for name,data in sorted(payload.items()):
    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
(C/'payload-members.json').write_text(json.dumps({p:sha(v)for p,v in sorted(payload.items())},indent=2)+'\n')
prior={path:sha((R/path).read_bytes())if(R/path).exists()else None for path in changes}
for name,data in payload.items():
 if name.startswith('maps/'):continue
 target=R/name;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==data
 else:target.write_bytes(data)
for path in changes:
 target=R/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload['maps/'+path])
import sys;sys.path.insert(0,str(R));from atlas.evidence import checked_receipt,verify_manifest_files
verify_manifest_files(R,old_receipt);verify_manifest_files(R,str(D/'integration-v2/installation.json'));verify_manifest_files(R,core)
receipt={'identity':'kelvin-origin-v4-v5-binding-final-installation-v2','supersedes_as_final_handoff':core,'retained_core_receipt_sha256':sha((R/core).read_bytes()),'reason':'Full integration-v1 replay found two earlier installed map predecessors replaced by origin overlay; preserve both and close subsequent map receipt edges','files':{p:sha((R/p).read_bytes())for p in changes}|{p:sha(v)for p,v in payload.items()if not p.startswith('maps/')},'preinstallation_map_hashes':prior,'payload_sha256':sha((C/'closure-payload.tar.gz').read_bytes()),'passed':True}
(C/'installation.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Final closure installed; all old and core installation manifests replay')
