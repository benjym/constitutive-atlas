"""Nonmutating source/map preservation proposal; never installs the F profile."""
from pathlib import Path
from collections import defaultdict, deque
import hashlib
import json
import shutil
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
SOURCE='cpp/profiles/implicit-path-v1/include/atlas/solver.hpp'
FUTURE='docs/ingestion/lade-duncan-1975/fused-linear-v1/proposed-native-source/include/atlas/solver.hpp'
OLD='098e1b926e3eb99545567111415f54d35c08f52e7afbaa796fa23a551fe4a6c0'
NEW='e2e517d9cb5a90383779d4d26eed66284b774d3646d1f74149541589f6ac1026'
VERSION='immutable-source-archive-map-0.1'
sha=lambda b:hashlib.sha256(b).hexdigest()
valid_hash=lambda x:isinstance(x,str) and len(x)==64 and all(c in '0123456789abcdef' for c in x)
def pairs(node):
    result=set()
    if isinstance(node,dict):
        for key,value in node.items():
            if valid_hash(value):result.add((key,value))
            result.update(pairs(value))
        if isinstance(node.get('path'),str):
            for key in ['sha256','hash']:
                if valid_hash(node.get(key)):result.add((node['path'],node[key]))
    elif isinstance(node,list):
        for value in node:result.update(pairs(value))
    return result

def canonical(original,digest):return 'catalogue/source-snapshots/'+digest+'/'+original

def main():
    source=(ROOT/SOURCE).read_bytes();future=(ROOT/FUTURE).read_bytes()
    assert sha(source)==OLD and sha(future)==NEW
    documents={};index=defaultdict(set);unreadable=[];archived_skipped=0
    own=HERE.parent.relative_to(ROOT).as_posix()+'/'
    for directory in ['docs','catalogue']:
        for path in sorted((ROOT/directory).rglob('*.json')):
            name=path.relative_to(ROOT).as_posix()
            if name.startswith(own):continue
            if name.startswith('catalogue/source-snapshots/'):
                archived_skipped+=1;continue
            data=path.read_bytes()
            try:value=json.loads(data)
            except (ValueError,UnicodeDecodeError) as error:
                unreadable.append(dict(document=name,error=str(error),bytes=len(data),old_document_sha256=sha(data),mentions_profile_pair=SOURCE.encode() in data and OLD.encode() in data));continue
            found=pairs(value);documents[name]=(data,value,found)
            for pair in found:index[pair].add(name)
    prior=json.loads((HERE.parent/'PLAN.json').read_bytes())
    recovery=json.loads((ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/legacy-prerequisite-recovery-v1/RECOVERY.json').read_bytes())
    seeds=[(SOURCE,OLD)]+[(r['original_path'],r['old_sha256']) for r in prior['archives']]+[(r['original_path'],r['old_sha256']) for r in recovery['records'] if r['changed']]
    queue=deque(seeds);visited=set();proposals={};original_maps={};archives={};obligations=[];issues=[]
    while queue:
        original,expected=queue.popleft()
        if (original,expected) in visited:continue
        visited.add((original,expected))
        data=(ROOT/original).read_bytes()
        if sha(data)!=expected:
            archived=ROOT/canonical(original,expected)
            if not archived.is_file():archived=HERE.parent/'snapshots'/canonical(original,expected)
            data=archived.read_bytes()
            if sha(data)!=expected:raise ValueError('Missing historical bytes: '+original)
        archive=canonical(original,expected)
        if (ROOT/archive).exists() and sha((ROOT/archive).read_bytes())!=expected:raise ValueError('Existing corrupt canonical snapshot: '+archive)
        archives[(original,expected)]=data
        for document in sorted(index[(original,expected)]):
            docbytes,value,found=documents[document];sidecar=(Path(document).parent/'source-archive-map.json').as_posix()
            obligations.append(dict(document=document,document_sha256=sha(docbytes),original_path=original,old_sha256=expected,sidecar=sidecar))
            if sidecar not in proposals:
                if (ROOT/sidecar).exists():
                    oldbytes=(ROOT/sidecar).read_bytes();mapping=json.loads(oldbytes);original_maps[sidecar]=oldbytes
                    if mapping.get('version')!=VERSION:raise ValueError('Unsupported existing map: '+sidecar)
                else:mapping={'version':VERSION,'documents':{},'entries':[]};original_maps[sidecar]=None
                proposals[sidecar]=mapping
            mapping=proposals[sidecar]
            pin=mapping.setdefault('documents',{}).get(document)
            if pin is not None and pin!=sha(docbytes):
                issues.append(dict(kind='preexisting_document_pin_mismatch',document=document,sidecar=sidecar,pinned=pin,current=sha(docbytes)))
                continue
            mapping['documents'][document]=sha(docbytes)
            entries=mapping.setdefault('entries',[]);matches=[e for e in entries if e.get('original_path')==original and e.get('sha256')==expected]
            if len(matches)>1:raise ValueError('Ambiguous existing map pair: '+sidecar)
            if matches:
                if matches[0].get('archived_path')!=archive:raise ValueError('Noncanonical existing map pair: '+sidecar)
            else:entries.append({'original_path':original,'sha256':expected,'archived_path':archive})
            oldbytes=original_maps[sidecar]
            if oldbytes is not None:
                candidate=(json.dumps(mapping,indent=2)+'\n').encode()
                if candidate!=oldbytes:queue.append((sidecar,sha(oldbytes)))
    # Freeze exact old/candidate maps and one canonical snapshot per queued pair.
    maprows=[]
    for name,mapping in sorted(proposals.items()):
        old=original_maps[name];candidate=(json.dumps(mapping,indent=2)+'\n').encode()
        if old==candidate:continue
        target=HERE/'candidates'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(candidate)
        if old is not None:
            saved=HERE/'prior-map-bytes'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(old)
        maprows.append(dict(original_path=name,old_sha256=sha(old) if old is not None else None,new_sha256=sha(candidate),candidate=target.relative_to(HERE).as_posix(),document_pins=[dict(original_document=doc,old_document_sha256=pin) for doc,pin in mapping['documents'].items()],entries=[dict(original_path=e['original_path'],old_sha256=e['sha256'],canonical_archive=e['archived_path']) for e in mapping['entries']]))
    ar=[]
    for (name,expected),data in sorted(archives.items()):
        original=canonical(name,expected);target=HERE/'snapshots'/original;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        ar.append(dict(original_path=name,old_sha256=expected,canonical_archive=original,snapshot=target.relative_to(HERE).as_posix(),already_present=(ROOT/original).exists()))
    for document in sorted({row['document'] for row in obligations}):
        saved=HERE/'receipt-bytes'/document;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(documents[document][0])
    baseline=[];simulated=[];existing_bindings=[]
    for row in obligations:
        try:checked_receipt(ROOT,row['document'],row['original_path'],row['old_sha256']);outcome='passed'
        except Exception as error:outcome=str(error)
        baseline.append(dict(**row,outcome=outcome))
    # Materialize only metadata/source files required by checked_receipt into a temp overlay.
    # Unrelated paths are unnecessary; canonical snapshots are copied individually.
    with tempfile.TemporaryDirectory(dir=HERE,prefix='.overlay-') as temporary:
        overlay=Path(temporary)
        def put(name,data):
            p=overlay/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for row in obligations:put(row['document'],documents[row['document']][0])
        for name,mapping in proposals.items():put(name,(json.dumps(mapping,indent=2)+'\n').encode())
        for (name,expected),data in archives.items():put(canonical(name,expected),data)
        put(SOURCE,future)
        # For all existing archived entries on each candidate map, provide the exact
        # original live/snapshot files without making an alternate duplicate archive tree.
        for name,mapping in proposals.items():
            for entry in mapping['entries']:
                archive=entry.get('archived_path');original=entry.get('original_path')
                if archive and not (overlay/archive).exists() and (ROOT/archive).is_file():put(archive,(ROOT/archive).read_bytes())
                if original and not (overlay/original).exists() and (ROOT/original).is_file():put(original,(ROOT/original).read_bytes())
            for document in mapping['documents']:
                if document in documents and not (overlay/document).exists():put(document,documents[document][0])
        for row in obligations:
            try:checked_receipt(overlay,row['document'],row['original_path'],row['old_sha256']);outcome='passed'
            except Exception as error:outcome=str(error)
            simulated.append(dict(**row,outcome=outcome))
        # Verify every actual recognized old-entry binding for existing documents,
        # in addition to the transitive obligations introduced by this proposal.
        for name,mapping in proposals.items():
            for document in mapping['documents']:
                if document not in documents:continue
                for entry in mapping['entries']:
                    pair=(entry.get('original_path'),entry.get('sha256'))
                    if pair not in documents[document][2]:continue
                    try:checked_receipt(overlay,document,*pair);outcome='passed'
                    except Exception as error:outcome=str(error)
                    existing_bindings.append(dict(document=document,original_path=pair[0],old_sha256=pair[1],outcome=outcome))
    for document,(data,_,_) in documents.items():
        if (ROOT/document).read_bytes()!=data:raise ValueError('Concurrent JSON receipt changed; rerun planner: '+document)
    for name,old in original_maps.items():
        if old is not None and (ROOT/name).read_bytes()!=old:raise ValueError('Concurrent map changed: '+name)
    failed=[r for r in simulated+existing_bindings if r['outcome']!='passed']
    output=dict(scope='nonmutating prospective preservation only; no source/profile installation',source=dict(original_path=SOURCE,old_sha256=OLD,new_sha256=NEW,future_copy=FUTURE),scan=dict(json_documents=len(documents),unreadable=unreadable,canonical_snapshot_targets_excluded=archived_skipped,reason='canonical snapshots are historical targets, not new receipt identities; own prospective context excluded'),closure=dict(queued_pairs=len(visited),receipt_obligations=len(obligations)),maps=maprows,archives=ar,baseline=baseline,simulated=simulated,all_existing_candidate_map_bindings=existing_bindings,issues=issues,failed=failed,passed=not failed and not issues)
    (HERE/'PLAN.json').write_text(json.dumps(output,indent=2)+'\n')
    writes=[dict(original_path=row['original_path'],old_sha256=row['old_sha256'],new_sha256=row['new_sha256'],operation='replace_existing_map' if row['old_sha256'] else 'create_new_map') for row in maprows]
    writes += [dict(original_path=row['canonical_archive'],old_sha256=None,new_sha256=row['old_sha256'],operation='create_canonical_snapshot') for row in ar if not row['already_present']]
    (HERE/'APPLY_WHITELIST.json').write_text(json.dumps(dict(scope='candidate metadata and canonical old-byte snapshots only; does not authorize source installation',writes=writes,future_source_install=dict(original_path=SOURCE,old_sha256=OLD,new_sha256=NEW,operation='separate later authorized exact copy after all gates')),indent=2)+'\n')
    print(json.dumps(dict(passed=output['passed'],maps=len(maprows),archives=len(ar),obligations=len(obligations),existing_bindings=len(existing_bindings),baseline_failures=len([x for x in baseline if x['outcome']!='passed']),failures=failed,issues=issues),indent=2))

if __name__=='__main__':main()
