"""Independent cached exact-receipt resolution proof over saved predicate sets.

No artifact calls or production writes. Candidate/source bytes form a virtual
future root; caches change parsing/hash cost, not any receipt predicate.
"""
from pathlib import Path
import hashlib,json,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[6]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
A='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
P=ROOT/A/'shared-hook-install-v1/revision-v5'
PREV=P.parent/'revision-v3'
sha=lambda data:hashlib.sha256(data).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())

def safe(name):
    p=Path(name)
    assert not p.is_absolute() and '..' not in p.parts,name
    assert (ROOT/p).resolve().is_relative_to(ROOT),name
    return p.as_posix()

def pairs(node):
    found=set()
    valid=lambda v:isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)
    if isinstance(node,dict):
        for k,v in node.items():
            if valid(v):found.add((k,v))
            found.update(pairs(v))
        if isinstance(node.get('path'),str):
            for k in ['sha256','hash']:
                if valid(node.get(k)):found.add((node['path'],node[k]))
    elif isinstance(node,list):
        for v in node:found.update(pairs(v))
    return found

def main():
    plan=load(P/'PLAN.json');previous=load(PREV/'CHECK_RESULTS.json')
    overrides={};physical_pins={};cache={};parsed={};paircache={};mapcache={}
    def read_physical(path):
        path=Path(path);data=path.read_bytes()
        physical_pins[path.relative_to(ROOT).as_posix()]=sha(data)
        return data
    def candidate(row):
        path=P/row['candidate'];data=read_physical(path);assert sha(data)==row['new_sha256'];return path
    for row in plan['maps']:overrides[row['original_path']]=candidate(row)
    for row in plan['archives']:
        path=P/row['snapshot'];assert sha(read_physical(path))==row['old_sha256'];overrides[row['canonical_archive']]=path
    for row in plan['replacements']:
        path=ROOT/row['future_copy'];assert sha(read_physical(path))==row['new_sha256'];overrides[row['original_path']]=path
    def exists(name):return name in overrides or (ROOT/name).is_file()
    def read(name):
        name=safe(name)
        if name not in cache:cache[name]=read_physical(overrides.get(name,ROOT/name))
        return cache[name]
    def obj(name):
        if name not in parsed:parsed[name]=json.loads(read(name))
        return parsed[name]
    def resolve(doc,name,digest):
        safe(doc);safe(name)
        assert isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest)
        if doc not in paircache:paircache[doc]=pairs(obj(doc))
        assert (name,digest) in paircache[doc],(doc,name,'absent original pair')
        selected=name;side=str(Path(doc).parent/'source-archive-map.json')
        if exists(side):
            if side not in mapcache:
                mapping=obj(side);assert mapping['version']=='immutable-source-archive-map-0.1'
                entries=mapping.get('entries');assert isinstance(entries,list) and all(isinstance(e,dict) for e in entries)
                index={}
                for e in entries:index.setdefault((e.get('original_path'),e.get('sha256')),[]).append(e)
                mapcache[side]=(mapping,index)
            mapping,index=mapcache[side]
            assert mapping.get('documents',{}).get(doc)==sha(read(doc)),(doc,'document pin')
            matches=index.get((name,digest),[]);assert len(matches)<=1
            if matches:
                selected=f'catalogue/source-snapshots/{digest}/{name}'
                assert matches[0].get('archived_path')==selected
        assert sha(read(selected))==digest,(doc,name,selected,'selected bytes')
        return selected,side
    oldrows=[r for r in previous['checks'] if r['outcome']=='passed']
    oldkeys={(r['document'],r['original_path'],r['old_sha256']) for r in oldrows}
    saved=load(P/'CHECK_RESULTS.json')
    newkeys={(r['document'],r['original_path'],r['old_sha256']) for r in saved['checks']}
    allkeys=oldkeys|newkeys
    branches={};direct=[]
    for doc,name,digest in sorted(allkeys):
        selected,side=resolve(doc,name,digest)
        branches.setdefault((side,selected!=name),(doc,name,digest))
    # Direct unchanged API comparisons cover every sidecar/resolution branch,
    # plus every declared transitive closure obligation when separately listed.
    direct=list(branches.values())
    with tempfile.TemporaryDirectory(dir=HERE,prefix='api-proof-') as temp:
        overlay=Path(temp)
        for name,data in cache.items():
            path=overlay/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        for doc,name,digest in direct:
            expected,_=resolve(doc,name,digest)
            actual=checked_receipt(overlay,doc,name,digest)
            assert actual.relative_to(overlay).as_posix()==expected
    for name,digest in physical_pins.items():assert sha((ROOT/name).read_bytes())==digest,'Concurrent drift '+name
    result=dict(status='passed',scope='Exact cached receipt-resolution proof; no numerical/material execution',prior_passing_distinct=len(oldkeys),new_checked_distinct=len(newkeys),union_proved=len(allkeys),direct_unchanged_api_branch_checks=len(direct),selected_files_hashed=len(cache),source='Unchanged atlas.evidence.checked_receipt semantics: safe paths, original pair membership, exact document pin, unique canonical archive, selected byte hash',api_source_sha256=sha((ROOT/'atlas/evidence.py').read_bytes()))
    (HERE/'composition-results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'composition-pins.json').write_text(json.dumps(dict(files=physical_pins),indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
