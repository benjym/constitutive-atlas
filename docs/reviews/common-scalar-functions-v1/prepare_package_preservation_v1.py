"""One-shot exact-byte archival before the assigned solver/policy edits."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent/'package-preservation-v1'
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    assert not (OUT/'preservation.json').exists(), 'one-shot preservation already completed'
    spec = importlib.util.spec_from_file_location('scanner', ROOT/'docs/reviews/spectral-dsl-source-bindings-v1/audit/scan.py')
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    scanner.TARGETS = set(json.loads((OUT.parent/'package-install-base-preflight-v1.json').read_text())['existing_destination_bases'])
    # External historical worktree receipts are not references to owned files.
    original_pairs=scanner.pairs
    external=set()
    def owned_pairs(node,parts=(),secondary=False):
        for row in original_pairs(node,parts,secondary):
            path=row[0]
            if Path(path).is_absolute() or '..' in Path(path).parts:
                external.add(path)
            else:
                yield row
    scanner.pairs=owned_pairs
    before = scanner.scan(ROOT)
    before['excluded_external_sidecar_paths']=sorted(external)
    (OUT/'frozen').mkdir(exist_ok=True)
    (OUT/'frozen/bindings-before.json').write_text(json.dumps(before, indent=2)+'\n')
    primary = [r for r in before['primary_references'] if r['expected_equals_current_live']]
    original = {}
    maps = {}
    plans = {}
    rollforwards = []

    def archive(path):
        b = (ROOT/path).read_bytes()
        h = sha(b)
        dest = ROOT/'catalogue/source-snapshots'/h/path
        if dest.exists():
            assert dest.read_bytes() == b
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b)
        return h, dest.relative_to(ROOT).as_posix()

    def plan(document, path, expected):
        assert sha((ROOT/document).read_bytes()) == document_pins[document]
        sidecar = str(Path(document).parent/'source-archive-map.json')
        if sidecar not in maps:
            p = ROOT/sidecar
            original[sidecar] = p.read_bytes() if p.exists() else None
            maps[sidecar] = json.loads(original[sidecar]) if p.exists() else {
                'version':'immutable-source-archive-map-0.1', 'documents':{}, 'entries':[]}
            assert maps[sidecar]['version'] == 'immutable-source-archive-map-0.1'
            if p.exists(): archive(sidecar)
            else:
                for sibling in p.parent.glob('*.json'):
                    maps[sidecar]['documents'][sibling.relative_to(ROOT).as_posix()] = sha(sibling.read_bytes())
        mapping = maps[sidecar]
        pin = mapping['documents'].get(document)
        if pin is not None and pin != document_pins[document]:
            prior=ROOT/'catalogue/source-snapshots'/pin/document
            assert prior.is_file() and sha(prior.read_bytes())==pin, ('Missing prior document archive', document, pin)
            current_h,current_archive=archive(document)
            assert current_h==document_pins[document]
            map_h,map_archive=archive(sidecar)
            rollforwards.append({'document':document,'prior_sha256':pin,'prior_archived_path':prior.relative_to(ROOT).as_posix(),'current_sha256':current_h,'current_archived_path':current_archive,'sidecar':sidecar,'prior_sidecar_sha256':map_h,'prior_sidecar_archived_path':map_archive,'reason':'Existing mutable document version already changed; preserve both exact versions and original sidecar before updating current document pin; no source expected hash or receipt document modified'})
        mapping['documents'][document] = document_pins[document]
        h, archived = archive(path)
        assert h == expected, (path, expected, h)
        entry = {'original_path':path, 'sha256':h, 'archived_path':archived}
        matches = [e for e in mapping['entries'] if e['original_path']==path and e['sha256']==h]
        assert not matches or matches == [entry]
        if not matches: mapping['entries'].append(entry)
        plans[(document,path,expected)] = archived

    document_pins = {r['document']:r['document_sha256'] for r in before['primary_references']+before['secondary_source_map_references']}
    for source in sorted(scanner.TARGETS): archive(source)
    for row in primary: plan(row['document'], row['original_path'], row['sha256'])
    # Preserve old map identities for ordinary receipt documents that pin a map
    # we are extending. Sidecar-entry references already resolve directly to the
    # old canonical snapshot, which archive() preserves before extension.
    changed = True
    while changed:
        changed = False
        for row in before['secondary_source_map_references']:
            path = row['original_path']
            if path not in maps or row['document'].endswith('/source-archive-map.json'):
                continue
            if original[path] is None or row['sha256'] != sha(original[path]): continue
            key = (row['document'], path, row['sha256'])
            if key not in plans:
                plan(*key)
                changed = True
    # Preflight concurrent changes before any sidecar writes.
    for path, b in original.items():
        assert (ROOT/path).read_bytes() == b if b is not None else not (ROOT/path).exists(), path
    for document, path, expected in plans:
        assert sha((ROOT/document).read_bytes()) == document_pins[document], document
    staged={}
    for path,mapping in maps.items():
        f=OUT/'planned-sidecars'/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(mapping,indent=2)+'\n');staged[path]={'proposed_path':str(f.relative_to(ROOT)),'proposed_sha256':sha(f.read_bytes()),'original_sha256':None if original[path] is None else sha(original[path])}
    checks=[]
    for (document,path,expected),archived in plans.items():
        assert sha((ROOT/document).read_bytes())==document_pins[document]
        assert sha((ROOT/archived).read_bytes())==expected
        checks.append({'document':document,'original_path':path,'sha256':expected,'archived_path':archived})
    (OUT/'preservation-plan.json').write_text(json.dumps({'status':'Prospective; canonical archives added, no sidecars or runtime changed','bindings':checks,'planned_sidecars':staged,'document_pins':{d:document_pins[d] for d,_,_ in plans},'document_pin_rollforwards':rollforwards,'original_documents_unchanged':True},indent=2)+'\n')
    print(json.dumps({'bindings':len(checks),'planned_sidecars':len(maps),'document_pin_rollforwards':len(rollforwards)}))


if __name__ == '__main__': main()
