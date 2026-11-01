#!/usr/bin/env python3
"""Read-only installed integrity review; temporary ordinary metadata projections only."""
import argparse,collections,hashlib,json,sqlite3,sys,tempfile,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('docs/admission/baseline-hypoplastic-install-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def need(v,m):
 if not v:raise ValueError(m)
def tables(p):
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as c:
  need(c.execute('pragma integrity_check').fetchall()==[('ok',)],'integrity')
  need(not c.execute('pragma foreign_key_check').fetchall(),'foreign keys')
  return {n:collections.Counter(c.execute('select * from '+n).fetchall()) for (n,) in c.execute("select name from sqlite_master where type='table'")}
def files(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}
def run(root):
 root=root.resolve();p=root/REL;m=load(HERE/'manifest.json')
 for group,base in [('inputs',root),('outputs',HERE)]:
  for n,h in m[group].items():need(sha(base/n)==h,'binding '+n)
 sys.path.insert(0,str(root))
 from atlas.evidence import checked_receipt
 from atlas.agent_review import approval_entry
 from atlas.research import export_database
 from tools.build_evidence import bundle
 journal=load(p/'APPLY_JOURNAL.json');prior=load(p/'independent-review/decision.json');ops=journal['operations']
 need(journal['status']=='installed-pass' and journal['apply'] and ops==prior['operations'],'journal/approved operations')
 need(journal['completed']==[o['path'] for o in ops] and len(ops)==9,'incomplete apply')
 need(journal['review']['sha256']==sha(p/'independent-review/decision.json'),'applied review identity')
 for o in ops:need(sha(root/o['path'])==o['after'],'installed bytes '+o['path'])
 freeze=load(p/'INSTALL_SOURCE_FREEZE.json')
 for n,h in freeze.items():need(sha(root/n)==h,'installer source '+n)
 plan=load(p/'PLAN.json')
 for r in plan['baseline']:
  need(sha(root/r['document'])==r['document_sha256'],'original immutable receipt')
 for r in plan['baseline']+plan['all_existing_candidate_map_bindings']:
  checked_receipt(root,r['document'],r['original_path'],r['old_sha256'])
 for r in plan['maps']:
  for d in r['document_pins']:need(sha(root/d['original_document'])==d['old_document_sha256'],'map document pin')
 entries=load(root/'docs/admission/baseline-hypoplastic-canonical-v1/approval-entries.json');reg=load(root/'catalogue/approved-models.json')
 need(len(reg['models'])==19,'registry membership')
 for e in entries:need(approval_entry(root/e['review']['path'],root=root)==e and reg['models'].count(e)==1,'actual path canonical entry')
 baseline=tables(p/'database-before.sqlite');after=tables(p/'database-after.sqlite');need(set(baseline)==set(after) and len(after)==9,'SQL table identity')
 delta={}
 for name in baseline:
  added=after[name]-baseline[name];removed=baseline[name]-after[name]
  need(not removed and sum(added.values())==(2 if name in ['agent_reviews','model_approvals'] else 0),'SQL multiset '+name)
  delta[name]={'before':sum(baseline[name].values()),'after':sum(after[name].values()),'added':sum(added.values()),'removed':sum(removed.values())}
 with tempfile.TemporaryDirectory(prefix='installed-review-') as td:
  td=Path(td);export_database(td/'fresh.sqlite');need(tables(td/'fresh.sqlite')==after,'fresh ordinary fullroot export differs')
  fresh=bundle(td/'evidence',root=root);need(files(td/'evidence')==files(p/'evidence-after'),'fresh normal evidence files differ')
  js="import fs from 'node:fs';import {validateEvidenceIndex} from './web/catalogue.mjs';const d=JSON.parse(fs.readFileSync(process.argv[1]));validateEvidenceIndex(d);console.log(d.agent_reviews.length);"
  proc=subprocess.run(['node','--input-type=module','-e',js,str(td/'evidence/evidence.json')],cwd=root,text=True,capture_output=True)
  need(proc.returncode==0 and proc.stdout.strip()=='15','full current source renderer schema')
 b=load(p/'evidence-before/evidence.json');a=load(p/'evidence-after/evidence.json')
 need(a['records']==b['records'] and a['reviews']==b['reviews'],'prior numerical/source projection')
 old={x['id']:x for x in b['agent_reviews']};new={x['id']:x for x in a['agent_reviews']}
 need(len(old)==13 and len(new)==15 and all(new[k]==v for k,v in old.items()),'prior agent projection')
 need(set(new)-set(old)=={load(root/e['review']['path'])['id'] for e in entries},'new agent identity')
 f0=files(p/'evidence-before');f1=files(p/'evidence-after');added=sorted(f1.keys()-f0.keys());removed=sorted(f0.keys()-f1.keys());changed=sorted(k for k in f0.keys()&f1.keys() if f0[k]!=f1[k])
 expected=sorted('evidence-records/'+e['review']['path'] for e in entries)+sorted('evidence-records/catalogue/agent-reviews/definitions/'+Path(e['review']['path']).name for e in entries)
 need(added==sorted(expected) and not removed and changed==['evidence-records/catalogue/approved-models.json','evidence.json'],'public allowlist delta')
 parent=load(p/'POST_INSTALL_CHECKS.json');need(parent['complete_current_database']==delta and parent['public_export_delta']==dict(added=added,removed=removed,changed=changed),'parent result differs')
 # Do not rerun 431MB historical reconstruction. Independently inspect all raw source pins,
 # redirect bytes, unchanged checker identity and original stdout/result/empty stderr.
 hist=load(p/'historical-package-result.json');out=load(p/'historical-package.stdout');baseline_hist=load(p/'independent-review/baseline-historical/historical-package.stdout')
 checker='docs/ingestion/lade-duncan-1975/fused-linear-v1/independent-review/actual-package-v2/check.py'
 need(sha(root/checker)==hist['checker_sha256']=='02f74cbe2738e4d15a79d63c71a69dcd7dac0920fbaf9122da6cec2569d4938e','old checker identity')
 need("for name,h in freeze['files'].items():assert sha(R/name)==h,name" in (root/checker).read_text(),'old checker direct pin semantics')
 source='docs/ingestion/lade-duncan-1975/atlas-integration-v1/actual-package-v2/EXECUTION_SOURCE_FREEZE.json'
 oldfreeze=load(root/source)['files'];drift=[];absolute=0
 for n,h in oldfreeze.items():
  q=Path(n)
  if q.is_absolute():absolute+=1
  else:q=root/n
  if sha(q)!=h:
   drift.append(n);need(sha(checked_receipt(root,source,n,h))==h,'historical exact redirect')
 need(len(oldfreeze)==8194 and absolute==33 and drift==['catalogue/approved-models.json'],'historical raw freeze drift')
 need(hist['returncode']==0 and hist['live_root_drift']==drift and len(hist['exact_archive_redirects'])==1,'historical result')
 need(hist['source_files']==8194 and hist['absolute_frozen_prerequisites']==33 and out==baseline_hist and out['status']=='passed','unchanged saved checker outcome')
 need((p/'historical-package.stderr').read_bytes()==b'','historical stderr')
 baseline_reviews=[]
 for name in ['linear-elastic-agent-v1','drucker-prager-agent-v1','mcc-agent-v1','vw96-agent-v1','igs97-agent-v1']:
  rpath='catalogue/agent-reviews/'+name+'.json';r=load(root/rpath);e=approval_entry(root/rpath,root=root)
  need(r['status']=='accepted' and not r['blocking_findings'] and reg['models'].count(e)==1,'baseline canonical approval')
  need(all(c['outcome']=='pass' for c in r['checklist']),'baseline checklist')
  need(r['reviewer']['run_id'] not in r['author_run_ids'] and r['reviewer']['run_id']!='/root','baseline reviewer independence')
  need(any(row['id']==r['id'] for row in a['agent_reviews']),'baseline normal projection')
  baseline_reviews.append({'id':r['id'],'checklist_items':len(r['checklist']),'reviewer_run_id':r['reviewer']['run_id']})
 return dict(status='PASS',operations=9,installer_source_bindings=len(freeze),preserved_resolver_checks=9,sql_multiset_delta=delta,public_export_delta=dict(added=added,removed=removed,changed=changed),unchanged_numerical_records=len(a['records']),unchanged_source_reviews=len(a['reviews']),unchanged_agent_reviews=13,new_agent_reviews=2,node_source_schema_rows=15,historical_source_pins=len(oldfreeze),historical_absolute_prerequisites=absolute,historical_registry_redirects=len(drift),historical_full_rerun_by_reviewer=False,historical_saved_stdout_identical=True,baseline_review_acceptance=baseline_reviews,m1_independent_review_requirement='satisfied for exact five accepted scopes; no broader numerical, experimental, current engine, UI or live qualification',builds=0,compiled_calls=0,material_calls=0)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();print(json.dumps(run(a.root),indent=2))
