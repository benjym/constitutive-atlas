"""Compare the delivered NorSand assets with the exact Actions Pages upload."""
import argparse,hashlib,json,urllib.request
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 site=a.site.resolve();identity=json.loads((site/'engine-path/identity.json').read_text());base='https://benjym.github.io/constitutive-atlas/'
 assert identity['model']=='norsand-jefferies-1993-active-axial'
 assert identity['definition_sha256']=='67ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c'
 assert identity['files']['review.json']=='9cfe9b7d58632c5dbc3099fb6debe40a8fdcea47ae66b7077a5e60bf8bebf6b7'
 declared={**{'engine-path/'+n:h for n,h in identity['files'].items()},**identity['components']}
 manifest={str(p.relative_to(site)):sha(p.read_bytes()) for p in sorted(site.rglob('*')) if p.is_file()}
 for name,h in declared.items(): assert manifest[name]==h,(name,'upload declaration')
 selected=set(declared)|{'engine-path/identity.json','index.html','app.js','catalogue.json','atlas.sqlite','atlas-database.json'}
 selected.update(str(p.relative_to(site)) for p in site.glob('*.css'))
 rows=[]
 for name in sorted(selected):
  req=urllib.request.Request(base+name,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-audit'})
  with urllib.request.urlopen(req,timeout=60) as res:
   payload=res.read(); status=res.status;headers={k:res.headers.get(k) for k in ('ETag','Last-Modified','Content-Type','Content-Length')}
  h=sha(payload);assert status==200 and h==manifest[name],(name,status,h,manifest[name]);rows.append({'path':name,'status':status,'sha256':h,'bytes':len(payload),'headers':headers})
 out={'result':'PASS','scope':'Actual tested upload versus live project-path assets; exact model and accepted review','base_url':base,'identity':identity,'upload_files':manifest,'fetched':rows}
 a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'result':'PASS','upload_files':len(manifest),'fetched':len(rows)}))
if __name__=='__main__':main()
