from pathlib import Path
import json,hashlib,subprocess,sys,tempfile,importlib.util,re
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=R/'docs/ingestion/vibe-2026/sclay-browser-retention-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=R)
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
m=P/'source-manifest-v1.json';assert h(m)=='5380d8ac5de2802be267427cfe78ccbe4da4c91d9c654b8201d955772a2cbdb4'
for f in read(m)['files']:assert h(R/f['path'])==f['sha256']
plan=read(P/'plan-v1.json');baseline=read(O/'independent-baseline.json');assert h(P/'plan-v1.json')=='4a0d63713f2ef934f899b4275e2a4ca93592c9a37bc45dfa3c41eb255fb3c982';assert len(plan['files'])==5
browser=R/plan['original_manifest']['path'];assert h(browser)==baseline['browser_manifest_sha256']==plan['original_manifest']['sha256'];assert git('show','HEAD:'+str(browser.relative_to(R)))==browser.read_bytes()
for row in plan['files']:
 original=R/row['original_path'];archive=R/row['archived_path'];assert not original.exists();assert git('show','HEAD:'+row['original_path'])==archive.read_bytes();assert h(archive)==row['sha256'] and archive.stat().st_size==row['bytes'];assert row['archived_path']=='catalogue/source-snapshots/'+row['sha256']+'/'+row['original_path'];assert read(browser)['files'][row['manifest_key']]==row['sha256']
assert sum(r['bytes'] for r in plan['files'])==572358
oldpaths=git('ls-tree','-r','--name-only','HEAD','docs/ingestion/s-clay1').decode().splitlines();unchanged=0
for p in oldpaths:
 if p in [r['original_path'] for r in plan['files']]:continue
 assert git('show','HEAD:'+p)==(R/p).read_bytes(),p;unchanged+=1
assert unchanged==553
for p in ['tests/test_ingestion_packets.py','catalogue/agent-reviews/source-archive-map.json','atlas/evidence.py']:assert git('show','HEAD:'+p)==(R/p).read_bytes()
# Exact original-folder navigation links must resolve to extant retained bytes/receipts.
ret=R/'docs/ingestion/s-clay1/supplied-original-v3/browser-v1/RETENTION.md'
for href in re.findall(r'\]\(([^)]+)\)',ret.read_text()):assert (ret.parent/href).resolve().is_file(),href
spec=importlib.util.spec_from_file_location('independent_sclay_retention',P/'retention.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);proof=mod.verify();assert proof==read(P/'recovery-receipt-v1.json')
negatives=[]
with tempfile.TemporaryDirectory(prefix='retention-negative-',dir=O) as t:
 root=Path(t);doc=root/plan['original_manifest']['path'];doc.parent.mkdir(parents=True);doc.write_bytes(browser.read_bytes());row=plan['files'][0];arc=root/row['archived_path'];arc.parent.mkdir(parents=True);arc.write_bytes((R/row['archived_path']).read_bytes());assert mod.resolve_screenshot(row['manifest_key'],root)==arc
 for name,action in [('corrupt archive',lambda:arc.write_bytes(b'corrupt')),('missing archive',lambda:arc.unlink()),('changed manifest',lambda:doc.write_text('{}'))]:
  action()
  try:mod.resolve_screenshot(row['manifest_key'],root)
  except (ValueError,FileNotFoundError):negatives.append(name)
  else:raise AssertionError(name)
for key in ['../escape.png','/screenshots/profile-desktop.png','screenshots/unknown.png']:
 try:mod.resolve_screenshot(key)
 except ValueError:negatives.append(key)
 else:raise AssertionError(key)
cmd=baseline['command'];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'independent-packet-guard-post.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and 'OK' in r.stderr
v='catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json';vibe=read(R/v);assert len(vibe['artifacts'])==281
for f in vibe['artifacts']:assert h(R/f['path'])==f['sha256']==h(checked_receipt(R,v,f['path'],f['sha256']))
count=0
for a in read(R/'catalogue/approved-models.json')['models']:
 p=R/a['review']['path']
 if p.suffix=='.json':validate_review(p,root=R,for_approval=True);assert approval_entry(p,root=R)==a
 else:assert git('show','HEAD:'+a['review']['path'])==p.read_bytes()
 count+=1
closures=[]
for name in ['controlled-path-refresh-v1/plan-v5.json','maxwell-refresh-v1/plan.json']:
 p=read(R/'docs/ingestion/vibe-2026'/name);pins={**p.get('source_closure',p.get('source_manifest',{}).get('files',{})),**{x['path']:x['sha256'] for x in p.get('files',[])}}
 for path,sha in pins.items():assert h(R/path)==sha
 closures.append({'plan':name,'pins':len(pins)})
report={'status':'accepted','source_manifest_sha256':h(m),'original_screenshots':5,'lossless_bytes':572358,'all_original_png_bytes_equal_git_head':True,'unchanged_other_sclay_files':unchanged,'old_manifest_and_receipts_unchanged':True,'map_and_resolver_unchanged':True,'consumer':'New explicit original-folder RETENTION.md links and frozen relative-key resolver bind exact old browser manifest to canonical archive; no generic checked_receipt claim.','negative_rejection_checks':negatives,'unchanged_packet_guard':{'baseline':'genuine S-CLAY PNG violation retained','post':'PASS','test_sha256':h(R/'tests/test_ingestion_packets.py')},'vibe_supports_direct_and_resolver':281,'approvals':count,'dependency_closures':closures,'blocking_findings':[],'build_browser_material_remote_calls':0,'cleanup':'Pure recovery and negative fixtures automatically removed; no processes/builds/downloads created. Five unique PNGs durably retained; no original receipt modified.'};(O/'decision.json').write_text(json.dumps(report,indent=2)+'\n');files=[p for p in O.iterdir() if p.is_file()]+[m,ret];(O/'manifest.json').write_text(json.dumps({'files':[{'path':str(p.relative_to(R)),'sha256':h(p)} for p in files]},indent=2)+'\n');print('decision',h(O/'decision.json'));print('manifest',h(O/'manifest.json'));print('unchanged',unchanged,'approvals',count)
