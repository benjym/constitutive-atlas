"""Read-only integration audit. No exporter, material model, build or network calls."""
from pathlib import Path
from collections import Counter
import hashlib,json,sqlite3,subprocess,sys,tarfile
if not __debug__: raise RuntimeError('Do not disable required audit assertions')
R=Path(sys.argv[1]).resolve();E=Path(sys.argv[2]).resolve()
BASE='e32f8a86df44298f100394b34e084e313d48b195';REVIEW='5190673eb3991450b598f1d0bb0943e6995f605be8890f69d0dc536d9014d9ce';MODEL='6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_bytes())
git=lambda *a:subprocess.check_output(['git','-C',str(R),*a])
assert git('rev-parse','HEAD').decode().strip()==BASE
pinsfile=Path(__file__).with_name('source-pins.json')
if pinsfile.exists():
 pins=read(pinsfile)
 for label,folder in [('candidate',R),('saved_evidence',E)]:
  for name,digest in pins[label].items(): assert sha((folder/name).read_bytes())==digest,(label,name)
plan=read(E/'INSTALL.json');assert plan['base']==BASE and plan['review_sha256']==REVIEW
new=plan['new_files'];assert len(new)==16
tracked=git('diff','--name-only',BASE,'--').decode().splitlines();untracked=git('ls-files','--others','--exclude-standard').decode().splitlines()
assert tracked==['catalogue/approved-models.json'],tracked
assert set(untracked)==set(new),(set(untracked)^set(new))
for name,digest in new.items():
 p=R/name;assert p.is_file()and not p.is_symlink()and sha(p.read_bytes())==digest,name
 assert not p.read_bytes().startswith(b'%PDF-'),name
 assert not name.endswith('.pdf')
 assert subprocess.run(['git','-C',str(R),'cat-file','-e',BASE+':'+name],capture_output=True).returncode!=0,name
assert not (R/'.local/private-sources/mohr-coulomb/arxiv-1508.07435v3.pdf').exists()
reviewpath='catalogue/agent-reviews/mohr-coulomb-agent-v1.json';review=read(R/reviewpath)
assert sha((R/reviewpath).read_bytes())==REVIEW and review['status']=='accepted'
assert sha((R/'models/mohr-coulomb.json').read_bytes())==MODEL
beforebytes=git('show',BASE+':catalogue/approved-models.json');assert beforebytes==(E/'registry-before.json').read_bytes()
before=json.loads(beforebytes);after=read(R/'catalogue/approved-models.json');assert set(before)==set(after)
for k in before:
 if k!='models':assert before[k]==after[k],k
assert len(before['models'])==24 and len(after['models'])==25
assert before['models']==after['models'][:-1]
assert sha(beforebytes)==plan['registry_before_sha256']
assert sha((R/'catalogue/approved-models.json').read_bytes())==plan['registry_after_sha256']
sys.path.insert(0,str(R))
from atlas.agent_review import validate_review,approval_entry
from atlas.research import approved_definitions
_,approvals=approved_definitions();assert len(approvals)==25
expected=approval_entry(R/reviewpath,root=R)
assert after['models'][-1]==expected==read(E/'approval-entry.json')
assert expected['experimental_validation']=='not_assessed'and expected['deployment_authorized']is False
validated=[];oldscientific=[]
for a in approvals:
 if a.get('approval_authority',{}).get('kind')=='independent-agent-review':
  q=R/a['review']['path'];record=validate_review(q,root=R,for_approval=True)
  assert a==approval_entry(q,root=R)
  validated.append(record['model']['id'])
  if a['model_id']!='mohr-coulomb':
   for name in (a['review']['path'],a['definition']['path']):
    assert(R/name).read_bytes()==git('show',BASE+':'+name),name;oldscientific.append(name)
assert len(validated)==21 and len(oldscientific)==40
# Pin the frozen scientific inputs and each direct artifact without running the scientific checker.
inputs=read(R/'docs/reviews/mohr-coulomb-agent-v1/inputs.json')
for name,digest in inputs['files'].items():assert sha((R/name).read_bytes())==digest,name
for a in review['artifacts']:assert sha((R/a['path']).read_bytes())==a['sha256'],a['path']
assert len(review['artifacts'])==55
# Compare all saved database rows, with duplicate-aware multisets and no writes.
def tables(path):
 db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
 try:
  names=[x[0]for x in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
  return {n:Counter(db.execute('select * from "'+n+'"').fetchall())for n in names}
 finally:db.close()
bt,at=tables(E/'before/atlas.sqlite'),tables(E/'after/atlas.sqlite');assert set(bt)==set(at)and len(bt)==9
counts={}
for n in bt:
 assert not(bt[n]-at[n]),n
 plus=at[n]-bt[n];want=1 if n in ('model_approvals','agent_reviews')else 0
 assert sum(plus.values())==want,(n,len(plus))
 counts[n]={'before':sum(bt[n].values()),'after':sum(at[n].values()),'added_rows':want,'removed_rows':0}
assert counts['models']['before']==48 and counts['sources']['before']==202
for n,obj in [('model_approvals',expected),('agent_reviews',review)]:
 row=next(iter(at[n]-bt[n]));assert json.loads(row[-1])==obj,n
# Independently compare every saved evidence index section and exported file.
bi=read(E/'before/metadata/evidence.json');ai=read(E/'after/metadata/evidence.json');assert set(bi)==set(ai)
for k in bi:
 if k!='agent_reviews':assert bi[k]==ai[k],k
old={a['id']:a for a in bi['agent_reviews']};now={a['id']:a for a in ai['agent_reviews']}
assert len(old)==20 and len(now)==21 and all(now[k]==v for k,v in old.items())
added=next(v for k,v in now.items()if k not in old)
assert added['catalogue_id']=='mohr-coulomb'and added['definition_current']and added['record_sha256']==REVIEW
assert added['definition_sha256']==added['current_definition_sha256']==MODEL
assert added['registered_approval_id']==expected['id']
for k in ('status','scope','reviewer','limitations','blocking_findings','checklist'):
 assert added[k]==review[k],k
files=lambda d:{p.relative_to(d).as_posix():sha(p.read_bytes())for p in d.rglob('*')if p.is_file()}
bf,af=files(E/'before/metadata'),files(E/'after/metadata')
newexports=sorted(set(af)-set(bf));changedexports=sorted(n for n in bf if n in af and bf[n]!=af[n]);assert not(set(bf)-set(af))
assert newexports==['evidence-records/catalogue/agent-reviews/definitions/mohr-coulomb-agent-v1.json','evidence-records/catalogue/agent-reviews/mohr-coulomb-agent-v1.json']
assert changedexports==['evidence-records/catalogue/approved-models.json','evidence.json']
for export,source in [('evidence-records/'+reviewpath,reviewpath),('evidence-records/catalogue/agent-reviews/definitions/mohr-coulomb-agent-v1.json','models/mohr-coulomb.json'),('evidence-records/catalogue/approved-models.json','catalogue/approved-models.json')]:
 assert(E/'after/metadata'/export).read_bytes()==(R/source).read_bytes(),export
summary=read(E/'PROJECTION_CHECKS.json');assert summary['pass']and summary['tables']==counts
assert summary['metadata_files']=={'new':newexports,'changed':changedexports,'removed':[]}
# Read terminal output, preserving the original environment failure as a failure.
first=(E/'metadata-tests.log').read_text();retry=(E/'metadata-loopback-retry.log').read_text()
assert 'Ran 34 tests' in first and 'FAILED (errors=1)'in first and 'PermissionError: [Errno 1] Operation not permitted'in first
assert first.count('ERROR: ')==1 and "self.socket.bind(self.server_address)"in first
assert 'Ran 1 test' in retry and retry.rstrip().endswith('OK')
tests=read(E/'TESTS.json')
assert tests['initial']['exit_code']==1 and tests['initial']['tests']==34 and tests['initial']['passes']==33
assert tests['retry']['exit_code']==0 and tests['retry']['tests']==1 and tests['retry']['passes']==1
assert tests['initial']['log_sha256']==sha((E/'metadata-tests.log').read_bytes())
assert tests['retry']['log_sha256']==sha((E/'metadata-loopback-retry.log').read_bytes())
assert tests['source_change_during_tests'] is False
preserve=read(E/'PRESERVATION.json');assert preserve['source_files']==dict(new,**{'catalogue/approved-models.json':plan['registry_after_sha256']})
for key,folder in [('source_archive',R),('projection_archive',E)]:
 entry=preserve[key];f=E/entry['path'];assert sha(f.read_bytes())==entry['sha256']and f.stat().st_size==entry['bytes']
 with tarfile.open(f,'r:gz')as tar:
  names=tar.getnames();assert len(names)==len(set(names))==entry['files']
  assert all(tar.getmember(n).isfile()and not Path(n).is_absolute()and '..'not in Path(n).parts for n in names)
  if key=='source_archive':assert set(names)==set(new)|{'catalogue/approved-models.json'}
  else:assert set(names)=={str(f.relative_to(E))for side in ('before','after')for f in(E/side).rglob('*')if f.is_file()}
  for n in names:assert tar.extractfile(n).read()==(folder/n).read_bytes(),n
result={'passed':True,'reviewer_run':'/root/mc_scientific_review','task':'REVIEW-mohr-coulomb-integration-v1','base':BASE,'scientific_review_unchanged_sha256':REVIEW,'model_unchanged_sha256':MODEL,'tracked_delta':tracked,'new_files':new,'source_paths':17,'prior_approval_objects_preserved':24,'agent_reviews_validated':validated,'prior_review_and_definition_artifacts_exact':40,'frozen_scientific_input_hashes_exact':len(inputs['files']),'scientific_review_artifacts_bound':55,'tables':counts,'metadata_exports':{'new':newexports,'changed':changedexports,'removed':[]},'prior_evidence_index_sections_exact':True,'prior_agent_review_rows_exact':20,'test_disposition':'Initial33/34pass; sole socketbind error retained; exactcase retry terminal Ran1/OK. Parent reports exit1 then exit0.','private_pdf_added':False,'material_calls':0,'builds':0,'exporter_calls_during_review':0,'browser_or_network_calls':0,'scope':'Metadata integration only; no new scientific decision, model/runtime/web/CI edits or current release/experimental qualification.'}
print(json.dumps(result,indent=2,sort_keys=True))
