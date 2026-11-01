"""Plan/apply additive exact-byte archival before the three owned source edits."""
from pathlib import Path
import copy, hashlib, json, sys, tempfile
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
scan = read(HERE / 'prior-references.json')
initial = {r['original_path']:r['sha256'] for r in scan['live_source_identities']}
primary = [r for r in scan['primary_references'] if r['resolution'] == 'live']
secondary = scan['secondary_source_map_references']
redirect = list(primary)
maps = {str(Path(r['document']).parent / 'source-archive-map.json') for r in primary}
while True:
    selected = [r for r in secondary if r['resolution'] == 'live' and r['original_path'] in maps]
    extra = {str(Path(r['document']).parent / 'source-archive-map.json') for r in selected}
    if extra <= maps:
        redirect += selected
        break
    maps |= extra
prior = dict(initial)
for name in maps:
    if (ROOT/name).exists():
        prior[name] = sha(ROOT/name)
for name, expected in prior.items():
    assert sha(ROOT/name) == expected, name
newmaps = {}
docs = {}
for name in sorted(maps):
    path = ROOT/name
    node = copy.deepcopy(read(path)) if path.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
    assert node['version'] == 'immutable-source-archive-map-0.1'
    for document in sorted(path.parent.glob('*.json')):
        if document.name == 'source-archive-map.json':
            continue
        rel = str(document.relative_to(ROOT))
        node['documents'].setdefault(rel, sha(document))
    for row in redirect:
        if str(Path(row['document']).parent / 'source-archive-map.json') != name:
            continue
        docs[row['document']] = sha(ROOT/row['document'])
        assert node['documents'].get(row['document']) == docs[row['document']]
        entry = {'original_path':row['original_path'],'sha256':row['sha256'],
                 'archived_path':str(Path('catalogue/source-snapshots')/row['sha256']/row['original_path'])}
        if entry not in node['entries']:
            node['entries'].append(entry)
    newmaps[name] = node
affected_secondary = [r for r in secondary if r['resolution'] != 'unresolved' and (r['original_path'] in maps or r['document'] in maps)]
def check(root, row):
    if all(loc['shape'] == 'original_path-object' for loc in row['locations']):
        original = root/row['original_path']
        archive = root/'catalogue/source-snapshots'/row['sha256']/row['original_path']
        assert any(p.is_file() and sha(p) == row['sha256'] for p in [archive, original])
    else:
        assert sha(checked_receipt(root,row['document'],row['original_path'],row['sha256'])) == row['sha256']
for row in redirect + affected_secondary:
    check(ROOT, row)
# Minimal shadow installation validates remapping before mutating the checkout.
with tempfile.TemporaryDirectory(prefix='tmd2-archive-shadow-') as directory:
    shadow = Path(directory)
    def put(name, data):
        target = shadow/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for name, expected in prior.items():
        put(str(Path('catalogue/source-snapshots')/expected/name), (ROOT/name).read_bytes())
    for row in redirect + affected_secondary:
        for name in [row['document'],row['original_path'],row.get('resolved_path')]:
            if name and (ROOT/name).is_file():
                put(name,(ROOT/name).read_bytes())
        side = str(Path(row['document']).parent/'source-archive-map.json')
        if (ROOT/side).is_file():
            put(side,(ROOT/side).read_bytes())
    for name,node in newmaps.items():
        put(name,(json.dumps(node,indent=2)+'\n').encode())
    for name in initial:
        put(name,b'changed source bytes for shadow verification')
    for row in redirect + affected_secondary:
        check(shadow,row)
plan = {'prior':prior,'maps':newmaps,'unchanged_documents':docs,
        'redirected_pairs':redirect,'affected_secondary':affected_secondary,
        'preexisting_unresolved_primary':scan['summary']['primary_unresolved'],
        'scope':'Exact additive archival only; copied receipt maps retain their previous bytes at content-addressed paths.'}
if '--apply' not in sys.argv:
    (HERE/'archive-plan-v2.json').write_text(json.dumps(plan,indent=2)+'\n')
    print('Shadow PASS:',len(redirect),'primary/direct pairs;',len(affected_secondary),'secondary pairs;',len(maps),'maps.')
    sys.exit(0)
saved = read(HERE/'archive-plan-v2.json')
assert saved == plan, 'Plan or source identities changed'
for name,expected in prior.items():
    for target in [ROOT/'catalogue/source-snapshots'/expected/name,HERE/'prior-source'/name]:
        target.parent.mkdir(parents=True,exist_ok=True)
        raw=(ROOT/name).read_bytes()
        if target.exists():
            assert target.read_bytes() == raw
        else:
            target.write_bytes(raw)
for name,node in newmaps.items():
    target=ROOT/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(node,indent=2)+'\n')
for name,expected in docs.items():
    assert sha(ROOT/name) == expected
for row in redirect + affected_secondary:
    check(ROOT,row)
print('Applied exact additive preservation; source replacements may now proceed.')
