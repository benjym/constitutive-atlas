"""Read-only actual five-member archive/qualification identity audit; no provision."""
from pathlib import Path
import hashlib,io,json,sys,tarfile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
sys.path.insert(0,str(ROOT))
from tools.provision_implicit_path_assets import selected_bytes,MEMBERS
A=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';F=ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1'
sha=lambda data:hashlib.sha256(data).hexdigest();pins={}
def data(path,expected=None):
    b=path.read_bytes();h=sha(b)
    if expected:assert h==expected,str(path)
    pins[path.relative_to(ROOT).as_posix()]=h;return b
index_path=A/'asset-provision-v1/INDEX.json';index=json.loads(data(index_path,'9d7c81df2989072ab83e6b4a7616a35da7a08545892a95101124e58b9eb98771'))
archive=ROOT/index['archive']['path'];blob=data(archive,'e527459cf66fe4703c66f4e9573bf614b3b2f50323a7cf7454aa0e6cf22b5880');assert len(blob)==219571
assert sha(blob)==index['archive']['sha256'];assert index['status']=='passed' and index['model']=='lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
members=selected_bytes(blob,index['files']);assert set(members)==MEMBERS
with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
    rows=tar.getmembers();assert len(rows)==5 and {m.name for m in rows}==MEMBERS
    assert all(m.isfile() and not m.pax_headers for m in rows)
    for m in rows:assert tar.extractfile(m).read()==members[m.name]
actual={
    'build-review.json':F/'independent-review/qualified-build-v1/build-review.json',
    'implicit-path-qualification.json':A/'qualified-assets-v1/implicit-path-qualification.json',
    'generated/models.json':F/'proposed-native-source/generated/models.json',
    'lade-domain.mjs':ROOT/'.local/lade-fused-linear-v1/wasm-build/lade-domain.mjs',
    'lade-domain.wasm':ROOT/'.local/lade-fused-linear-v1/wasm-build/lade-domain.wasm'}
for name,path in actual.items():assert data(path,index['files'][name])==members[name]
qualified=json.loads(members['implicit-path-qualification.json']);review=json.loads(members['build-review.json']);expected=json.loads(data(A/'EXPECTED_F_BINDING.json'))
assert qualified['schema_version']=='implicit-path-qualified-build-1' and qualified['model']==index['model'] and qualified['status']=='passed'
assert review['status']=='accepted' and review['reviewer_run']=='/root/lade_source_review' and qualified['implementation_run']=='/root'
assert review['reviewer_run']!=qualified['implementation_run'] and qualified['binding']==review['binding']==expected['binding']
assert qualified['gates']==review['gates'] and len(qualified['gates'])==11 and all(v is True for v in qualified['gates'].values())
assert qualified['independent_review']=={'path':'build-review.json','sha256':sha(members['build-review.json'])}
for row in qualified['evidence'].values():data(ROOT/row['path'],row['sha256'])
result={'passed':True,'members':5,'archive_bytes':len(blob),'qualification_sha256':sha(members['implicit-path-qualification.json']),'build_review_sha256':sha(members['build-review.json']),'scope':'Exact archived qualification/build-review/model catalogue and compiled bytes read only; no authorization/provisioning/material call','pins':pins}
(OUT/'qualified-assets-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='pins'}))
