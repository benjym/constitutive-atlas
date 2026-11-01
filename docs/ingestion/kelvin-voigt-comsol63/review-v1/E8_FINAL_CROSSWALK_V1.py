"""Bind the current 57 requirements; preserve inherited independent decisions."""
import copy,hashlib,json
from pathlib import Path
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
SOURCE=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source')
P=Path('docs/ingestion/kelvin-voigt-comsol63');D=ROOT/P/'review-v1';R=SOURCE/P/'release-v3'
def pin(p):
 p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 prior=D/'CHECKLIST_CROSSWALK_V3.json';x=copy.deepcopy(json.loads(prior.read_text()))
 result=json.loads((D/'E8_FINAL_CHECK_V1.json').read_text())
 assert len(x['items'])==57 and pin(ROOT/'docs/MODEL_DELIVERY_CHECKLIST.md')['sha256']==x['checklist_sha256']
 assessments={
 'E8.1':'Exact final ecd1f3b1 application scope/source-only repair acceptance is retained in E8_ECD_PREPARATION_REVIEW_V1.md and E8_ECD_SOURCE_PRELIMINARY_V1.json. Exact Git SQL recheck binds committed app/profile, every approval/review, all approved definitions, catalogue and sources to actual upload.',
 'E8.2':'Recorded current-session publication authorization was already independently supported; no new permission inferred or requested.',
 'E8.3':'Final application ecd1f3b12381dd8edec34fe6121b80a0bd5792aa and workflow41357170257 are bound to terminal completed/success workflow evidence. Earlier failed workflow remains a separate retained identity.',
 'E8.4':'All six required terminal jobs pass, including both native platforms, both Wasm platforms, controlled-path and deployment. Four exact CI Kelvin raw datasets independently replay the unchanged assessor: 43 cases/86 calls/eight negative-recovery pairs per backend.',
 'E8.5':'Actual tested github-pages artifact13103773962 TAR and all1049 extracted bytes match the manifest. Complete live report requires exactly the same1049 paths, HTTP200 and actual/expected/upload hashes equal, including entry, engines, catalogue, source/review/approval and database.',
 'E8.6':'Live profile data/renderer/app bytes are included in the complete upload/live equality. Saved actual desktop/mobile profile shows behaviour-first content, closed technical section, Pa/Pa/s parameters, complete preparation, related Maxwell navigation and main-lab return; screenshots independently inspected.',
 'E8.7':'Saved actual public general-atlas laboratory run has exact fetched upload identity and all120 Cartesian state/stress values satisfy unchanged analytical gates; plots show held stress and finite creep, desktop/mobile layout and empty console. This reviewer independently assessed saved evidence and did not claim to operate the browser.',
 'E8.8':'Coordinator ledger records exact live URL, application revision, complete CI/deployment/upload/live/browser evidence and explicit exclusions. Administrative board closure remains coordinator-owned after this review handoff.'}
 pending=[]
 ledger=SOURCE/P/'DELIVERY.md';text=ledger.read_text()
 ledger_done=('- [X] E8' in text and result['application_commit'] in text and '41357170257' in text and 'https://benjym.github.io/constitutive-atlas/' in text)
 for item in x['items']:
  item['evidence_bindings']=[]
  for old in item['evidence']:
   relative=Path(old) if old.startswith('docs/') else P/old
   p=SOURCE/relative if (SOURCE/relative).exists() else ROOT/relative
   item['evidence_bindings'].append(pin(p))
  item['evidence_bindings'] += [dict(**pin(prior),locator=item['id']),pin(D/'FINAL_LOCAL_RELEASE_REVIEW_V1.md')]
  if item['id'].startswith('E8.'):
   item['assessment']=assessments[item['id']]
   item['evidence_bindings'] += [pin(D/'E8_FINAL_CHECK_V1.json'),pin(D/'E8_FINAL_DATABASE_CHECK_V1.json'),pin(R/'workflow.json'),pin(R/'tested-upload-manifest.json')]
   if (R/'live-assets.json').exists():item['evidence_bindings'].append(pin(R/'live-assets.json'))
   item['review_status']='supported' if result['E8_technical_acceptance'] or item['id'] in ['E8.1','E8.2','E8.3','E8.4','E8.7'] else 'pending'
   if item['id']=='E8.8':
    item['evidence_bindings'].append(pin(ledger))
    if not ledger_done:item['review_status']='pending';item['assessment']='Technical E8 evidence assessed separately; authoritative coordinator DELIVERY.md has not yet recorded final E8 completion/live URL. Parent must update and reviewer rebind before all57 closure.'
   if item['review_status']=='pending':pending.append(item['id'])
  else:item['decision_basis']='Carried accepted prior independent Kelvin review; no reauthored source/science decision by closeout reviewer.'
 x.update(identity='kelvin-independent-current57-final-E8-crosswalk-v1',reviewer='/root/maxwell_scientific_review',prior_reviewer='/root/kelvin_scientific_review',scope='Final E8 saved-evidence closeout for exact ecd1f3b1 application, inheriting accepted exact E0-E7 and bounded scientific review. No new experiment or unsupported host claim.',application_commit=result['application_commit'],workflow=41357170257,status_counts={'supported':57-len(pending),'pending':len(pending)},pending_items=pending,all57_supported=not pending)
 (D/'E8_FINAL_CURRENT57_CROSSWALK_V1.json').write_text(json.dumps(x,indent=2)+'\n')
 print(json.dumps({'all57_supported':not pending,'pending':pending}))
if __name__=='__main__':main()
