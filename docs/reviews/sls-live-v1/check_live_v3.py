"""Compare saved real-browser live exports and live hashes to exact CI artifact."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(Path(path).read_text())
def cli_result(path):
 text=Path(path).read_text();return json.loads(text.split('### Result\n',1)[1].split('\n### ',1)[0])
parser=argparse.ArgumentParser();parser.add_argument('artifact',type=Path);parser.add_argument('--deployment-proof',type=Path,required=True);args=parser.parse_args()
proof=read(args.deployment_proof)
assert proof['revision']=='f18db8e75d27cf182f2c03dfcd6534b7f51d5a86' and proof['status']=='success'
cases=read(ROOT/'docs/ingestion/sls-comsol63/execution-v1/cases.json')['cases'];comparisons=0
for name,caseid in [('browser-default','relax-schedule'),('browser-rate','load-hold-reverse')]:
 data=read(HERE/(name+'.json'));case=next(x for x in cases if x['id']==caseid)
 assert data['result']['ok'] and len(data['result']['points'])==6
 assert data['result']['catalogue_hash']==data['provenance']['catalogue_hash']
 for point in data['result']['points']:
  reference=next(x for x in case['references'] if x['time']==point['time'])
  assert len(point['state'])==12 and len(point['observables'])==6
  for i,(actual,expected) in enumerate(zip(point['state'],reference['state'])):
   assert abs(actual-expected)<=(3e-8 if i<6 else 1),(name,point['time'],i,actual,expected);comparisons+=1
  for actual,expected in zip(point['observables'],reference['stress']):
   assert abs(actual-expected)<=1,(name,point['time'],actual,expected);comparisons+=1
assets=cli_result(HERE/'browser-assets.log')['assets'];manifest=read(args.artifact/'engine-sls/package-manifest.json')
for item in assets:
 assert item['status']==200
 expected=hashlib.sha256((args.artifact/item['path']).read_bytes()).hexdigest()
 assert item['sha256']==expected,item['path']
 if item['path'] in manifest:assert expected==manifest[item['path']],item['path']
for path,expected in read(ROOT/'docs/reviews/sls-web-v1/implementation-freeze-v4.json').items():
 if path=='web/sls.html':assert hashlib.sha256((args.artifact/'sls.html').read_bytes()).hexdigest()==expected
result=dict(ok=True,revision=proof['revision'],browser_reference_comparisons=comparisons,ci_artifact_live_assets_equal=len(assets),deployment_proof=str(args.deployment_proof))
(HERE/'assessment-v3.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
