from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent;root=here.parents[4];site=root/'.local/clay2013-current-delivery-v1/site'
plan=json.loads((here/'PLAN.json').read_bytes());manifest=json.loads((here.parent/'PACKAGE_MANIFEST.json').read_bytes())['files']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in plan['files'].items():
 if sha(here/name)!=h:raise ValueError('changed prospective checker/server input '+name)
for n,item in manifest.items():
 if sha(site/n)!=item['sha256']:raise ValueError('changed sealed package '+n)
rows=[json.loads(line) for line in (here/'responses.jsonl').read_text().splitlines()];selected={}
for n in plan['required_assets']:
 matches=[x for x in rows if x['relative_path']==n]
 if not matches:raise ValueError('missing actual browser fetch '+n)
 for x in matches:
  if not (x['path']==plan['url_prefix']+n and x['status']==200 and x['cache_control']=='no-store' and x['write_completed'] is True and x['write_returned_bytes']==x['body_bytes']==x['content_length']==manifest[n]['bytes'] and x['body_sha256']==manifest[n]['sha256'] and x['request_if_none_match'] is None and x['request_if_modified_since'] is None):raise ValueError('incomplete/mismatched delivery '+n)
  if not x['user_agent'] or 'Mozilla' not in x['user_agent']:raise ValueError('browser user agent absent')
 selected[n]=matches
export=json.loads((here/'export.json').read_bytes());supported=json.loads((here.parent/'supported-package.json').read_bytes());case=next(x for x in supported['ordinary'] if x['id']=='hypoplastic-clay-2013')
cat=json.loads((site/'models.json').read_bytes())
if not (export['catalogue_hash']==cat['sha256'] and export['specification']==case['specification'] and export['result']['ok'] and export['result']['points']==case['result']['points'] and len(export['result']['points'])==101):raise ValueError('actual browser run/catalogue/response identity')
print(json.dumps({'status':'pass','method':'Actual browser delivery via fresh nonce-prefix/ownorigin, no-store full200response transport writes, sealed package before/after and same-run exported result. Not browser-cache-body or CPU attestation.','origin':'http://127.0.0.1:'+str(plan['port']),'url_prefix':plan['url_prefix'],'package_files_unchanged':len(manifest),'required_deliveries':selected,'journal_sha256':sha(here/'responses.jsonl'),'export_sha256':sha(here/'export.json'),'catalogue_hash':cat['sha256'],'physical_points_exact_current_package':101},indent=2))
