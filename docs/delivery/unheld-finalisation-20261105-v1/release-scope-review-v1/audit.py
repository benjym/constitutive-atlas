from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parent;W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def git(*args):return subprocess.check_output(['git',*args],cwd=W)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert git('rev-parse','HEAD').decode().strip()=='6b957b866c977263fad0c02be4216c7f9170cf5b'
changed=git('diff','--name-only','-z').decode().split('\0')[:-1];untracked=git('ls-files','--others','--exclude-standard','-z').decode().split('\0')[:-1]
required={};missing=[]
def add(name,digest,why):
 p=W/name
 if not p.is_file():missing.append({'path':name,'reason':why});return
 assert sha(p)==digest,(name,why)
 required[name]=why
plan='docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/plan-v1.json';add(plan,'ed7839d19ec5c5b3615f5bf54d2e6273b8ec19fbe811f12a0336938c42581361','workflow explicit plan')
for key in ['norsand','interface2016']:
 base='docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/execution-v2/'+key+'/engine'
 p=W/base;data=json.loads((p/'refresh-qualification.json').read_text());binding=data['binding']
 for group in ['artifacts','build_metadata','generated']:
  for name,digest in binding[group].items():add(base+('/generated/' if group=='generated' else '/')+name,digest,'validate_refresh '+key+' '+group)
 for group in ['commands','results','source_closure']:
  for name,digest in binding[group].items():add(name,digest,'validate_refresh '+key+' '+group)
 add(base+'/build-review.json',data['independent_review']['sha256'],'independent controlled review')
 pending=json.loads((p/'build-review.json').read_text());add(base+'/qualification-pending.json',pending['qualification_pending_sha256'],'pending exact review preimage')
 # Final receipt itself must be retained for selected Pages engine path.
 add(base+'/refresh-qualification.json',sha(p/'refresh-qualification.json'),'workflow selected engine')
for row in json.loads((W/'catalogue/approved-models.json').read_text())['models']:
 if row['model_id'] not in ['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']:continue
 # Approval consumer retains a direct support closure; existing archive sidecar handles changed historical canonicals.
 for pin in row.get('supporting_files',[]):
  if isinstance(pin,dict) and 'path'in pin:
   name=pin['path'];digest=pin.get('sha256')
   if digest and (W/name).is_file() and sha(W/name)==digest:add(name,digest,'five E5 direct pin')
# Resolve every selected direct pin through the exact established archive sidecars.
archives=[]
for sidecar in ['catalogue/source-archive-map.json','catalogue/agent-reviews/source-archive-map.json']:
 obj=json.loads((W/sidecar).read_text());archives.extend(obj.get('entries',obj.get('archives',[])))
def resolve_pin(name,digest):
 if (W/name).is_file() and sha(W/name)==digest:return name
 matches=[x['archived_path']for x in archives if x.get('original_path')==name and x.get('sha256')==digest]
 assert len(set(matches))==1,(name,digest,matches)
 return matches[0]
for row in json.loads((W/'catalogue/approved-models.json').read_text())['models']:
 if row['model_id']not in ['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']:continue
 for pin in row.get('supporting_files',[]):
  if isinstance(pin,dict)and 'path'in pin and 'sha256'in pin:add(resolve_pin(pin['path'],pin['sha256']),pin['sha256'],'exact E5 direct closure resolved')
# Every changed/untracked file is scoped canonical payload or its installed direct-proof closure.
extra=sorted(set(required)-set(changed)-set(untracked));ignored=[]
for name in extra:
 result=subprocess.run(['git','check-ignore','-q','--',name],cwd=W)
 if result.returncode==0:ignored.append(name)
tracked=set(git('ls-files','-z').decode().split('\0')[:-1])
stage=sorted(set(changed+untracked+ignored))
rows=[]
for name in stage:
 p=W/name;assert p.is_file() and not p.is_symlink(),name
 rows.append({'path':name,'sha256':sha(p),'bytes':p.stat().st_size,'mode':'100755'if p.stat().st_mode&0o111 else'100644','tracked_preimage':name in tracked,'requires_explicit_force':name in ignored,'reason':required.get(name,'installed canonical change or retained direct proof input')})
(R/'stage-paths.nul').write_bytes(b'\0'.join(x['path'].encode()for x in rows)+b'\0')
(R/'stage-paths.txt').write_text('\n'.join(x['path']for x in rows)+'\n');(R/'stage-pins.json').write_text(json.dumps(rows,indent=2)+'\n')
report={'status':'SOURCE_SCOPE_READY'if not missing else'BLOCKED','base':'6b957b866c977263fad0c02be4216c7f9170cf5b','tracked_changed':len(changed),'untracked_nondisposable':len(untracked),'ignored_required':ignored,'stage_paths':len(rows),'stage_bytes':sum(x['bytes']for x in rows),'required_closure_pins':len(required),'missing':missing,'browser':'pending separate actual review','no_git_mutations':True,'stage_vector_sha256':sha(R/'stage-paths.nul')}
(R/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
