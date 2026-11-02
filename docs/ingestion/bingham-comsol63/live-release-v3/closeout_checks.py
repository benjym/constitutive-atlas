"""Require all retained release gates before closing E8."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
HEAD='43ea5c45f0e6112661fe996b685a3adcdac12ce6'
reports={n:json.loads((HERE/n).read_text()) for n in ['ALL-JOBS-CHECK.json','PAGES-DEPLOYMENT-CHECK.json','LIVE-UPLOAD-COMPARISON.json','LIVE-BROWSER-CHECKS.json','LIVE-DEFAULT-CHECK.json','UPLOAD-DATABASE-PRESERVATION.json']}
checks={n:d.get('passed',d.get('pass')) is True for n,d in reports.items()}
checks['current_source_in_all_revision_reports']=all(d['source_revision']==HEAD for d in reports.values() if 'source_revision' in d)
m=json.loads((HERE/'UPLOAD-MANIFEST.json').read_text());assert m['source_revision']==HEAD
pins={
 'app.js':'f7b09ec267f85ee67890da4090cd4cfbe423863457f8b68783ff5813174dd36d',
 'model-profile-data.mjs':'31ad08d2f3db9e04aca616c54879b33e87d06b09f6e49e40630b155c60ae6f6b',
 'engine-bingham/bingham.mjs':'22316dc4955e824fdd0eae33b3af01ed7ce3732717ac0230e6de06286f872e02',
 'engine-bingham/bingham.wasm':'586239f8c9c3b4ede5f359ccc3dd2844f4ab45d0440a52c5bb706a3e893ab368',
 'engine-bingham/models.json':'7e5bf7356a0f8b7860d5c0c43133c10d739debbc93905c5825db11ea3d06bdb6',
 'engine-bingham/review.json':'61022026949f2ce9b9a536ab564239edd97ac0b5b3ba66f4ffe3f0066aa6b836',
 'evidence-records/catalogue/agent-reviews/definitions/bingham-comsol63-agent-v1.json':'6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850',
 'evidence-records/catalogue/approved-models.json':'48d98b12b53048d6480ee97ca0962d778237089f979a068b0c0e50145f4935fd',
}
checks['qualified_engine_model_review_and_reader_bytes']=all(m['files'][n]['sha256']==h for n,h in pins.items())
for label in ['LINUX','MACOS']:
 d=json.loads((HERE/f'{label}-PAIRED-ARTIFACT.json').read_text())
 checks[label.lower()+'_current_paired_original_assessments']=d['source_revision']==HEAD and all(d['checks'].values()) and len(d['unchanged_post_receipts'])==5 and all(x['all_records_unchanged'] for x in d['unchanged_post_receipts'])
out={'kind':'bingham-e8-release-closeout-v1','source_revision':HEAD,'run_id':41388826742,'deployment_id':7485425155,'passed':all(checks.values()),'checks':checks,'qualified_public_pins':pins,'live_profile':'https://benjym.github.io/constitutive-atlas/index.html#catalogue/bingham-comsol63-mises-perfect-zero-spin-ode','limitations':'Bounded backward-Euler physical-time schedule API, fixed maximum step 5/12288 s, small strain and zero spin, constant positive yield/no hardening. No experimental validation or broad accuracy guarantee for custom histories.','prior_failures_retained':['live-release-v1/','live-release-v2/'],'reports':{n:{'sha256':hashlib.sha256((HERE/n).read_bytes()).hexdigest(),'passed':checks[n]} for n in reports}}
(HERE/'CLOSEOUT-CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['reports','qualified_public_pins']},indent=2));assert out['passed']
