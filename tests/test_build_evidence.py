"""Temporary-root integrity/export tests; no numerical checker or executable."""
import copy,hashlib,json,pathlib,tempfile,unittest
from tools import build_evidence as b
class Export(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)/'repo';self.dest=pathlib.Path(self.tmp.name)/'site';self.root.mkdir();(self.root/'catalogue/evidence').mkdir(parents=True)
  self.write('catalogue/manifest.json',{'models':[{'id':'elastic','status':'transcribed'},{'id':'candidate','status':'candidate'}]});self.write('models/elastic.json',{'id':'elastic'});self.write('artifacts/a.json',{'value':1})
  self.record={'schema_version':'0.1','kind':'numerical-evidence','id':'elastic-old-v1','created_at':'2026-10-31','source_commit':'a'*40,'model':{'id':'elastic','definition_sha256':self.sha('models/elastic.json')},'executor':{'name':'synthetic','automated':True,'method':'analytical-closed-form','independent_review':False},'scope':'Retained failed bounded comparison','limitations':['Not scientific admission'],'outcome':'failed','artifacts':[{'path':'artifacts/a.json','sha256':self.sha('artifacts/a.json')}],'source_files':[{'path':'old/source.py','sha256':'b'*64}],'reproduction_command':'unused; not executed'}
  self.write('catalogue/evidence/old.json',self.record)
 def write(self,p,data):
  p=self.root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data)+'\n');return p
 def sha(self,p):return hashlib.sha256((self.root/p).read_bytes()).hexdigest()
 def export(self,bindings=()):return b.bundle(self.dest,self.root,bindings=bindings)
 def research(self):
  definition='models/research/candidate/model.json';self.write(definition,{'id':'candidate-research'});m={'version':'synthetic-v1','public_admission':False,'complete_model':False,'verified_scope':{'rates':3,'integration':False},'replay_policy':'No executable rerun','files':{definition:self.sha(definition)}};p='catalogue/investigations/research/manifest.json';self.write(p,m);return ('candidate',definition,'research'),m,p
 def test_repeat_bundle_is_deterministic_and_preserves_other_assets(self):
  self.dest.mkdir();(self.dest/'index.html').write_text('builder-owned')
  first=self.export();before={str(p.relative_to(self.dest)):p.read_bytes()for p in self.dest.rglob('*')if p.is_file()}
  self.assertEqual(first,self.export());self.assertEqual(before,{str(p.relative_to(self.dest)):p.read_bytes()for p in self.dest.rglob('*')if p.is_file()});self.assertEqual((self.dest/'index.html').read_text(),'builder-owned')
 def test_failed_record_retained_and_original_bytes_only(self):
  x=self.export();r=x['records'][0];self.assertEqual(r['outcome'],'failed');self.assertTrue(r['definition_current']);self.assertEqual(r['scope'],self.record['scope']);self.assertEqual(r['record_sha256'],self.sha('catalogue/evidence/old.json'));self.assertEqual((self.dest/'evidence-records/catalogue/evidence/old.json').read_bytes(),(self.root/'catalogue/evidence/old.json').read_bytes());self.assertFalse((self.dest/'artifacts').exists());self.assertFalse((self.dest/'evidence-records/artifacts').exists())
 def test_definition_change_not_historical_outcome_erasure(self):
  self.write('models/elastic.json',{'id':'elastic','changed':True});r=self.export()['records'][0];self.assertFalse(r['definition_current']);self.assertEqual(r['outcome'],'failed');self.assertNotEqual(r['definition_sha256'],r['current_definition_sha256'])
 def test_missing_historical_definition_noncurrent(self):
  (self.root/'models/elastic.json').unlink();r=self.export()['records'][0];self.assertFalse(r['definition_current']);self.assertIsNone(r['current_definition_sha256'])
 def test_corrupt_artifact_fails_before_destination_writes(self):
  self.dest.mkdir();(self.dest/'evidence.json').write_text('unchanged');self.write('artifacts/a.json',{'changed':True})
  with self.assertRaises(ValueError):self.export()
  self.assertEqual((self.dest/'evidence.json').read_text(),'unchanged');self.assertFalse((self.dest/'evidence-records').exists())
 def test_unknown_top_level_record_not_silently_omitted(self):
  self.write('catalogue/evidence/unknown.json',{'kind':'new-kind'})
  with self.assertRaises(ValueError):self.export()
 def test_research_outcome_not_inferred_scope_and_flags_preserved(self):
  binding,m,p=self.research();x=self.export((binding,));r=x['records'][1];self.assertEqual(r['catalogue_id'],'candidate');self.assertIsNone(r['outcome']);self.assertIs(r['admission_flags']['public_admission'],False);self.assertEqual(r['scope'],'');self.assertEqual(r['details']['verified_scope'],m['verified_scope']);self.assertEqual(r['limitations'],['No executable rerun']);self.assertEqual((self.dest/'evidence-records'/p).read_bytes(),(self.root/p).read_bytes())
 def test_unselected_manifests_explicitly_omitted(self):
  _,_,p=self.research();self.assertIn(p,self.export()['coverage']['omitted_investigation_manifests'])
 def test_missing_definition_pin_rejected(self):
  binding,m,p=self.research();m['files']={};self.write(p,m)
  with self.assertRaises(ValueError):self.export((binding,))
 def test_missing_canonical_binding_rejected(self):
  binding,_,_=self.research()
  with self.assertRaises(ValueError):self.export((('unknown',binding[1],binding[2]),))
 def test_conflicting_dependency_pin_rejected(self):
  binding,m,p=self.research();m['dependencies']={binding[1]:'c'*64};self.write(p,m)
  with self.assertRaises(ValueError):self.export((binding,))
 def test_archive_checked_current_definition_stays_separate(self):
  binding,m,p=self.research();definition=binding[1];expected=m['files'][definition];archive='catalogue/source-snapshots/'+expected+'/'+definition;raw=(self.root/definition).read_bytes();ap=self.root/archive;ap.parent.mkdir(parents=True);ap.write_bytes(raw);self.write(definition,{'id':'candidate-research','new':True});self.write('catalogue/investigations/research/source-archive-map.json',{'version':'immutable-source-archive-map-0.1','documents':{p:self.sha(p)},'entries':[{'original_path':definition,'sha256':expected,'archived_path':archive}]});r=self.export((binding,))['records'][1];self.assertFalse(r['definition_current']);self.assertEqual(r['definition_sha256'],expected);self.assertFalse((self.dest/'evidence-records/catalogue/source-snapshots').exists())
  ap.write_bytes(b'corrupt')
  with self.assertRaises(ValueError):self.export((binding,))
 def test_unsafe_definition_symlink_rejected(self):
  outside=pathlib.Path(self.tmp.name)/'outside.json';outside.write_text('{}');(self.root/'models/elastic.json').unlink();(self.root/'models/elastic.json').symlink_to(outside)
  with self.assertRaises(ValueError):self.export()
 def test_schema_invalid_record_rejected(self):
  bad=copy.deepcopy(self.record);bad['executor']['independent_review']=True;self.write('catalogue/evidence/old.json',bad)
  with self.assertRaises(ValueError):self.export()
 def review(self):
  self.write('docs/models/elastic.md',{'synthetic':'dossier'})
  record={'schema_version':'0.1','kind':'source-review','id':'elastic-review-v1','created_at':'2026-11-01','source_commit':'a'*40,'model':{'id':'elastic','definition_sha256':self.sha('models/elastic.json')},'status':'pending','independent':False,'dossier':'docs/models/elastic.md','evidence_ids':['elastic-old-v1'],'unresolved':['Independent scientific review pending.']}
  path='catalogue/reviews/elastic.json';self.write(path,record);return path,record
 def test_source_review_preserves_pending_questions_and_verbatim_receipt(self):
  path,review=self.review();x=self.export();self.assertEqual(len(x['records']),1);self.assertEqual(len(x['reviews']),1);item=x['reviews'][0]
  self.assertEqual(item['status'],'pending');self.assertFalse(item['independent']);self.assertIsNone(item['reviewer']);self.assertIsNone(item['reviewed_at']);self.assertEqual(item['unresolved'],review['unresolved']);self.assertEqual(item['evidence_ids'],review['evidence_ids']);self.assertTrue(item['definition_current'])
  self.assertEqual((self.dest/'evidence-records'/path).read_bytes(),(self.root/path).read_bytes());self.assertEqual((self.dest/review['dossier']).read_bytes(),(self.root/review['dossier']).read_bytes());self.assertTrue((self.dest/(review['dossier']+'.html')).is_file())
 def test_multiple_reviews_and_historical_acceptance_do_not_promote_current_definition(self):
  path,review=self.review();old=copy.deepcopy(review);old.update(id='elastic-review-old',status='accepted',independent=True,reviewer='Synthetic test fixture',reviewed_at='2026-10-30',unresolved=[]);old['model']['definition_sha256']='f'*64;self.write('catalogue/reviews/old.json',old)
  x=self.export();self.assertEqual(len(x['reviews']),2);accepted=next(v for v in x['reviews']if v['status']=='accepted');self.assertFalse(accepted['definition_current']);self.assertEqual(x['records'][0]['outcome'],'failed');self.assertEqual(json.loads((self.root/'catalogue/manifest.json').read_text())['models'][0]['status'],'transcribed')
 def test_unsigned_acceptance_and_unknown_review_model_fail_before_write(self):
  path,review=self.review();review.update(status='accepted',unresolved=[]);self.write(path,review)
  with self.assertRaises(ValueError):self.export()
  self.assertFalse(self.dest.exists())
  review.update(status='pending',unresolved=['Still pending']);review['model']['id']='absent';self.write(path,review)
  with self.assertRaises(ValueError):self.export()
  self.assertFalse(self.dest.exists())
 def test_review_definition_symlink_cannot_escape_repository(self):
  self.review();outside=pathlib.Path(self.tmp.name)/'outside.json';outside.write_text('{}');(self.root/'models/elastic.json').unlink();(self.root/'models/elastic.json').symlink_to(outside)
  with self.assertRaises(ValueError):self.export()


 def test_public_dossier_view_preserves_original_and_escapes_markup(self):
  _,review=self.review();raw=b'# Dossier <script>alert(1)</script>'
  (self.root/review['dossier']).write_bytes(raw);self.export()
  self.assertEqual((self.dest/review['dossier']).read_bytes(),raw)
  viewer=(self.dest/(review['dossier']+'.html')).read_text()
  self.assertNotIn('<script>',viewer);self.assertIn('&lt;script&gt;',viewer);self.assertIn('Download original Markdown',viewer)
 def test_invalid_dossier_encoding_rejects_before_destination_writes(self):
  _,review=self.review();(self.root/review['dossier']).write_bytes(b'\xff')
  with self.assertRaises(UnicodeDecodeError):self.export()
  self.assertFalse(self.dest.exists())
