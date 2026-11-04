from pathlib import Path
import json,hashlib,ast
Q=Path(__file__).resolve().parent;N=Q.parent;O=N/'current17-source-witness-v1';S=O/'source';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
rev='64002531f0af5c06ad0402d0d80548102f8e6a38';bindings={}
for name in ('first-source-bindings.json','source-bindings-v2.json','reuse-source-bindings-v1.json'):
 d=json.loads((O/name).read_text());ok(d['revision']==rev,'exact shared revision '+name)
 for row in d['files']:
  p=Path(row['witness']);ok(H(p)==row['sha256'],'exact supplied blob '+row['path']);bindings[row['path']]=row
report=json.loads((N/'python-fixture-release-v1/concurrent-reuse-comparison.json').read_text());ok(report['revision']==rev,'comparison exact shared revision')
for row in report['source_paths']:
 ok(H(S/row['path'])==row['current_main_sha256'],'independently rehash42 source reuse '+row['path'])
 before=N/'python-historical-contexts-fix-v2/proposed'/row['path']
 if not before.exists():before=N/'python-explicit-fixtures-fix-v1/proposed'/row['path']
 ok(H(before)==row['reviewed_sha256'],'exact previously approved candidate '+row['path'])
 ok(row['exact']==(row['current_main_sha256']==row['reviewed_sha256']),'truthful exact flag '+row['path'])
ok(len(report['source_paths'])==42 and sum(r['exact']for r in report['source_paths'])==39,'exact39of42 unchanged')
for row in report['five_definitions_and_accepted_reviews']:
 ok(H(S/row['path'])==row['sha256'] and row['exact_702'],'all10 baseline definition/E5 witness hashes exact')
# Reversibly map two current17 test changes to B2; every other assertion/expression unchanged.
for n in ('tests/test_controlled_time.py','tests/test_historical_generation.py'):
 after=(S/n).read_text().replace('tests/contexts/current-seventeen-md1997-baseline-v1.json','docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/current-sixteen-baseline-v03-v1.json').replace('current-seventeen-md1997-baseline-v1','current-sixteen-baseline-v03-v1').replace('self.assertEqual(len(paths),17)','self.assertEqual(len(paths),16)').replace('self.assertEqual(len(current_paths), 17)','self.assertEqual(len(current_paths), 16)').replace("header.count(',StressScope::effective'), 15","header.count(',StressScope::effective'), 14")
 ok(after==(N/'python-historical-contexts-fix-v2/proposed'/n).read_text(),'exact whole test reversal '+n)
old=json.loads((N/'python-historical-contexts-fix-v2/proposed/catalogue/agent-reviews/source-archive-map.json').read_text());new=json.loads((S/'catalogue/agent-reviews/source-archive-map.json').read_text());ok(old['documents']==new['documents'],'all immutable agent-review document pins unchanged')
added=[e for e in new['entries']if e not in old['entries']];ok(all(e in new['entries']for e in old['entries'])and len(new['entries'])==len(old['entries'])+1,'source map exact one-entry additive union')
ok(added==[{'original_path':'cpp/include/atlas/solver.hpp','sha256':'b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e','archived_path':'catalogue/source-snapshots/b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e/cpp/include/atlas/solver.hpp'}],'precise old solver archival route only')
# Verify strict context17 covers all original16 plus newMD; full metadata literal equivalence.
context=json.loads((S/'tests/contexts/current-seventeen-md1997-baseline-v1.json').read_text());baseline=json.loads((N/'python-historical-contexts-fix-v2/proposed/docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/current-sixteen-baseline-v03-v1.json').read_text());ok(len(context['models'])==17 and all(x in context['models']for x in baseline['models']),'strict17 preserves all16 exact member hashes')
ok([x['path']for x in context['models']if x not in baseline['models']]==['models/manzari-dafalias-1997-constant-m-be-v1.json'],'only newMD context member')
metadata=json.loads((S/context['catalogue']['path']).read_text());ok(H(S/context['catalogue']['path'])==context['catalogue']['sha256'],'new17 metadata exact byte pin')
oldmodels=json.loads((N/'python-historical-contexts-fix-v2/proposed/docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2/current-sixteen-baseline-v03-v1.models.json').read_text())['models'];ok(len(metadata['models'])==17 and [x for x in metadata['models']if x['id']!='manzari-dafalias-1997-constant-m-be-v1']==oldmodels,'all16 old metadata literal objects unchanged')
# Every original9 example specification must stay exact despite input-only transport.
index=json.loads((S/'catalogue/laboratory-examples.json').read_text());ok(len(index['examples'])>=9,'published example index includes original9')
oldindex=json.loads((N/'nine-example-proposal-v1/catalogue/laboratory-examples.json').read_text())if(N/'nine-example-proposal-v1/catalogue/laboratory-examples.json').exists()else None
for p in sorted((N/'nine-example-proposal-v1/protocols').glob('*.json')):
 original=json.loads(p.read_text());spec=original['specification'];matching=[e for e in index['examples']if e['model']==spec['model'] and (S/e['document_path']).exists()and json.loads((S/e['document_path']).read_text()).get('specification')==spec]
 ok(len(matching)==1,'exact original9 specification including integration settings '+p.name)
 e=matching[0];doc=S/e['document_path'];x=json.loads(doc.read_text());ok(x['schema_version']=='atlas-laboratory-example-input-0.1'and H(doc)==e['document_sha256']and x['definition_sha256']==e['definition_sha256'],'explicit input document binds new transport and unchanged definition '+p.name)
(Q/'source-checks.json').write_text(json.dumps({'status':'PASS_SOURCE_SCOPE_ONLY','checks':len(labels),'labels':labels,'revision':rev,'added_map_entry':added},indent=2)+'\n');print(json.dumps({'status':'PASS_SOURCE_SCOPE_ONLY','checks':len(labels)}))
