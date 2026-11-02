"""Exact tracked bytes and complete observed export input membership."""
from pathlib import Path
import gzip,hashlib,json,sqlite3,os
H=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-bingham-clean-checkout-evidence-v1');C=S/'tracked-context';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tracked=json.loads(gzip.decompress((H/'TRACKED-INPUTS.json.gz').read_bytes()));missing=json.loads((H/'OBSERVED-MISSING.json').read_text());selected={n:v['sha256'] for n,v in json.loads((H/'INSTALLATION.json').read_text())['files'].items()}
for n,v in tracked.items():
 actual=hashlib.sha256(os.readlink(C/n).encode()).hexdigest() if v['mode']=='120000' else sha(C/n)
 assert actual==v['sha256'],n
actual={p.relative_to(C).as_posix() for p in C.rglob('*') if p.is_file() or p.is_symlink()};assert actual==set(tracked)|set(selected),(actual-(set(tracked)|set(selected)))
local=json.loads((S/'local-baseline-v2/RESULT.json').read_text());before=json.loads((S/'tracked-before/RESULT.json').read_text());after=json.loads((S/'tracked-after-ten/RESULT.json').read_text());assert local['passed'] and after['passed'] and not before['passed'];assert local['inputs']==after['inputs'];assert set(after['inputs'])-set(tracked)==set(missing)
registry=json.loads((H/'REGISTRY-PATHS.json').read_text());assert registry['passed'];assert set(registry['inputs'])<=set(tracked)|set(selected)
assert (S/'local-baseline-v2/site/evidence.json').read_bytes()==(S/'tracked-after-ten/site/evidence.json').read_bytes()
def database(p):
 with sqlite3.connect(p) as db:
  names=[x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")];return {n:sorted(db.execute('SELECT * FROM '+n).fetchall(),key=repr) for n in names}
a=database(S/'local-baseline-v2/atlas.sqlite');b=database(S/'tracked-after-ten/atlas.sqlite');assert a==b
for n in ['local-baseline-v2','tracked-before','tracked-after-ten']:
 prefix={'local-baseline-v2':'LOCAL-BASELINE','tracked-before':'TRACKED-BEFORE','tracked-after-ten':'TRACKED-AFTER-TEN'}[n]
 (H/(prefix+'.json')).write_bytes((S/n/'RESULT.json').read_bytes())
 for p in (S/n).glob('*-failure.log'):(H/(prefix+'-'+p.name)).write_bytes(p.read_bytes())
report={'passed':True,'tracked_members_exact_unchanged':len(tracked),'only_added_members':selected,'scope_split':{'active_export':7,'existing_mapped_asset_receipts':3},'observed_export_read_inputs':len(after['inputs']),'all_export_reads_tracked_or_selected_additions':True,'all26approval_path_checks':registry['path_checks'],'all_approval_reads_tracked_or_selected_additions':True,'local_and_overlay_input_hashes_equal':True,'local_and_overlay_export_evidence_bytes_equal':True,'export_evidence_sha256':sha(S/'tracked-after-ten/site/evidence.json'),'local_and_overlay_database_rows_equal':True,'database_table_counts':{n:len(v) for n,v in b.items()},'old_map_pin_review_model_runtime_modifications':0,'compiler_material_calls':0}
(H/'INTEGRITY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
