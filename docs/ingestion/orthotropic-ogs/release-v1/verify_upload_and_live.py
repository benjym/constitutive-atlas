"""Coordinator-only exact tested-upload/live byte audit; no constitutive calls."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,time,urllib.request,urllib.parse,sqlite3
MID='orthotropic-linear-elastic-ogs';SHA='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14';COMMIT='462a450c69b0fd481fc99b67e8c42f03f82e0e97';RUN=41341461226
h=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--upload',type=Path,required=True);p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();site=a.upload
 inventory={str(f.relative_to(site)):h(f.read_bytes()) for f in sorted(site.rglob('*')) if f.is_file()};a.output.mkdir(parents=True,exist_ok=True)
 (a.output/'upload-inventory.json').write_text(json.dumps({'commit':COMMIT,'run':RUN,'files':inventory},indent=2)+'\n')
 required=['index.html','app.js','atlas.js','atlas.wasm','models.json','catalogue.json','atlas.sqlite','orthotropic-contract.mjs','orthotropic-laboratory.mjs','docs/models/'+MID+'.md','docs/models/'+MID+'.md.html']
 manifest=json.loads((site/'material-point-orthotropic/package-manifest.json').read_text());required+=list(manifest)+['material-point-orthotropic/package-manifest.json'];assert all(x in inventory for x in required)
 assert all(inventory[f]==v for f,v in manifest.items());assert inventory['material-point-orthotropic/model.json']==SHA
 assert inventory['material-point-orthotropic/approval.json']=='3cb73256ceea7dcdb592275a40cd0685cd2dc6f0c8fc49eb2288f92348d89b79'
 assert inventory['material-point-orthotropic/review.json']=='a2862129dd393f2c73923b06706e12b75767f8b360b57bd1cfbb67c6069ef50f'
 model=json.loads((site/'material-point-orthotropic/model.json').read_text());approval=json.loads((site/'material-point-orthotropic/approval.json').read_text());review=json.loads((site/'material-point-orthotropic/review.json').read_text());assert approval['definition']['sha256']==SHA and review['model']['sha256']==SHA
 ordinary=json.loads((site/'models.json').read_text());assert len(ordinary['models'])==14;catalogue=json.loads((site/'catalogue.json').read_text());catalogue=catalogue.get('models',[]) if isinstance(catalogue,dict) else catalogue;assert sum(x['id']==MID for x in catalogue)==1
 db=sqlite3.connect(site/'atlas.sqlite');db.row_factory=sqlite3.Row
 row=dict(db.execute('select * from models where id=?',(MID,)).fetchone());assert json.loads(row['definition_json'])==model
 row=dict(db.execute('select * from model_approvals where model_id=?',(MID,)).fetchone());assert json.loads(row['record_json'])==approval and row['definition_sha256']==SHA
 row=dict(db.execute('select * from agent_reviews where model_id=?',(MID,)).fetchone());assert json.loads(row['record_json'])==review
 src=[dict(x) for x in db.execute('select * from sources where model_id=?',(MID,))];assert len({json.dumps(x,sort_keys=True) for x in src})==3;assert not list(db.execute('pragma foreign_key_check'))
 selected=sorted(set(required)|{f for f in inventory if ('/' not in f and not f.startswith('.')) or f.startswith(('engine-','material-point-j2/'))})
 nonce=str(time.time_ns())
 def fetch(f):
  url=a.url.rstrip('/')+'/'+urllib.parse.quote(f,safe='/')+'?orthotropic_release='+COMMIT+'&proof='+nonce
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-verification'}),timeout=45) as r:b=r.read();status=r.status
   return {'path':f,'url':url,'status':status,'expected_sha256':inventory[f],'actual_sha256':h(b),'size':len(b),'ok':status==200 and h(b)==inventory[f]}
  except Exception as e:return {'path':f,'url':url,'ok':False,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(fetch,selected))
 report={'commit':COMMIT,'run':RUN,'ok':all(x['ok'] for x in rows),'uploaded_files':len(inventory),'live_assets_compared':len(rows),'ordinary_models':len(ordinary['models']),'catalogue_models':len(catalogue),'exact_exported_model_approval_review':True,'source_rows':len(src),'unique_source_identities':3,'rows':rows}
 (a.output/'live-assets.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2));assert report['ok']
if __name__=='__main__':main()
