"""Compare the exact tested Pages upload with the live ordinary Barodesy sand laboratory."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
MID='barodesy-sand'
MODEL='3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239'
REVIEW='df0e95028f38e4af94665ea8689d58b37a92d8c84b33f6aec4c503cbbd84efc6'
BASE='https://benjym.github.io/constitutive-atlas/'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);p.add_argument('output',type=Path);p.add_argument('--artifact-receipt',type=Path,required=True);p.add_argument('--artifact-tar',type=Path,required=True);a=p.parse_args();site=a.site.resolve()
 receipt=json.loads(a.artifact_receipt.read_text());assert receipt['run_id']==41362197554 and receipt['head_sha']=='a1f9bac74e1cf13b4934b13873e92b5e875ee422';assert sha(a.artifact_tar.read_bytes())==receipt['tar_sha256']
 manifest={str(p.relative_to(site)):sha(p.read_bytes()) for p in sorted(site.rglob('*')) if p.is_file()}
 assert manifest['models/'+MID+'.json']==MODEL
 rp='evidence-records/catalogue/agent-reviews/barodesy-sand-agent-v1.json';assert manifest[rp]==REVIEW
 rv=json.loads((site/rp).read_text());assert rv['status']=='accepted' and not rv['blocking_findings']
 approvals=json.loads((site/'evidence-records/catalogue/approved-models.json').read_text());assert any(x['model_id']==MID and x['definition']['sha256']==MODEL and x['review']['sha256']==REVIEW for x in approvals['models'])
 assert sha(json.dumps(manifest,sort_keys=True).encode())==receipt['extracted_manifest_sha256']
 cat=json.loads((site/'models.json').read_text());assert cat['sha256']=='29c12dec5d2ec9ce1ea84b8991757e4f03af1122a92095689c5b6f81b64c342f';assert next(x for x in cat['models'] if x['id']==MID)==json.loads((site/('models/'+MID+'.json')).read_text())
 names={'index.html','catalogue.json','models.json','atlas.sqlite','atlas-database.json','evidence.json','applicability.json','models/'+MID+'.json',rp,'evidence-records/catalogue/agent-reviews/definitions/barodesy-sand-agent-v1.json','evidence-records/catalogue/approved-models.json','docs/models/barodesy-sand-qualified-v1.md','docs/models/barodesy-sand-qualified-v1.md.html'}
 names.update(str(p.relative_to(site)) for pattern in ('*.js','*.mjs','*.css','*.wasm') for p in site.glob(pattern))
 def fetch(name):
  row={'path':name,'expected_sha256':manifest[name]}
  try:
   req=urllib.request.Request(BASE+name,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-audit'})
   with urllib.request.urlopen(req,timeout=45) as res:body=res.read();row.update(status=res.status,sha256=sha(body),bytes=len(body),headers={k:res.headers.get(k) for k in ('ETag','Last-Modified','Content-Type')})
   row['match']=row['status']==200 and row['sha256']==manifest[name]
  except Exception as exc:row.update(match=False,error=str(exc))
  return row
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,sorted(names)))
 report={'status':'passed' if all(x['match'] for x in rows) else 'failed','scope':'Exact CI-tested Pages upload versus live project-path assets; complete ordinary engine and Barodesy sand definition, primary-source links, review and approval identity (private source originals excluded)','artifact_receipt_sha256':sha(a.artifact_receipt.read_bytes()),'artifact_receipt':receipt,'base_url':BASE,'model_sha256':MODEL,'review_sha256':REVIEW,'catalogue_hash':cat['sha256'],'upload_files':manifest,'fetched':rows}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'upload_files':len(manifest),'compared':len(rows),'mismatches':[x['path'] for x in rows if not x['match']]}));assert report['status']=='passed'
if __name__=='__main__':main()
