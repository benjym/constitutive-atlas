"""Independent SQLite approval-interface review; temporary databases only."""
import argparse,copy,hashlib,importlib.util,io,json,sqlite3,tempfile,unittest
from pathlib import Path
from contextlib import closing
from atlas import research
from atlas.agent_review import approval_entry
from atlas.dsl import ValidationError

def require(value,message):
 if not value:raise AssertionError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();root=research.ROOT;require(sha(root/'atlas/research.py')=='279f5564d9484514f9d66db9b8a5fa4482dc534a6c9d4954b0e10001ad7b2c0a','reviewed exporter changed');require(sha(root/'tests/test_database_approval_integrity.py')=='aad4d04913a806e48cbb33160d7e7e5d9e78d83a92a35ba11df3b2d6933d43a1','reviewed tests changed');packet=root/'docs/reviews/database-approval-integrity-v1';checks=[]
 def mark(i,d):checks.append({'id':i,'result':'pass','detail':d})
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in ['tests.test_database_approval_integrity','tests.test_approved_export']);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);require(result.wasSuccessful(),'focused tests failed: '+stream.getvalue());mark('focused_tests',{'tests':result.testsRun,'skipped':len(result.skipped)})
 spec=importlib.util.spec_from_file_location('db_approval_probe_fixture',root/'tests/test_database_approval_integrity.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);negative=[]
 for variant in ['change_kind','remove_kind','remove_review']:
  fixture=module.DatabaseApprovalIntegrity();fixture.setUp()
  try:
   altered=copy.deepcopy(fixture.approval);altered['scope']={'use':'Independent synthetic forged broader scope'}
   if variant=='change_kind':altered['review']['kind']='other-review'
   elif variant=='remove_kind':altered['review'].pop('kind')
   else:altered.pop('review')
   fixture.write(fixture.registry_path,{'models':[altered]})
   try:fixture.export()
   except ValidationError as exc:negative.append({'variant':variant,'rejected':True,'reason':str(exc)})
   else:raise AssertionError('agent-authority discriminator bypass accepted')
  finally:fixture.doCleanups()
 mark('independent_discriminator_probes',negative)
 before=json.loads((packet/'before.json').read_text());repair=json.loads((packet/'archive-repair.json').read_text());require(sha(root/before['archive'])==before['sha256'],'old source archive');require(sha(root/repair['archive'])==repair['source_sha256'],'old checklist');require(sha(root/repair['prior_working_map_archive'])==repair['prior_working_map_sha256'],'old dirty-map snapshot');old=json.loads((root/repair['prior_working_map_archive']).read_text());mapping=json.loads((root/'catalogue/agent-reviews/source-archive-map.json').read_text());require(all(e in mapping['entries'] for e in old['entries']),'prior entries lost');require(all(mapping['documents'].get(n)==h for n,h in old['documents'].items()),'prior documents lost')
 for name in repair['documents']:require(mapping['documents'][name]==sha(root/name),'exact added review binding')
 owned={'original_path':repair['source_path'],'sha256':repair['source_sha256'],'archived_path':repair['archive']};require(owned in mapping['entries'],'own checklist archive entry');mark('archive_preservation',{'old_source':before['sha256'],'old_checklist':repair['source_sha256'],'all_prior_dirty_map_entries_and_documents_preserved':True,'owned_projection':{'documents':{n:mapping['documents'][n] for n in repair['documents']},'entries':[owned]},'other_working_entries_not_approved_for_staging':True})
 # This observes current shared checkout state, not a scientific or release approval.
 registry=json.loads((root/'catalogue/approved-models.json').read_text());approved=[a for a in registry['models'] if a.get('status')=='approved'];ordinary={m['id'] for m in research.all_models()}
 with tempfile.TemporaryDirectory(prefix='db-approval-review-') as d:
  database=Path(d)/'atlas.sqlite';research.export_database(database)
  with closing(sqlite3.connect(database)) as connection:
   actual=[json.loads(r[0]) for r in connection.execute('select record_json from model_approvals')];reviews=[json.loads(r[0]) for r in connection.execute('select record_json from agent_reviews')];require({a['id'] for a in actual}=={a['id'] for a in approved},'approval membership');require({r[0] for r in connection.execute('select id from models where executable=1')}==ordinary,'ordinary membership')
   byid={a['id']:a for a in actual}
   for a in approved:require(byid[a['id']]==a,'registry record JSON equality')
   agent=[a for a in approved if a.get('review',{}).get('kind')=='agent-model-review'];require(len(reviews)==len({a['review']['path'] for a in agent}),'agent review count')
   for a in agent:
    expected=approval_entry(root/a['review']['path'],root=root);require(all(a.get(k)==v for k,v in expected.items()),'canonical fields');record=json.loads((root/a['review']['path']).read_text());require(record in reviews,'exact review JSON')
   legacy=[a for a in approved if a.get('approval_authority',{}).get('kind')=='explicit-user-instruction'];require(all(byid[a['id']]==a for a in legacy),'non-agent authority retained');saved='\n'.join(connection.iterdump())
  research.export_database(database)
  with closing(sqlite3.connect(database)) as connection:require('\n'.join(connection.iterdump())==saved,'idempotent real export')
 mark('current_working_database',{'ordinary_executable_definitions':len(ordinary),'approved_records':len(approved),'agent_reviews':len(agent),'distinct_user_authority_records':len(legacy),'exact_records_and_generated_fields':True,'idempotent':True,'working_registry_sha256':sha(root/'catalogue/approved-models.json'),'working_source_map_sha256':sha(root/'catalogue/agent-reviews/source-archive-map.json'),'not_staged_or_release_proof':True})
 output={'id':'REVIEW-database-approval-integrity-v1','checks':checks,'test_log':stream.getvalue(),'source_sha256':sha(root/'atlas/research.py'),'tests_sha256':sha(root/'tests/test_database_approval_integrity.py'),'new_builds':0,'new_material_calls':0,'new_fits':0};args.output.write_text(json.dumps(output,indent=2)+'\n');print('PASS',len(checks),'independent review groups;',result.testsRun,'tests')
if __name__=='__main__':main()
