"""Independent nonmutating future-profile receipt overlay audit."""
from pathlib import Path
import hashlib,json,sys,tempfile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
BASE=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/profile-install-v1/revision-v2'
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
plan=read(BASE/'PLAN.json');whitelist=read(BASE/'APPLY_WHITELIST.json');freeze=read(BASE/'SOURCE_FREEZE.json')
assert sha(BASE/'PLAN.json')=='e0439b53c593c38ca75488691bba2eeeca027be88a4a9195e1fc0016ca85271a'
assert sha(BASE/'APPLY_WHITELIST.json')=='276540c16c1320b1247f740f5195eeba5dd187a23aa7d2f500012ca0dd59a1c0'
assert sha(BASE/'SOURCE_FREEZE.json')=='5780c1c8c5f6a03682dee510b116bcaaf132dc7f2ddbb4e9da83fff292652ee7'
pins={}
def pin(name,expected):
    assert sha(ROOT/name)==expected,name
    pins[name]=expected
for name in ['SOURCE_FREEZE.json','SOURCE_PINS.json']:
    for row in read(BASE/name)['files']:pin(row['original_path'],row['old_sha256'])
source=plan['source'];pin(source['original_path'],source['old_sha256']);pin(source['future_copy'],source['new_sha256'])
assert len(plan['maps'])==20 and len(whitelist['writes'])==26
expected_writes={};oldbytes={}
for row in plan['maps']:
    name=row['original_path'];live=ROOT/name;candidate=BASE/row['candidate'];assert sha(candidate)==row['new_sha256']
    assert (sha(live) if live.exists() else None)==row['old_sha256'],name
    before=read(live) if live.exists() else {'documents':{},'entries':[]}
    after=read(candidate);assert after['version']=='immutable-source-archive-map-0.1'
    assert all(after['documents'].get(k)==v for k,v in before['documents'].items()),name
    assert all(entry in after['entries'] for entry in before['entries']),name
    assert len({(e['original_path'],e['sha256']) for e in after['entries']})==len(after['entries'])
    for entry in after['entries']:assert entry['archived_path']=='catalogue/source-snapshots/'+entry['sha256']+'/'+entry['original_path']
    for doc,h in after['documents'].items():pin(doc,h)
    expected_writes[name]=(row['old_sha256'],row['new_sha256'])
    if live.exists():oldbytes[name]=live.read_bytes()
for row in plan['archives']:
    assert sha(BASE/row['snapshot'])==row['old_sha256']
    target=ROOT/row['canonical_archive'];assert row['already_present']==target.exists()
    if target.exists():pin(row['canonical_archive'],row['old_sha256'])
    else:expected_writes[row['canonical_archive']]=(None,row['old_sha256'])
assert expected_writes=={row['original_path']:(row['old_sha256'],row['new_sha256']) for row in whitelist['writes']}
for name,(old,new) in expected_writes.items():assert (sha(ROOT/name) if (ROOT/name).exists() else None)==old,name
checks=plan['combined_overlay_checks'];assert len(checks)==218
with tempfile.TemporaryDirectory(dir=OUT,prefix='overlay-') as temporary:
    overlay=Path(temporary)
    def put(name,data,overwrite=False):
        p=overlay/name
        if p.exists() and not overwrite:return
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    for row in plan['maps']:
        mapping=read(BASE/row['candidate'])
        for doc in mapping['documents']:put(doc,(ROOT/doc).read_bytes())
        for entry in mapping['entries']:
            for name in [entry['original_path'],entry['archived_path']]:
                if (ROOT/name).is_file():put(name,(ROOT/name).read_bytes())
    for row in checks:
        put(row['document'],(ROOT/row['document']).read_bytes())
        sidecar=(Path(row['document']).parent/'source-archive-map.json').as_posix()
        if (ROOT/sidecar).is_file():put(sidecar,(ROOT/sidecar).read_bytes())
        name=row['original_path']
        if (ROOT/name).is_file():put(name,(ROOT/name).read_bytes())
    for row in plan['archives']:put(row['canonical_archive'],(BASE/row['snapshot']).read_bytes(),True)
    for row in plan['maps']:put(row['original_path'],(BASE/row['candidate']).read_bytes(),True)
    put(source['original_path'],(ROOT/source['future_copy']).read_bytes(),True)
    for row in checks:checked_receipt(overlay,row['document'],row['original_path'],row['old_sha256'])
    # Fresh independent scan: no new receipt consumer may be omitted from closure.
    targets={(r['original_path'],r['old_sha256']) for r in plan['archives']}
    def found(node):
        pairs=set()
        if isinstance(node,dict):
            for k,v in node.items():
                if isinstance(v,str) and (k,v) in targets:pairs.add((k,v))
                pairs.update(found(v))
            if isinstance(node.get('path'),str):
                for k in ['sha256','hash']:
                    pair=(node['path'],node.get(k))
                    if isinstance(pair[1],str) and pair in targets:pairs.add(pair)
        elif isinstance(node,list):
            for value in node:pairs.update(found(value))
        return pairs
    scanned=0;fresh_bindings=0
    for directory in ['docs','catalogue']:
        for doc in (ROOT/directory).rglob('*.json'):
            relative=doc.relative_to(ROOT)
            if relative.as_posix().startswith('catalogue/source-snapshots/') or doc.is_relative_to(BASE.parent) or doc.is_relative_to(OUT):continue
            try:value=read(doc)
            except (ValueError,UnicodeDecodeError):continue
            scanned+=1;pairs=found(value)
            if not pairs:continue
            put(relative,doc.read_bytes())
            sidecar=relative.parent/'source-archive-map.json'
            if not (overlay/sidecar).exists() and (ROOT/sidecar).is_file():put(sidecar,(ROOT/sidecar).read_bytes())
            for name,h in pairs:checked_receipt(overlay,relative,name,h);fresh_bindings+=1
    recovered=read(ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1/legacy-prerequisite-recovery-v1/RECOVERY.json')
    for row in recovered['records']:
        assert sha(ROOT/row['original_path'])==row['current_full_sha256']
        assert sha(overlay/row['original_path'])==row['current_full_sha256']
for name,data in oldbytes.items():assert (ROOT/name).read_bytes()==data
pin(source['original_path'],source['old_sha256'])
result={'passed':True,'overlay_checks':218,'fresh_json_documents_scanned':scanned,'fresh_affected_receipt_bindings':fresh_bindings,'maps':20,'new_canonical_snapshots':6,'exact_whitelisted_writes':26,'current_raws_unchanged':57,'old_entries_and_document_pins_preserved':True,'production_writes':0,'observed_preconditions':[{'original_path':name,'old_sha256':h} for name,h in pins.items()]}
(OUT/'preservation-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='observed_preconditions'}))
