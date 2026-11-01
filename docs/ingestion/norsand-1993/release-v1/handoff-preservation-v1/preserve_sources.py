"""One-shot exact-byte archival before the three assigned shared-source edits."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    assert not (OUT/'preservation.json').exists(), 'one-shot preservation already completed'
    spec = importlib.util.spec_from_file_location('scanner', OUT/'scan.py')
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    scanner.TARGETS = {'IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md','docs/ingestion/norsand-1993/DELIVERY.md','docs/ingestion/norsand-1993/CHECKLIST.md'}
    scanner.ROOTS = ('docs/ingestion/norsand-1993/release-v1',)
    scanner.EXCLUDE_PARTS.update({'ci-preservation-v1','layout-preservation-v1','final-preservation-v1','status-preservation-v1','merge-preservation-v1','merge-remote-preservation-v1','catalogue-routing-fix-v1','handoff-preservation-v1'})
    before = scanner.scan(ROOT)
    (OUT/'frozen').mkdir(exist_ok=True)
    (OUT/'frozen/bindings-before.json').write_text(json.dumps(before, indent=2)+'\n')
    primary = [r for r in before['primary_references'] if r['expected_equals_current_live'] and r['resolution'] != 'unresolved']
    original = {}
    maps = {}
    plans = {}

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
        assert pin is None or pin == document_pins[document], document
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
            if path not in maps or row['document'].endswith('/source-archive-map.json') or row['resolution']=='unresolved':
                continue
            if original[path] is None or row['sha256'] != sha(original[path]): continue
            key = (row['document'], path, row['sha256'])
            if key not in plans:
                plan(*key)
                changed = True
    (OUT/'planned-preservation.json').write_text(json.dumps({'bindings':[{'document':d,'original_path':p,'sha256':h,'archived_path':a} for (d,p,h),a in plans.items()], 'sidecars':sorted(maps)},indent=2)+'\n')
    # Preflight concurrent changes before any sidecar writes.
    for path, b in original.items():
        assert (ROOT/path).read_bytes() == b if b is not None else not (ROOT/path).exists(), path
    for document, path, expected in plans:
        assert sha((ROOT/document).read_bytes()) == document_pins[document], document
    for path, mapping in maps.items():
        (ROOT/path).write_text(json.dumps(mapping, indent=2)+'\n')
    checks = []
    for (document,path,expected), archived in plans.items():
        try: resolved = checked_receipt(ROOT, document, path, expected)
        except Exception as e: raise RuntimeError((document,path,expected)) from e
        assert resolved == ROOT/archived
        checks.append({'document':document,'original_path':path,'sha256':expected,'archived_path':archived})
    (OUT/'preservation.json').write_text(json.dumps({
        'scope':'source identity preservation only; original receipt documents unchanged',
        'bindings':checks,'changed_sidecars':sorted(maps),
        'original_documents_unchanged':True, 'preexisting_unresolved': [r for r in before['primary_references']+before['secondary_source_map_references'] if r['resolution']=='unresolved']},indent=2)+'\n')
    print(json.dumps({'bindings':len(checks),'sidecars':len(maps)}))


if __name__ == '__main__': main()
