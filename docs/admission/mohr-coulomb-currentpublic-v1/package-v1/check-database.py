from pathlib import Path
import sqlite3,json,hashlib
root=Path('/private/tmp/atlas-mc-admission-public-v1');site=Path('/private/tmp/atlas-mc-package-v1/site-v2');packet=Path('/Users/bmar5496/code/constitutive-atlas/docs/admission/mohr-coulomb-currentpublic-v1/package-v1')
c=sqlite3.connect((site/'atlas.sqlite').as_uri()+'?mode=ro',uri=True)
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
models={id:json.loads(text) for id,text in c.execute('SELECT id,definition_json FROM models WHERE definition_json IS NOT NULL')}
model=json.loads((root/'models/mohr-coulomb.json').read_text());assert models['mohr-coulomb']==model
registry=json.loads((root/'catalogue/approved-models.json').read_text())['models']
approvals={id:json.loads(text) for id,text in c.execute('SELECT id,record_json FROM model_approvals')}
assert len(approvals)==len(registry)==25
assert all(approvals[a['id']]==a for a in registry)
reviews={id:json.loads(text) for id,text in c.execute('SELECT id,record_json FROM agent_reviews')}
review=json.loads((root/'catalogue/agent-reviews/mohr-coulomb-agent-v1.json').read_text());assert reviews[review['id']]==review
before=json.loads((packet.parent/'registry-before.json').read_text())['models'];assert len(before)==24
assert all(approvals[a['id']]==a for a in before)
index=json.loads((site/'evidence.json').read_text());entry=next(x for x in index['agent_reviews'] if x['catalogue_id']=='mohr-coulomb')
assert entry['definition_current'] and entry['status']=='accepted' and entry['registered_approval_id'] in approvals
assert entry['definition_sha256']==hashlib.sha256((root/'models/mohr-coulomb.json').read_bytes()).hexdigest()
result={'status':'passed','scope':'Full packaged database and evidence exports only; complete builder/browser gates remain separate','sqlite_integrity':'ok','models':c.execute('SELECT COUNT(*) FROM models').fetchone()[0],'executable_definition_rows':len(models),'approvals':len(approvals),'agent_reviews':len(reviews),'all_prior_approval_records_preserved':len(before),'mc_definition_exact':True,'mc_review_exact':True,'mc_public_evidence_accepted_current_registered':True,'database_sha256':hashlib.sha256((site/'atlas.sqlite').read_bytes()).hexdigest(),'evidence_sha256':hashlib.sha256((site/'evidence.json').read_bytes()).hexdigest()}
(packet/'database-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
