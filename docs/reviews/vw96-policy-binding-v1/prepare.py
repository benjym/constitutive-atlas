from pathlib import Path
import json,hashlib,shutil,sys
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root))
from atlas.agent_review import validate_review
sha=lambda b:hashlib.sha256(b).hexdigest()
p=Path('/private/tmp/atlas-vw96-policy-binding-v1');p.mkdir(exist_ok=False)
name='catalogue/agent-reviews/vw96-agent-v1.json';review=json.loads((root/name).read_text());policy=Path('/private/tmp/vw96-exact-AGENTS.md').read_bytes();h=sha(policy)
assert h=='af554aa5c12e4f3706efdf20399a283e7a09bda8be748b1f394b4d0c78c3709e'
assert sha(Path('/private/tmp/atlas-clay2013-release-v5/AGENTS.md').read_bytes())==h
mapname='catalogue/agent-reviews/source-archive-map.json';old=(root/mapname).read_bytes();m=json.loads(old);before=json.loads(old)
assert name not in m['documents'];m['documents'][name]=sha((root/name).read_bytes())
entry={'original_path':'AGENTS.md','sha256':h,'archived_path':f'catalogue/source-snapshots/{h}/AGENTS.md'}
assert not any(x['original_path']=='AGENTS.md' and x['sha256']==h for x in m['entries']);m['entries'].append(entry)
assert all(m['documents'][k]==v for k,v in before['documents'].items())
assert m['entries'][:-1]==before['entries']
proposed=(json.dumps(m,indent=2)+'\n').encode();(p/'proposed-source-archive-map.json').write_bytes(proposed);(p/'map-before.json').write_bytes(old)
isolated=p/'isolated';isolated.mkdir()
for rel in [name,review['model']['path']]+[x['path'] for x in review['artifacts']]:
 target=isolated/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/rel).read_bytes())
mp=isolated/mapname;mp.parent.mkdir(parents=True,exist_ok=True);mp.write_bytes(proposed)
a=isolated/entry['archived_path'];a.parent.mkdir(parents=True,exist_ok=True);a.write_bytes(policy)
validate_review(isolated/name,root=isolated,for_approval=True)
negative=[]
a.write_bytes(policy+b'\n')
try:validate_review(isolated/name,root=isolated,for_approval=True)
except Exception as e:negative.append({'case':'corrupt_exact_policy_archive','rejected':True,'error':str(e)})
else:raise AssertionError('Corrupt archive accepted')
a.write_bytes(policy)
rp=isolated/name;original=rp.read_bytes();rp.write_bytes(original+b'\n')
try:validate_review(rp,root=isolated,for_approval=True)
except Exception as e:negative.append({'case':'changed_bound_review_document','rejected':True,'error':str(e)})
else:raise AssertionError('Changed review document accepted')
rp.write_bytes(original);validate_review(rp,root=isolated,for_approval=True)
record={'task':'ARCHIVE-vw96-policy-source-v1','source_commit':review['source_commit'],'source_command':['git','show',review['source_commit']+':AGENTS.md'],'policy_sha256':h,'policy_bytes':len(policy),'independent_retained_copy':'/private/tmp/atlas-clay2013-release-v5/AGENTS.md','archive_path':entry['archived_path'],'review_path':name,'review_sha256':sha(original),'shared_map_path':mapname,'shared_map_before_sha256':sha(old),'proposed_map_sha256':sha(proposed),'proposed_delta':{'document_pins_added':1,'entries_added':1,'prior_document_pins_unchanged':True,'prior_entries_unchanged':True},'isolated_validation':'PASS','negative_probes':negative,'production_map_installed':False,'scope':'Recover exact historical policy and test an additive proposal only. No new scientific decision, model/runtime change, build, approval change or release. Shared-map source consumers need coordinated preservation before integration.'}
(p/'RECOVERY.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'isolated_validation':'PASS','negative_rejections':len(negative),'policy_sha256':h,'shared_map_installed':False}))
