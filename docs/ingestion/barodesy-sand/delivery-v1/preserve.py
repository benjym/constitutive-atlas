"""Coordinator exact-byte preservation before changing scoped integration files.

Find only literal receipt pairs accepted by checked_receipt. Never alter the
original receipt JSON or its expected hash. Canonical copies are additive.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]

def sha(b):return hashlib.sha256(b).hexdigest()
def has(node,name,pin):
    if isinstance(node,dict):
        return node.get(name)==pin or (node.get('path')==name and any(node.get(k)==pin for k in ['sha256','hash'])) or any(has(v,name,pin) for v in node.values())
    return isinstance(node,list) and any(has(v,name,pin) for v in node)

def preserve(names,report_name='preservation.json'):
    documents={}
    for base in ['docs','catalogue','tests','benchmarks']:
        for p in (ROOT/base).rglob('*.json'):
            rel=p.relative_to(ROOT).as_posix()
            if '/source-snapshots/' in rel or '/barodesy-sand/delivery-v1/' in rel:continue
            try:documents[rel]=(p.read_bytes(),json.loads(p.read_bytes()))
            except (ValueError,UnicodeError):continue
    queue=[(n,(ROOT/n).read_bytes()) for n in names];seen=set();changes={};bindings=[]
    while queue:
        name,raw=queue.pop(0);pin=sha(raw)
        if (name,pin) in seen:continue
        seen.add((name,pin))
        archive='catalogue/source-snapshots/'+pin+'/'+name
        target=ROOT/archive;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==raw
        else:target.write_bytes(raw)
        for doc,(blob,node) in documents.items():
            if not has(node,name,pin):continue
            side=str(Path(doc).parent/'source-archive-map.json')
            if side not in changes:
                file=ROOT/side
                if file.exists():
                    original=file.read_bytes();changes[side]=json.loads(original);queue.append((side,original))
                else:changes[side]={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
            mapping=changes[side]
            existing=mapping['documents'].get(doc)
            assert existing is None or existing==sha(blob),(doc,'document changed')
            mapping['documents'][doc]=sha(blob)
            entry={'original_path':name,'sha256':pin,'archived_path':archive}
            matches=[v for v in mapping['entries'] if v['original_path']==name and v['sha256']==pin]
            assert not matches or matches==[entry]
            if not matches:mapping['entries'].append(entry)
            bindings.append({'document':doc,'original_path':name,'sha256':pin,'map':side})
    for n,m in changes.items():(ROOT/n).write_text(json.dumps(m,indent=2)+'\n')
    # Verify all old bindings now, before the target mutations.
    sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
    for b in bindings:checked_receipt(ROOT,b['document'],b['original_path'],b['sha256'])
    report={'targets':names,'archived_paths':[{'path':n,'sha256':h} for n,h in sorted(seen)],'changed_maps':sorted(changes),'old_bindings_verified':bindings}
    (Path(__file__).parent/report_name).write_text(json.dumps(report,indent=2)+'\n')
    print(len(bindings),'old bindings preserved in',len(changes),'maps')

if __name__=='__main__':preserve(sys.argv[1:])
