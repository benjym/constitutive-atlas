"""Resolve unchanged historical screenshot pins to exact canonical archives."""
import hashlib,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PACKET=Path(__file__).resolve().parent
PLAN_SHA256='4a0d63713f2ef934f899b4275e2a4ca93592c9a37bc45dfa3c41eb255fb3c982'
def digest(blob):return hashlib.sha256(blob).hexdigest()
def resolve_screenshot(relative,root=ROOT,plan_path=PACKET/'plan-v1.json'):
    root=Path(root).resolve();raw=Path(plan_path).read_bytes()
    if digest(raw)!=PLAN_SHA256:raise ValueError('Retention plan changed')
    plan=json.loads(raw);document=plan['original_manifest'];manifest_raw=(root/document['path']).read_bytes()
    if digest(manifest_raw)!=document['sha256']:raise ValueError('Original browser manifest changed')
    manifest=json.loads(manifest_raw);rows=plan['files']
    if {k:v for k,v in manifest['files'].items() if k.startswith('screenshots/')}!={row['manifest_key']:row['sha256'] for row in rows}:raise ValueError('Original screenshot pins differ')
    matches=[row for row in rows if row['manifest_key']==relative]
    if len(matches)!=1:raise ValueError('Unknown original screenshot key')
    row=matches[0];original=Path(document['path']).parent/relative
    canonical=Path('catalogue/source-snapshots')/row['sha256']/original
    if original.as_posix()!=row['original_path'] or canonical.as_posix()!=row['archived_path']:raise ValueError('Noncanonical retention path')
    target=(root/canonical).resolve()
    if not target.is_relative_to(root):raise ValueError('Unsafe archive path')
    blob=target.read_bytes()
    if len(blob)!=row['bytes'] or digest(blob)!=row['sha256'] or not blob.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Screenshot archive corrupt')
    return target

def verify():
    plan=json.loads((PACKET/'plan-v1.json').read_text());rows=[]
    with tempfile.TemporaryDirectory(prefix='atlas-sclay-browser-recovery-') as directory:
        for row in plan['files']:
            source=resolve_screenshot(row['manifest_key']);blob=source.read_bytes()
            target=Path(directory)/row['original_path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
            assert digest(target.read_bytes())==row['sha256'] and target.read_bytes()==blob
            rows.append({'original_path':row['original_path'],'manifest_key':row['manifest_key'],'archived_path':str(source.relative_to(ROOT)),'sha256':digest(blob),'bytes':len(blob),'lossless_recovery':True,'original_absent':not (ROOT/row['original_path']).exists()})
    for invalid in ['../escape.png','screenshots/unknown.png','/screenshots/profile-desktop.png']:
        try:resolve_screenshot(invalid)
        except ValueError:pass
        else:raise AssertionError('Unknown key accepted')
    return {'kind':'sclay-browser-lossless-retention-v1','original_manifest':plan['original_manifest'],'files':rows,'recovered_files':len(rows),'recovered_bytes':sum(r['bytes'] for r in rows),'temporary_fixture_removed':True,'compiled_calls':0,'browser_calls':0}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
