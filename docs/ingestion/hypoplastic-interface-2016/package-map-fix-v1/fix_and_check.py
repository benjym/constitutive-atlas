"""Narrow sidecar document registration; isolated atomic writes; no execution/build."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');RELEASE=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2');OUT=Path(__file__).resolve().parent
PARENT='e6f734d5988d941776995bd48900c1a9b230fec2'
MAP='catalogue/agent-reviews/source-archive-map.json';REVIEW='catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json';PIN='13aa0f267736a9a5ad246e34461ead944fea5aa052ee74d2cec0ab3426a8ee0b'
def digest(b):return hashlib.sha256(b).hexdigest()
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);temporary=path.with_name(path.name+'.interface2016-document-registration')
 assert not temporary.exists();temporary.write_bytes(data);os.replace(temporary,path)
sys.path.insert(0,str(RELEASE));from atlas.evidence import checked_receipt
map_path=RELEASE/MAP;old=map_path.read_bytes();mapping=json.loads(old);assert mapping['version']=='immutable-source-archive-map-0.1';assert REVIEW not in mapping['documents']
assert digest((RELEASE/REVIEW).read_bytes())==PIN
committed=subprocess.check_output(['git','show',PARENT+':'+MAP],cwd=ROOT);assert old==committed
approval=next(a for a in json.loads((RELEASE/'catalogue/approved-models.json').read_text())['models'] if a['model_id']=='hvwe2016-reconciled-fixed-local');assert approval['review']['path']==REVIEW and approval['review']['sha256']==PIN
before=[]
for item in approval['supporting_files']:
 try:checked_receipt(RELEASE,REVIEW,item['path'],item['sha256'])
 except ValueError as e:before.append({'path':item['path'],'error':str(e)})
assert len(before)==97 and all(e['error']=='original evidence document changed after archival' for e in before)
archive='catalogue/source-snapshots/'+digest(old)+'/'+MAP;archived=RELEASE/archive
if archived.exists():assert archived.read_bytes()==old
else:atomic(archived,old)
new=json.loads(old);new['documents'][REVIEW]=PIN
assert new['entries']==mapping['entries'];assert {k:v for k,v in new['documents'].items() if k!=REVIEW}==mapping['documents']
atomic(map_path,(json.dumps(new,indent=2)+'\n').encode())
after=[]
for item in approval['supporting_files']:
 selected=checked_receipt(RELEASE,REVIEW,item['path'],item['sha256']);assert digest(selected.read_bytes())==item['sha256'];after.append({'path':item['path'],'sha256':item['sha256'],'resolved':selected.relative_to(RELEASE).as_posix()})
assert len(after)==97
report={'status':'passed-source-only-map-fix','parent':PARENT,'isolated_root':str(RELEASE),'map':MAP,'old_map_sha256':digest(old),'old_map_archive':archive,'new_map_sha256':digest(map_path.read_bytes()),'added_document':{REVIEW:PIN},'unchanged_existing_document_pins':len(mapping['documents']),'unchanged_archive_entries':len(mapping['entries']),'supporting_file_count':len(after),'before_failures':before,'after_verified':after,'candidate_review_approval_qualified_source_changed':False,'Git_mutations_build_material_browser_calls':0,'historical_package_failure':'Parent retained package-v1 run stdout/stderr and prospective package metadata; neither changed by this task.'}
(OUT/'check-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['before_failures','after_verified']},indent=2))
