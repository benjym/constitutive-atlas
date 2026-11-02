"""Freeze only the owned source/mock packet; no shared installation."""
from pathlib import Path
import difflib,gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-disclosure-fix-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda n,o:(H/n).write_text(json.dumps(o,indent=2)+'\n')
old=H/'before/web/app.js';new=H/'candidates/web/app.js';assert sha(R/'web/app.js')==sha(old)=='cc3c8bb8c871b0a27ebf2c2ed273d930abab18c765d2d3fce3832d3ce010a319'
# The isolated fixture used only prospective sources; keep it equal final bytes.
(C/'web/app.js').write_bytes(new.read_bytes())
(H/'consumer-context-inventory.json.gz').write_bytes(gzip.compress((json.dumps({'web/app.js':sha(new)},indent=2)+'\n').encode(),mtime=0))
(H/'app.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='before/web/app.js',tofile='candidate/web/app.js')))
mentions=json.loads(gzip.decompress((H/'binding-mentions.json.gz').read_bytes()));rows=[]
for n,v in mentions.items():
 if 'browser-disclosure-fix-v1' in n:reason='This new packet input; not a historical consumer.'
 elif v['excluded_by']:reason='Immutable preparation/candidate/copy namespace; source record and owned candidate bytes remain unchanged.'
 elif n.endswith('installation-v3/RECEIPT.json'):reason='Historical installed transition {before_sha256,sha256,candidate} nested under web/app.js; no recognized path→hash or {path,sha256} pair. Preserved unchanged.'
 else:reason='Absolute path pin to immutable preparation/private-context app copy, not live root-relative web/app.js. Those copies remain unchanged.'
 rows.append({'document':n,**v,'classification':reason})
package='docs/ingestion/bingham-comsol63/package-v3/SITE-MANIFEST.json';assert json.loads((R/package).read_text())['files']['app.js']==sha(old)
rows.append({'document':package,'sha256':sha(R/package),'excluded_by':[],'classification':'Supplementary independent review discovery after initial audit: immutable failed-site package inventory files/app.js uses packaged-site-relative app.js, not live root-relative web/app.js. Package bytes and manifest remain unchanged.'})
save('MENTION-CLASSIFICATION.json',{'preexisting_mentions_initial_audit':13,'supplementary_package_mention':1,'own_new_packet_mentions_initial_audit':1,'own_installation_record_created_later':1,'active_exact_root_relative_consumers':0,'mentions':rows,'scope':'All exact old-hash JSON mentions from catalogue/docs/tools/tests/schemas. Recursive reverse discovery has no seed consumers; therefore no affected sibling maps or reverse edges. Other old-hash archive consumers unchanged; no maps or historical files are proposed.'})
save('INSTALLATION.json',{'installed':False,'files':{'web/app.js':{'before_sha256':sha(old),'sha256':sha(new),'candidate':'candidates/web/app.js'}},'canonical_archive_required':False,'before_bytes_preserved':'before/web/app.js','requires_independent_review':True})
assert json.loads((H/'RENDER-CHECK.json').read_text())['passed'];s=json.loads((H/'SUMMARY.json').read_text());assert s['primary_edges']==s['affected_maps']==s['failures']==0
pins=['web/model-profile-data.mjs','web/bingham-laboratory.mjs','web/bingham-atlas-contract.mjs','web/model-profiles.mjs','catalogue/manifest.json','catalogue/approved-models.json','catalogue/agent-reviews/bingham-comsol63-agent-v1.json','docs/ingestion/bingham-comsol63/browser-v3/technical-disclosure.json']
save('SOURCE-BINDINGS.json',{'baseline_commit':'7f145f2df71e53178a98e1ec4ae7bf52795e8b9d','source_files':{n:sha(R/n) for n in pins},'candidate_changes_only':['web/app.js'],'build_or_browser_or_module_or_material_or_remote_calls':0})
files={p.relative_to(H).as_posix():sha(p) for p in H.rglob('*') if p.is_file() and p.name!='MANIFEST.json'};save('MANIFEST.json',{'identity':'bingham-browser-disclosure-fix-v1','status':'prospective-review-request','files':files,'installation_sha256':sha(H/'INSTALLATION.json'),'new_app_sha256':sha(new),'old_app_sha256':sha(old),'independent_acceptance_claimed':False});print(json.dumps({'manifest_sha256':sha(H/'MANIFEST.json'),'new_app_sha256':sha(new),'files':len(files)},indent=2))
