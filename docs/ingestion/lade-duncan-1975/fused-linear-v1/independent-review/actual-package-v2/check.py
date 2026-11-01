from pathlib import Path
import hashlib,json,sys,tarfile,math
H=Path(__file__).resolve().parent;R=H.parents[5];sys.path.insert(0,str(R))
from tools.test_implicit_path_package import check
A=R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';P=A/'actual-package-v2';S=R/'.local/lade-main-atlas-v2/site'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
receipt=load(P/'PACKAGE_RECEIPT.json');manifest=load(P/'PACKAGE_MANIFEST.json');archive=P/'website.tar.gz'
assert sha(archive)==receipt['archive_sha256']=='ace661fddee71afcbe78f1649f66b98dd4c792d6a6835569637ac7b830ce161c'
assert sha(P/'PACKAGE_MANIFEST.json')==receipt['manifest_sha256']=='11728066e39755b17e827b9048f4bb0c1d29a950e2e22bb10c3f83a20a0313e9'
rows={r['path']:r for r in manifest['files']};assert len(rows)==len(manifest['files'])==receipt['files']==980
assert archive.stat().st_size==receipt['bytes']
for name,row in rows.items():assert sha(S/name)==row['sha256'] and (S/name).stat().st_size==row['bytes']
assert {p.relative_to(S).as_posix() for p in S.rglob('*') if p.is_file()}==set(rows)
with tarfile.open(archive) as t:
 ms=t.getmembers();assert len(ms)==980 and len({m.name for m in ms})==980
 for m in ms:
  assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  b=t.extractfile(m).read();assert len(b)==rows[m.name]['bytes'] and hashlib.sha256(b).hexdigest()==rows[m.name]['sha256']
assert not any(name.endswith('.pdf') or '/private-sources/' in name or name.startswith('.local/') for name in rows)
old={r['path']:r for r in load(A/'actual-package-v1/PACKAGE_MANIFEST.json')['files']}
delta=dict(only_old=sorted(set(old)-set(rows)),only_new=sorted(set(rows)-set(old)),changed=[dict(path=n,before=old[n]['sha256'],after=rows[n]['sha256']) for n in sorted(set(old)&set(rows)) if old[n]['sha256']!=rows[n]['sha256']])
assert delta==load(P/'PACKAGE_DELTA.json') and [r['path'] for r in delta['changed']]==['app.js']
assert len(delta['only_old'])==len(delta['only_new'])==1 and all(n.startswith('implicit-path-package-checks/build-') and n.endswith('/report.json') for n in delta['only_old']+delta['only_new'])
freeze=load(P/'EXECUTION_SOURCE_FREEZE.json');assert len(freeze['files'])==8194
for name,h in freeze['files'].items():assert sha(R/name)==h,name
post=load(P/'POST_BUILD_SOURCE_CHECK.json');assert post==dict(passed=True,checked_files=8194,drift=[])
for name in ['standard-site-build','public-dense-loose-replay','supported-ordinary-package','installed-routing','package-unit-tests']:
 status=load(P/'execution'/name/'STATUS.json');assert status['status']=='passed' and status['exit_code']==0 and status['elapsed_seconds']<status['deadline_seconds']
package=check(S);assert package['status']=='passed' and len(package['checks'])==106
(H/'package-check-results.json').write_text(json.dumps(package,indent=2)+'\n')
public=load(P/'public-presets.json');assert public['status']=='passed' and public['phase']=='complete' and len(public['calls'])==5
for name,h in public['inputs'].items():assert sha(R/name)==h
policy=load(A/'public-ci-v1/POLICY.json');bounds=policy['source_final_bounds'];refs=load(R/policy['references'])
for row in public['rows']:
 reference=[c['reference'] for c in refs['cases'] if c['set']==row['name'] and c['reference']['axial_strain']==.005];assert reference==[row['reference']]
 assert row['controls']['steps']==400 and row['controls']['target']==.005 and row['controls']['protocol']==1
 for phase in row['phases']:
  result=phase['result'];assert result['ok'] is True and len(result['points'])==401
  end=result['points'][-1];ref=row['reference'];errors=dict(relative_axial_stress=abs(end['state'][0]-ref['axial_stress'])/ref['axial_stress'],absolute_radial_strain=abs(end['strain'][1]-ref['radial_strain']),relative_work_using_1Pa_floor=abs(end['state'][7]-ref['wp'])/max(1,abs(ref['wp'])))
  assert errors==phase['source_errors'] and all(math.isfinite(v) and v<=bounds[k] for k,v in errors.items())
for folder,expected in [('metadata',1),('material',4)]:
 records=load(P/f'public-presets.json.raw/{folder}/manifest.json')['records'];assert len(records)==expected
 for record in records:
  assert record['state']=='finished' and record['status']==0 and record['signal'] is None and record['error'] is None and record['elapsed_ms']<120000
  for kind in ['stdout','stderr']:assert sha(Path(record[kind]['path']))==record[kind]['sha256']
ordinary=load(P/'supported-package.json');assert ordinary['status']=='passed' and len(ordinary['ordinary'])==14 and len(ordinary['named'])==1
result=dict(status='passed',archive_members=980,source_files=8194,source_drift=0,package_checks=106,saved_material_calls=4,saved_metadata_calls=1,public_points_each=401,ordinary_cases=14,named_cases=1,delta=delta,scope='Actual local package/source/archive and saved public replay evidence; no reviewer engine/build/browser call or live delivery claim')
(H/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
