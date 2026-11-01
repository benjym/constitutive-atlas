"""Read-only SQL identity check against exact committed Git bytes, no production imports."""
import argparse,subprocess,json,hashlib,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('output',type=Path);p.add_argument('--commit',default='ecd1f3b12381dd8edec34fe6121b80a0bd5792aa');a=p.parse_args();assert not a.output.exists()
repo='/Users/bmar5496/code/constitutive-atlas'
blob=lambda name:subprocess.check_output(['git','-C',repo,'show',a.commit+':'+name]);obj=lambda name:json.loads(blob(name));sha=lambda b:hashlib.sha256(b).hexdigest()
reg=obj('catalogue/approved-models.json')['models'];manifest=obj('catalogue/manifest.json')['models'];c=sqlite3.connect('file:'+str((a.package/'atlas.sqlite').resolve())+'?mode=ro',uri=True)
assert c.execute('pragma integrity_check').fetchall()==[('ok',)] and not c.execute('pragma foreign_key_check').fetchall()
assert {k:json.loads(v) for k,v in c.execute('select id,record_json from model_approvals')}=={x['id']:x for x in reg}
expected_ids={x['id'] for x in manifest}|{x['model_id'] for x in reg};assert {x[0] for x in c.execute('select id from models')}==expected_ids
for x in reg:
 b=blob(x['definition']['path']);assert sha(b)==x['definition']['sha256'];row=c.execute('select definition_json from models where id=?',(x['model_id'],)).fetchone();assert json.loads(row[0])==json.loads(b)
expected_reviews={x['review']['path']:x['review']['sha256'] for x in reg if x.get('review',{}).get('kind')=='agent-model-review'}
actual=list(c.execute('select path,sha256,record_json from agent_reviews'));assert {x[0]:x[1] for x in actual}==expected_reviews
for path,h,record in actual:assert sha(blob(path))==h and json.loads(blob(path))==json.loads(record)
mid='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';approval=next(x for x in reg if x['model_id']==mid);model=obj(approval['definition']['path']);entry=next(x for x in manifest if x['id']==mid)
expected_sources={(x['url'],x['locator'],x['role']) for x in model['sources']+entry.get('catalogue_sources',[])};assert set(c.execute('select url,locator,role from sources where model_id=?',(mid,)))==expected_sources
assert json.loads((a.package/'catalogue.json').read_text())==obj('catalogue/manifest.json')
for name in ['web/model-profile-data.mjs','web/model-profiles.mjs','web/app.js']:assert (a.package/Path(name).name).read_bytes()==blob(name)
result={'identity':'independent-exact-git-upload-database-v1','passed':True,'application_commit':a.commit,'models':len(expected_ids),'discovery':len(manifest),'exact_approvals':len(reg),'exact_reviews':len(actual),'kelvin_source_rows':len(expected_sources),'committed_app_profile_assets_exact':True,'database_sha256':sha((a.package/'atlas.sqlite').read_bytes()),'network_or_compiled_calls':0}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
