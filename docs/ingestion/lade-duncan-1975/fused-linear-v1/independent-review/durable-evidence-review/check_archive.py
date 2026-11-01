"""Read-only archive roundtrip and exact numerical-receipt coverage audit."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5];PACKET=OUT.parents[1]
BASE=PACKET/'durable-evidence-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
manifest_path=BASE/'MANIFEST.json';manifest=json.loads(manifest_path.read_bytes())
assert sha(manifest_path.read_bytes())=='2cf5f3a557fdafd40a7a404823d4e00bb73283246321f5447f20c449289be94a'
archive=ROOT/manifest['archive']['path'];assert sha(archive.read_bytes())==manifest['archive']['sha256']=='3aa84f704d9881885575ac98395a2fc83364ba6791eebb927eb66505b392f421'
assert archive.stat().st_size==manifest['archive']['bytes'];assert manifest['member_count']==len(manifest['files'])==6331
actual={};suffixes=collections.Counter()
with tarfile.open(archive,'r:gz') as tar:
    for member in tar:
        name=member.name;relative=PurePosixPath(name)
        assert member.isfile() and not relative.is_absolute() and '..' not in relative.parts and name not in actual,name
        assert name in manifest['files'],name
        assert member.size<=64*1024*1024,name
        data=tar.extractfile(member).read();assert len(data)==member.size
        actual[name]=sha(data);assert actual[name]==manifest['files'][name],name
        assert sha((ROOT/name).read_bytes())==actual[name],name
        assert not data.startswith(b'%PDF-'),name
        assert relative.suffix.lower() not in ['.pdf','.docx','.dll','.o','.obj','.a','.dylib'],name
        assert 'emscripten-cache' not in relative.parts and '.codex-attachments' not in relative.parts and 'private-sources' not in relative.parts,name
        suffixes[relative.suffix]+=1
assert actual==manifest['files']
recovery=json.loads((PACKET/'legacy-prerequisite-recovery-v1/RECOVERY.json').read_bytes())
recovered={row['original_path']:row for row in recovery['records'] if row['changed']}
assert len(recovered)==24
for row in recovered.values():assert actual[row['archived_path']]==row['old_sha256']
coverage=[]
def cover(label,files):
    count=0;archived=0
    for name,pin in files.items():
        if not name.startswith('.local/lade-fused-linear-v1/'):continue
        count+=1
        if actual.get(name)==pin:continue
        row=recovered.get(name);assert row and pin==row['old_sha256'] and actual[row['archived_path']]==pin,(label,name)
        archived+=1
    coverage.append({'receipt_or_report':label,'qualified_local_pins_covered':count,'via_recovered_archive':archived})
for receipt in ['saved-wasm-full-review-receipt.json','saved-wasm-chain-source-review-receipt.json']:
    cover(receipt,json.loads((OUT.parent/receipt).read_bytes())['files'])
for receipt in ['native-first-build-receipt.json','native-build-receipt.json','wasm-build-receipt.json']:
    cover(receipt,json.loads((PACKET/receipt).read_bytes())['files'])
for reportname in ['native-triaxial-results.json','native-triaxial-fixed-results.json','native-domain-results.json','native-lifecycle-corrected-results.json','native-legacy-results.json','native-supplement-results.json','wasm-legacy-prerequisite-results.json','wasm-results.json','wasm-chain-results.json']:
    doc=json.loads((PACKET/reportname).read_bytes());files={}
    for row in doc.get('requests',[])+doc.get('records',[]):
        if 'raw_path' in row:files[row['raw_path']]=row['raw_sha256']
    cover(reportname,files)
# Independently reconstruct the stated inventory, without running archive.py.
local=ROOT/'.local/lade-fused-linear-v1';expected=set()
for p in local.iterdir():
    if p.name=='emscripten-cache':continue
    if p.name.endswith('-build'):
        expected.update(q.relative_to(ROOT).as_posix() for q in p.iterdir() if q.is_file() and (q.name.startswith('atlas_') or q.suffix in ('.mjs','.wasm')))
    elif p.is_dir():expected.update(q.relative_to(ROOT).as_posix() for q in p.rglob('*') if q.is_file())
    elif p.is_file():expected.add(p.relative_to(ROOT).as_posix())
expected.update(row['archived_path'] for row in recovered.values());assert expected==set(actual)
result={'passed':True,'members':6331,'archive_sha256':manifest['archive']['sha256'],'manifest_sha256':sha(manifest_path.read_bytes()),'coverage':coverage,'suffix_counts':dict(suffixes),'copyright_scope':'No PDF magic, paper/document/private-source paths; source and executable bytes read only, never executed','scope':'Read-only durable qualified F archive inventory/hash roundtrip; not a new numerical or E5/browser claim'}
(OUT/'archive-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
