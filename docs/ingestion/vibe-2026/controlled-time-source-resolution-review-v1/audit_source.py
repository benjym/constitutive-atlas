from pathlib import Path
import ast,json,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=R/'docs/ingestion/vibe-2026/controlled-time-source-resolution-v1';sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
git=lambda *args:subprocess.check_output(['git',*args],cwd=R)
f=P/'source-manifest-v1.json';d=read(f)
for x in d['files']:assert sha(R/x['path'])==x['sha256'],x['path']
assert len(d['current_sources'])==2
for name,h in d['current_sources'].items():assert sha(R/name)==h
old=git('show','d4a17aa2c:tools/check_controlled_time_ci.py');new=(R/'tools/check_controlled_time_ci.py').read_bytes()
a=ast.parse(old);b=ast.parse(new)
functions=lambda tree:{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
af=functions(a);bf=functions(b)
for name in af:
 if name!='verify':assert ast.dump(af[name])==ast.dump(bf[name]),name
assignments=lambda tree:{n.targets[0].id:ast.dump(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
aa=assignments(a);ba=assignments(b)
for name in aa:assert aa[name]==ba[name],name
# Numerics, portable reversal and direct portable source gate remain exact source text.
s=old.decode();t=new.decode();start=s.index(" oldpath=ROOT/");end=s.index(" result=dict(status='pass-source-only'")
original=s[start:end];actual=t[t.index(" oldpath=ROOT/"):t.index(" accepted_decision(AMENDMENT_REVIEW")]
assert actual==original
assert s[s.index(" result=dict(status='pass-source-only'"):]==t[t.index(" result=dict(status='pass-source-only'"):]
ci='docs/ingestion/vibe-2026/controlled-time-ci-v1/source-manifest-v1.json';oldsha='9c599a0594035a3e77bd1fdbb22538041320847b58149a1427ce5b0e7ec28b05'
arch=R/'catalogue/source-snapshots'/oldsha/'tools/check_controlled_time_ci.py';assert arch.read_bytes()==old and sha(arch)==oldsha
m=read(R/Path(ci).with_name('source-archive-map.json'));assert set(m['documents'])=={ci} and len(m['entries'])==1
assert checked_receipt(R,ci,'tools/check_controlled_time_ci.py',oldsha)==arch
# No shared scientific records or production source changed besides the assigned checker.
for path in ['catalogue/approved-models.json','catalogue/manifest.json','atlas/evidence.py','atlas/compiler.py','atlas/model.py','atlas/research.py','tests/test_controlled_time.py']:
 assert git('show','d4a17aa2c:'+path)==(R/path).read_bytes(),path
registry=read(R/'catalogue/approved-models.json');approvals=[]
for row in registry['models']:
 doc=R/row['review']['path'];assert git('show','d4a17aa2c:'+row['review']['path'])==doc.read_bytes()
 if doc.suffix=='.json':validate_review(doc,root=R,for_approval=True);assert approval_entry(doc,root=R)==row
 assert sha(R/row['definition']['path'])==row['definition']['sha256'];approvals.append(row['model_id'])
v='catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json';supports=[]
for pin in read(R/v)['artifacts']:
 target=checked_receipt(R,v,pin['path'],pin['sha256']);assert sha(target)==pin['sha256'];supports.append(dict(path=pin['path'],selected=str(target.relative_to(R)),sha256=pin['sha256']))
assert len(supports)==281 and len(approvals)==30
closures=[]
for name in ['controlled-path-refresh-v1/plan-v5.json','maxwell-refresh-v1/plan.json']:
 plan=read(R/'docs/ingestion/vibe-2026'/name);pins={**plan.get('source_closure',plan.get('source_manifest',{}).get('files',{})),**{x['path']:x['sha256'] for x in plan.get('files',[])}}
 for path,h in pins.items():assert sha(R/path)==h,path
 closures.append(dict(plan=name,pins=len(pins)))
result=dict(source_freeze_sha256=sha(f),files=len(d['files']),current_sources=d['current_sources'],original_capture_and_other_functions_AST_exact=True,original_constants_AST_exact=True,portable_plan_reversal_numeric_and_result_source_exact=True,old_collector_exact_git_and_canonical=True,approval_count=30,vibe_supports=supports,dependency_closures=closures,compiled_calls=0)
(O/'source-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('source audit PASS',len(d['files']),'pins;281supports;30approvals;250+171dependency pins')
