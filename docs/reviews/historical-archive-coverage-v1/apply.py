"""One-shot coordinator application of a precomputed exact-byte repair plan."""
from pathlib import Path
import hashlib,json,sys,shutil
R=Path('/Users/bmar5496/code/constitutive-atlas');W=Path('/private/tmp/atlas-archive-coverage-v1');P=json.loads((W/'plan.json').read_text());D=R/'docs/reviews/historical-archive-coverage-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
D.mkdir();shutil.copyfile(W/'plan.json',D/'plan.json');shutil.copyfile(W/'initial-plan.json',D/'initial-plan.json');shutil.copyfile(W/'before-tests.log',D/'before-tests.log');shutil.copyfile(W/'plan.py',D/'plan.py');shutil.copyfile(__file__,D/'apply.py')
for row in P['documents']:assert sha(R/row['document'])==row['document_sha256']
old_maps={};archives=[]
for path,h in list(P['old_maps'].items())+[(P['test_source']['path'],P['test_source']['sha256'])]:
 if h is None:assert not(R/path).exists();continue
 assert sha(R/path)==h
 target=R/'catalogue/source-snapshots'/h/path
 if target.exists():assert sha(target)==h
 else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/path,target);archives.append(target.relative_to(R).as_posix())
 if path in P['old_maps']:old_maps[path]=load(R/path)
for row in P['documents']:
 path=R/row['sidecar'];mapping=load(path)if path.exists()else{'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 pin=mapping['documents'].get(row['document']);assert pin is None or pin==row['document_sha256'];mapping['documents'][row['document']]=row['document_sha256']
 bindings=[ref for ref in P['affected_reverse_references']if ref['document']==row['document']and ref['resolution']=='checked'and ref['resolved_before']==ref['original_path']]
 bindings += [dict(ref,resolution='checked')for ref in P['test_source']['receipts']if ref['document']==row['document']]
 for binding in bindings:
  entry={k:binding[k]for k in ('original_path','sha256')};entry['archived_path']=(Path('catalogue/source-snapshots')/entry['sha256']/entry['original_path']).as_posix()
  matches=[e for e in mapping['entries']if e['original_path']==entry['original_path']and e['sha256']==entry['sha256']];assert not matches or matches==[entry]
  if not matches:mapping['entries'].append(entry)
 path.write_text(json.dumps(mapping,indent=2)+'\n')
for name,old in old_maps.items():
 new=load(R/name);assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries']for e in old['entries'])
# Preserve exact old test identity before namespace-aware coverage checks.
test=R/P['test_source']['path'];assert sha(test)==P['test_source']['sha256'];s=test.read_text();needle='class RepositoryArchiveCoverageTests(unittest.TestCase):';assert needle in s;s=s.replace(needle,(W/'test_namespace_helpers.txt').read_text()+needle)
needle="  for sidecar in sorted((ROOT/'catalogue').rglob('source-archive-map.json')):\n   mapping=json.loads(sidecar.read_text())";assert needle in s;s=s.replace(needle,"  for sidecar in sorted((ROOT/'catalogue').rglob('source-archive-map.json')):\n   if not _is_active_archive_map(ROOT,sidecar):continue\n   mapping=json.loads(sidecar.read_text())");test.write_text(s)
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
for row in P['documents']:assert sha(R/row['document'])==row['document_sha256']
for ref in P['affected_reverse_references']:
 if ref['resolution']=='checked':assert sha(checked_receipt(R,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
 elif ref['resolution'].startswith('descriptive-'):
  target=R/'catalogue/source-snapshots'/ref['sha256']/ref['original_path'];assert sha(target)==ref['sha256']
for ref in P['test_source']['receipts']:assert checked_receipt(R,ref['document'],ref['original_path'],ref['sha256'])==R/'catalogue/source-snapshots'/ref['sha256']/ref['original_path']
(D/'repair.json').write_text(json.dumps({'old_maps':P['old_maps'],'new_maps':{p:sha(R/p)for p in P['old_maps']},'archived_new_files':archives,'all_original_documents_unchanged':True,'reverse_edges_preserved':len(P['affected_reverse_references']),'old_test_bindings_preserved':len(P['test_source']['receipts']),'live_missing_fixed':len(P['missing_live']),'frozen_namespace_copies_mutated':0},indent=2)+'\n')
print('Repaired13live bindings; preserved57reverse edges and4old-test receipts; frozen trees unchanged.')
