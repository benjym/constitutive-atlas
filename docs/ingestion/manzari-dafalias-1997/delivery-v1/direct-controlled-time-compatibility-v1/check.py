"""Source-only controlled-time dependency and generated-byte comparison."""
from pathlib import Path
import sys,json,hashlib,re,difflib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=S/'web/engines/controlled-time';q=json.loads((B/'public-qualification.json').read_text())
rows=[]
for x in q['source_files']:
 p=S/x['path'];rows.append(dict(path=x['path'],qualified=x['sha256'],current=sha(p)))
changed=[x for x in rows if x['qualified']!=x['current']]
assert len(changed)==1 and changed[0]['path']=='cpp/include/atlas/solver.hpp'
x=changed[0];old=S/'catalogue/source-snapshots'/x['qualified']/x['path'];assert sha(old)==x['qualified']
(P/'solver.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),(S/x['path']).read_text().splitlines(True),fromfile='qualified/solver.hpp',tofile='current/solver.hpp')))
sys.path.insert(0,str(S))
from atlas.controlled_time_compiler import generate
model=json.loads((S/'catalogue/approved-models.json').read_text())['models']
a=[a for a in model if a['model_id']==q['model_id'] and a['status']=='approved' and a['definition']['sha256']==q['definition_sha256']];assert len(a)==1
model=S/a[0]['definition']['path'];generate(P/'generated',[model])
generated={}
for n in ['controlled_time_api.cpp','controlled_time_models.hpp','controlled_time_catalogue.json']:
 assert (P/'generated'/n).read_bytes()==(B/'generated'/n).read_bytes(),n
 generated[n]=sha(P/'generated'/n)
# Quoted includes resolve using the exact target's generated and cpp/include paths.
seen={};pending=[B/'generated/controlled_time_api.cpp'];edges=[]
while pending:
 p=pending.pop();key=str(p.relative_to(S))
 if key in seen:continue
 seen[key]=sha(p)
 for line in p.read_text().splitlines():
  if re.match(r'\s*#\s*include\b',line):
   m=re.match(r'\s*#\s*include\s*[<"]([^>"]+)[>"]',line);assert m,('dynamic include',key,line)
   if '"' not in line:continue
   n=m.group(1);choices=[p.parent/n,S/'cpp/include'/n,B/'generated'/n];target=next((z for z in choices if z.is_file()),None);assert target,(key,n)
   edges.append([key,str(target.relative_to(S))]);pending.append(target)
assert 'cpp/include/atlas/solver.hpp' not in seen
unlisted={}
for name,h in seen.items():
 if name.startswith('cpp/'):
  matched=any(r['path']==name and r['qualified']==h==r['current'] for r in rows)
  if not matched:
   baseline=Path('/private/tmp/atlas-md1997-current-main-integration-v1/baseline16-source')/name
   assert baseline.is_file() and sha(baseline)==h,name
   unlisted[name]={'current_sha256':h,'original02ad_baseline_sha256':sha(baseline),'qualification_receipt_pin_present':False}
for n,h in q['artifacts'].items():assert sha(B/n)==h,n
assert (B/'public-qualification.json').read_bytes()==(S/q['root_receipt_path']).read_bytes()
for n in ['examples','public_results']:
 assert sha(S/q[n]['path'])==q[n]['sha256']
report=dict(source_files=len(rows),source_inventory=rows,changed=changed,generated=generated,compile_dependency_files=seen,include_edges=edges,solver_reachable=False,unlisted_dependency_headers=unlisted,artifacts_exact=q['artifacts'],qualification_sha256=sha(B/'public-qualification.json'),approval=a[0],historical_solver={'path':str(old.relative_to(S)),'sha256':sha(old)},current_model={'path':str(model.relative_to(S)),'sha256':sha(model)})
(P/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'source_files':len(rows),'changed':changed,'generated_exact':len(generated),'cpp_dependency_files':len(seen),'solver_reachable':False},indent=2))
