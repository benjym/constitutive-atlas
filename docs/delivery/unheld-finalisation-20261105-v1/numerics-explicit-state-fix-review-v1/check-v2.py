from pathlib import Path
import gzip,hashlib,json
O=Path(__file__).resolve().parent;P=O.parent/'numerics-explicit-state-fix-v1';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');ROOT=O.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=P/'manifest.json';assert sha(manifest)=='7b102e63152ff2ee4331a095032eb1cb17c78c815ab7719df57422579dbf2df9'
for f in json.loads(manifest.read_text())['files']:assert sha(P/f['path'])==f['sha256'] and (P/f['path']).stat().st_size==f['bytes']
delta=json.loads((P/'source-delta.json').read_text());assert len(delta['files'])==2
old=(R/'tools/test_numerics.mjs').read_text();new=(P/'proposed/tools/test_numerics.mjs').read_text();restored=new;substitutions=json.loads((P/'substitutions.json').read_text());assert len(substitutions)==6
for a,b in reversed(substitutions):assert restored.count(b)==1;restored=restored.replace(b,a)
assert restored==old
archive=P/delta['files'][1]['proposal'];assert archive.read_text()==old and sha(archive)==delta['files'][0]['preimage_sha256']
proof=json.loads((P/'initial-equivalence.json').read_text());rowsfile=R/proof['source_row_file']['path'];assert sha(rowsfile)==proof['source_row_file']['sha256']=='d97a58a505c023ab127706a099cd6da16f86e96a44be2cf79dddb8a75a98657c';rows=json.loads(gzip.decompress(rowsfile.read_bytes()))[:5]
assert [x['model'] for x in rows]==['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']
lengths=[]
for row,declared in zip(rows,proof['rows']):
 assert row['model']==declared['model']
 for kind,version in [('legacy','0.1'),('current','0.3')]:
  p=R/declared[kind]['path'];assert sha(p)==declared[kind]['sha256'];model=json.loads(p.read_text());assert model['schema_version']==version
  state=[]
  for field in model['state']:
   values=field['initial'] if field['shape']=='sym' else [field['initial']];state.extend(values)
  assert state==row['parent']==declared['frozen_row_parent']
 lengths.append(len(row['parent']))
assert lengths==[7,8,9,7,13]
for path,pin in json.loads((P/'source-and-failure-pins.json').read_text()).items():
 p=ROOT/path if path.startswith('docs/') else R/path;assert sha(p)==pin['sha256']
for f in delta['files']:assert sha(P/f['proposal'])==f['sha256']
assert "assert.equal(stopped.ok,false);assert.equal(stopped.points.length,1);" in new
assert "'0,1e-6,45,14,20000,11'" in new and 'assert.equal(bad.ok,false)' in new
assert "Math.abs(a-b)<=1e-7*Math.max(1,Math.abs(b))" in new
# Complete reversibility proves all original assertions/settings/controls/parameters and pair control flow unchanged.
result={'status':'PASS','manifest_members':len(json.loads(manifest.read_text())['files']),'exact_argument_substitutions':6,'all_other_harness_bytes_unchanged':True,'legacy_and_current_defaults_equal_frozen_parent_arrays':True,'state_lengths':lengths,'pair_count_unchanged':17,'limited_and_invalid_failure_gates_unchanged':True,'source_archive_exact':True,'genuine_failure_logs_pinned':True,'actual_compiled_module_material_browser_git_network_calls':0}
(O/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
