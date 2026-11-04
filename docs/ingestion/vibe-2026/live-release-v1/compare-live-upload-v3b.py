from pathlib import Path
from urllib.parse import urlparse,unquote
import json,sys,tarfile,hashlib
base=Path(__file__).resolve().parent
upload=json.loads(Path(sys.argv[1]).read_text())
assert upload['revision']==sys.argv[2] and upload['pages_run']==int(sys.argv[3]);deployment=int(sys.argv[4])
raw=base/'browser-v3'
def result(name):
 s=(raw/(name+'.log')).read_text();return json.loads(s.split('### Result\n',1)[1].split('\n### Ran',1)[0].strip())
assets=result('fetched-identities');links=result('profile-links');assert len(assets)==26 and len(links)==9
rows=[]
for row in assets+links:
 url=row.get('url',row.get('href'));p=urlparse(url);assert p.scheme=='https' and p.netloc=='benjym.github.io'
 prefix='/constitutive-atlas/';assert p.path.startswith(prefix)
 name=unquote(p.path[len(prefix):]);assert row['status']==200 and upload['files'][name]==row['sha256'],name
 rows.append({'path':name,'sha256':row['sha256'],'http_status':200})
run=json.loads((raw/'default-run.json').read_text())
with tarfile.open(upload['archive_path'],'r:*') as tf:
 members={m.name.removeprefix('./'):m for m in tf if m.isfile()}
 identity=json.load(tf.extractfile(members['engine-controlled-time/identity.json']))
assert run['identity']==identity
for n,h in identity['files'].items():assert upload['files']['engine-controlled-time/'+n]==h
for n,h in identity['components'].items():assert upload['files'][n]==h
for name in ['profile-content','profile-mobile-content']:
 r=result(name);assert r['rows']==30 and r['tech']['open'] is False and r['bounds']['page']==r['bounds']['viewport']
for name in ['live-mobile-bounds','live-desktop-bounds']:assert len(result(name)['rows'])==3
assert result('live-network-timing')['bad']==[]
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (raw/'live-console.log').read_text()
comparison=json.loads((base/'live-default-comparison-v3.json').read_text());assert comparison['request_exact'] and comparison['complete_result_exact']
report={'revision':upload['revision'],'pages_run':upload['pages_run'],'deployment_id':deployment,'tested_upload_sha256':upload['archive_sha256'],'upload_files':len(upload['files']),'matched_live_checks':len(rows),'matches':rows,'export_identity_exact_upload':True,'default_complete_reference_equal':True,'profile_desktop_mobile_pass':True,'plot_desktop_mobile_pass':True,'console_errors':0,'console_warnings':0,'http_failures':0,'scientific_limits':'Numerical qualification for disclosed Appendix A scope; no experimental validation.'}
out=base/'live-upload-comparison-v3.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',len(rows),'live asset/link matches and complete default/identity/profile/plot checks')
