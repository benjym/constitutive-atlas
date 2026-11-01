import argparse,hashlib,json,urllib.request,urllib.error,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--artifact',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args();root=a.artifact
manifest=json.loads((root/'material-point-hill/package-manifest.json').read_text());paths=set(manifest)|{'index.html','app.js','atlas.js','atlas.wasm','models.json','catalogue.json','atlas.sqlite','material-point-hill/package-manifest.json','laboratory-controller-router.mjs','docs/models/hill-abaqus2025.md','docs/models/hill-abaqus2025.md.html'}
base='https://benjym.github.io/constitutive-atlas/';rows=[];a.output.mkdir(parents=True,exist_ok=True)
for n in sorted(paths):
 expected=hashlib.sha256((root/n).read_bytes()).hexdigest();url=base+n+'?hill_release='+a.revision;req=urllib.request.Request(url,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-delivery-verification'})
 try:
  with urllib.request.urlopen(req,timeout=60)as r:b=r.read();status=r.status;headers={k:r.headers.get(k)for k in ['etag','last-modified','content-type']}
  actual=hashlib.sha256(b).hexdigest();row=dict(path=n,url=url,status=status,bytes=len(b),expected_sha256=expected,live_sha256=actual,exact=actual==expected,headers=headers)
 except Exception as e:row=dict(path=n,url=url,expected_sha256=expected,exact=False,error=str(e))
 rows.append(row);(a.output/'asset-comparison.json').write_text(json.dumps(dict(revision=a.revision,base_url=base,all_exact=all(x['exact']for x in rows),complete=len(rows)==len(paths),assets=rows),indent=2)+'\n');print(n,row['exact'],flush=True)
assert all(x['exact']for x in rows),'Live asset mismatch; retained report is not a pass'
print('LIVE',len(rows),'exact tested-upload assets')
