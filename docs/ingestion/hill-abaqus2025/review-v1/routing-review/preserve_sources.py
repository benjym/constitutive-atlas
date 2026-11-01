"""Plan/apply exact-byte source preservation; default dry run, no receipt rewrites.

Only canonical source snapshots and per-directory source-archive-map.json can be
written with --apply. Archive-map changes are closed transitively through all
tracked checked_receipt-compatible JSON pins. Outputs retain exact original hashes.
"""
import argparse,hashlib,importlib,json,subprocess,sys
from pathlib import Path
SHARED=['web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','tests/test_j2_main_routing.mjs']
def sha(b):return hashlib.sha256(b).hexdigest()
def packed(j):return (json.dumps(j,indent=2)+'\n').encode()
def pins(node):
    if isinstance(node,dict):
        for key,value in node.items():
            if isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value) and '/' in key:yield key,value
        p=node.get('path')
        if isinstance(p,str):
            for key in ['sha256','hash']:
                value=node.get(key)
                if isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value):yield p,value
        for value in node.values():yield from pins(value)
    elif isinstance(node,list):
        for value in node:yield from pins(value)
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',type=Path,required=True);a.add_argument('--git-root',type=Path,required=True);a.add_argument('--base',required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--apply',action='store_true');args=a.parse_args()
    root=args.root.resolve();git=args.git_root.resolve();original={};planned={};archives={};changed={};checks=set();matches={}
    def blob(rev,p):return subprocess.check_output(['git','show',rev+':'+p],cwd=git)
    def current(p):
        if p not in original:original[p]=(root/p).read_bytes() if (root/p).exists() else None
        return original[p]
    def archive(p,b):
        target='catalogue/source-snapshots/'+sha(b)+'/'+p
        existing=current(target)
        if existing is not None and existing!=b:raise ValueError('Conflicting immutable snapshot: '+target)
        archives[target]=b
    for p in SHARED:
        old=blob(args.base,p);archive(p,old)
        changed[p]=sha(old)  # Prospective shared whitelist: preserve before edits too.
    # Tracked JSON documents only; canonical snapshots retain independent original contexts.
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',args.base],cwd=git,text=True).splitlines()
    docs={}
    for p in paths:
        if not p.endswith('.json') or p.startswith('catalogue/source-snapshots/'):continue
        b=current(p)
        if b is None:continue
        try:j=json.loads(b)
        except (ValueError,UnicodeDecodeError):continue
        ps=set(pins(j))
        if ps:docs[p]=(sha(b),ps)
    # Every changed original is considered, including old bytes of newly edited maps.
    for iteration in range(100):
        prior=set(changed.items())
        grouped={}
        for doc,(digest,ps) in docs.items():
            wanted=ps & set(changed.items())
            if wanted:grouped[doc]=(digest,wanted)
        for doc,(digest,wanted) in grouped.items():
            side=str(Path(doc).parent/'source-archive-map.json')
            if side==doc:raise ValueError('Self-referential archive-map receipt requires separately reviewed context: '+doc)
            if side not in planned:
                raw=current(side)
                mapping=json.loads(raw) if raw else dict(version='immutable-source-archive-map-0.1',documents={},entries=[])
                if raw is None:
                    # A new sidecar governs every existing sibling receipt, even
                    # unchanged-source lookups: preserve all sibling identities.
                    for sibling in (root/side).parent.glob('*.json'):
                        if sibling.name!='source-archive-map.json':
                            mapping['documents'][sibling.relative_to(root).as_posix()]=sha(sibling.read_bytes())
                if mapping.get('version')!='immutable-source-archive-map-0.1':raise ValueError('Unknown sidecar: '+side)
                planned[side]=mapping
            mapping=planned[side];docpin=mapping.setdefault('documents',{}).get(doc)
            if docpin is not None and docpin!=digest:raise ValueError('Existing receipt binding differs: '+doc)
            mapping['documents'][doc]=digest
            for p,h in sorted(wanted):
                target='catalogue/source-snapshots/'+h+'/'+p
                if target not in archives:
                    raw=current(p)
                    if raw is None or sha(raw)!=h:raise ValueError('Missing exact old bytes: '+p+' '+h)
                    archive(p,raw)
                matching=[e for e in mapping.setdefault('entries',[]) if e.get('original_path')==p and e.get('sha256')==h]
                if len(matching)>1:raise ValueError('Duplicate archive entries: '+side)
                entry=dict(original_path=p,sha256=h,archived_path=target)
                if matching:
                    if matching[0]!=entry:raise ValueError('Conflicting existing archive mapping: '+side)
                else:mapping['entries'].append(entry)
                checks.add((doc,p,h));matches.setdefault(side,set()).add(doc)
        for p,mapping in planned.items():
            old=current(p);new=packed(mapping)
            if old is not None and old!=new:
                archive(p,old);changed[p]=sha(old)
        if set(changed.items())==prior:break
    else:raise ValueError('Archive reverse closure did not converge')
    writes={p:b for p,b in archives.items() if current(p)!=b}
    writes.update({p:packed(j) for p,j in planned.items() if current(p)!=packed(j)})
    result=dict(mode='apply' if args.apply else 'dry-run',base=args.base,root=str(root),shared_paths=SHARED,tracked_receipt_documents=len(docs),closure_iterations=iteration+1,receipt_checks=len(checks),maps_changed=sum(p.endswith('/source-archive-map.json') for p in writes),snapshots_added=sum(p.startswith('catalogue/source-snapshots/') for p in writes),files={p:dict(before=sha(current(p)) if current(p) is not None else None,after=sha(b)) for p,b in sorted(writes.items())})
    # Persist compact reviewable plan before mutations. Caller must own this destination.
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'preservation-plan.json').write_bytes(packed(result));(args.output/'receipt-checks.json').write_bytes(packed([dict(document=d,path=p,sha256=h) for d,p,h in sorted(checks)]))
    if args.apply:
        for p,b in writes.items():
            dest=root/p
            if dest.is_symlink() or not dest.resolve().is_relative_to(root):raise ValueError('Unsafe destination: '+p)
            expected=original[p];observed=dest.read_bytes() if dest.exists() else None
            if observed!=expected:raise ValueError('Concurrent destination change: '+p)
        for p,b in writes.items():
            dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
        for doc,p,h in sorted(checks):checked_receipt(root,Path(doc),p,h)
        for p,b in archives.items():assert (root/p).read_bytes()==b
        result['all_checked_receipt_pairs_passed']=True;(args.output/'preservation-result.json').write_bytes(packed(result))
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
if __name__=='__main__':main()
