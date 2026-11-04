from pathlib import Path
import ast,hashlib,json,re,copy,importlib.util,tempfile
N=Path('docs/delivery/unheld-finalisation-20261105-v1');P=N/'rate-restoration-compatibility-impact-v2';Q=N/'rate-restoration-compatibility-impact-review-v2';S=N/'current17-runtime-source-v1/source';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
ck('exact frozen manifest',sha((P/'manifest.json').read_bytes())=='0b9abc0ac14bd70feb82fc5c80632195beeac86b940d117d4c96c110ae0e0ad0')
for name,pin in json.loads((P/'manifest.json').read_text())['files'].items():
 f=P/name;ck('member '+name,not f.is_symlink()and f.stat().st_size==pin['bytes']and sha(f.read_bytes())==pin['sha256'])
proof=json.loads((P/'proof.json').read_text());delta=json.loads((P/'implementation-delta.json').read_text())['files'];ck('exact9 canonical changes',len(delta)==9)
for row in delta:
 f=P/row['proposal'];ck('proposal '+row['path'],sha(f.read_bytes())==row['sha256']and f.stat().st_size==row['bytes'])
 if row['preimage_sha256']is not None:
  source=S/row['path'];ck('exact predecessor '+row['path'],sha(source.read_bytes())==row['preimage_sha256'])
for n,h in proof['implementation'].items():ck('four implementation pins '+n,sha((P/'proposed'/n).read_bytes())==h)
for n,row in proof['aliases'].items():ck('intrinsic predecessor '+n,sha((P/'proposed'/row['archive']).read_bytes())==row['predecessor_sha256'])
for n,h in proof['ancestors'].items():ck('ten unchanged authorities '+n,sha((W/n).read_bytes())==h)
# Prove every function other than the declared byte-read boundary is exact AST.
for name,boundary in [('tools/profile_source_compatibility.py','regular'),('tools/profile_source_compatibility_baseline.py','regular'),('tools/build_controlled_time_web.py','sha')]:
 a=ast.parse((S/name).read_text());b=ast.parse((P/'proposed'/name).read_text());a.body=[x for x in a.body if not(isinstance(x,ast.FunctionDef)and x.name==boundary)];b.body=[x for x in b.body if not(isinstance(x,ast.FunctionDef)and x.name==boundary)];ck('entire other module AST exact '+name,ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False))
# Independently follow complete saved project quoted includes and compare edges.
closures=json.loads((P/'include-closures.json').read_text())
for profile,saved in closures.items():
 for path,h in saved['files'].items():
  f=Path(path)
  if f.resolve()==(S/'cpp/include/atlas/solver.hpp').resolve():f=N/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp'
  ck(profile+' include exact '+path,sha(f.read_bytes())==h)
  text=f.read_text();quoted=re.findall(r'^\s*#\s*include\s*"([^"]+)"',text,re.M)
  edges=[e for e in saved['edges']if e[0]==path];ck(profile+' all quoted dependencies enumerated '+path,len(edges)==len(quoted))
  generated=W/({'norsand':'web/engines/current17-compatible/norsand','interface2016':'web/engines/current17-baseline-compatible/interface2016','maxwell':'web/engines/current17-compatible/maxwell','controlled-time':'web/engines/controlled-time'}[profile])/'generated'
  for name,edge in zip(quoted,edges):
   candidates=[Path(path).parent/name,generated/name,S/'cpp/include'/name,S/'cpp/scalar-functions'/name];resolved=next(x.resolve()for x in candidates if x.is_file());ck(profile+' exact include edge '+name,str(resolved)==edge[1])
  ck(profile+' no hidden project angle include '+path,not re.search(r'#\s*include\s*<atlas/',text))
 ck(profile+' expected solver reachability',saved['solver_reachable']==(profile=='maxwell'))
main=(S/'cpp/main.cpp').read_text();require=main[main.index('void require_incremental_stress_contract('):main.index('void write_laboratory_scope(')]
response=main[main.index('static const char* run_response('):main.index('extern "C" ATLAS_EXPORT const char* atlas_run(')]
ck('Maxwell physical-time contract rejects incremental entry','if(m.physical_time||'in require and 'throw std::runtime_error'in require)
ck('Maxwell gate before controller producer',response.index('require_incremental_stress_contract(m,scope_aware)')<response.index('atlas::run_protocol'))
old=(S/'cpp/include/atlas/solver.hpp').read_text();c=(N/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp').read_text();start='inline bool controlled_step(';end='// Research range'
ck('C core outside controlled_step exact640',old[:old.index(start)]==c[:c.index(start)]and old[old.index(end):]==c[c.index(end):])
# Independently compare selected retained maps against the exact C source view.
for category,relative in [('direct','direct-profile-compatibility-implementation-v1/bindings.json'),('baseline','upstream-interface-compatibility-v1/bindings.json')]:
 bindings=json.loads((W/'docs/ingestion/manzari-dafalias-1997/delivery-v1'/relative).read_text())
 for profile,row in bindings.items():
  changes=[]
  for name,h in row['source_files'].items():
   if name=='cpp/include/atlas/solver.hpp':data=c.encode()
   else:
    source=S/name;data=(source if source.is_file()else W/name).read_bytes()
   if sha(data)!=h:changes.append(name)
  if category=='direct'and profile=='interface2016':ck('older unselected interface remains blocked',len(changes)==8)
  else:ck('selected map only C solver differs '+category+'/'+profile,changes==['cpp/include/atlas/solver.hpp'])
# Reproduce author's pure source/manufactured checks in owned scratch/output.
code=(P/'check_source.py').read_text().replace('P=Path(__file__).resolve().parent;',f'P=Path({str(P.resolve())!r});').replace('dir=P)',f'dir=Path({str(Q.resolve())!r}))').replace("(P/'source-checks.json').write_text",f"(Path({str(Q.resolve())!r})/'author-source-checks.json').write_text")
exec(compile(code,str(P/'check_source.py'),'exec'),{'__file__':str(Q/'check.py')})
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_generation_calls':0},indent=2)+'\n');print(json.dumps({'passed':True,'independent_checks':len(checks)}))
