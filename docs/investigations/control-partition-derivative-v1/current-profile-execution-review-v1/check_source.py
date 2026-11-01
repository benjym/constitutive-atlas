"""Independent read-only review; no collector, compiler, assessment main or artifact calls."""
import sys
sys.dont_write_bytecode=True
import ast, hashlib,json,subprocess
from pathlib import Path
R=Path.cwd(); C=R/'docs/investigations/control-partition-derivative-v1';D=C/'current-profile-execution-v1';V=C/'profile-build-support-v5';S=Path('/private/tmp/atlas-control-partition-support-v4/source');O=Path('/private/tmp/atlas-control-partition-support-v3/source')
h=lambda b:hashlib.sha256(b).hexdigest(); read=lambda p:json.loads(p.read_text()); checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def manifest(d,expected):
 check(str(d.name)+' manifest identity',h((d/'manifest.json').read_bytes())==expected)
 m=read(d/'manifest.json');m=m.get('files',m)
 for n,v in m.items():check(d.name+'/'+n,h((d/n).read_bytes())==v)
manifest(D,'1c21734488ba4ec34c71653c8f532e2a935877de9273bddaab8fe8c6a6e035ab');manifest(V,'dc12055af1fe54a8ea7f6ab0e14ae3808c1afa52b74341d7ea0f03e7eeece8bc')
f=read(V/'source-freeze.json')['files'];old=read(C/'qualification-support-v4/source-freeze.json')['files'];add=read(V/'addition-receipt.json')['added'];closure=read(D/'collector-closure.json')
check('2722=2628+94',len(f)==2722 and len(old)==2628 and len(add)==94 and set(f)==set(old)|set(add) and not set(old)&set(add))
check('exact complete filesystem inventory',set(f)=={p.relative_to(S).as_posix() for p in S.rglob('*') if p.is_file()})
for n,v in f.items():check('source '+n,h((S/n).read_bytes())==v)
check('all old bytes preserved',all(f[n]==v and h((O/n).read_bytes())==v for n,v in old.items()))
check('missing inventory exactly additions',{x['path']:x['sha256'] for x in closure['missing']}=={n:v['sha256'] for n,v in add.items()})
for n,v in add.items():check('exact Git addition '+n,h(subprocess.check_output(['git','show',v['git_source']]))==v['sha256']==f[n])
for n,v in closure['files'].items():check('collector pinned '+n,h(Path(n).read_bytes())==v)
for n,e in read(D/'adapter-proof.json').items():
 if 'replacements' in e:
  original=Path(e['source']).read_text();adapter=(D/'adapters'/n).read_text();reverse=adapter
  for x in reversed(e['replacements']):reverse=reverse.replace(x['replacement'],x['original'])
  check('reversible '+n,reverse==original and h(original.encode())==e['source_sha256'] and h(adapter.encode())==e['adapter_sha256'])
 elif e.get('exact_reuse'):check('exact reused '+n,h((D/'adapters'/n).read_bytes())==e['sha256'])
# Reconstruct actual consumer membership, not merely rehash the supplied maps.
maxpaths={S/'cmake/maxwell/CMakeLists.txt',S/'cmake/AtlasScalarFunctions.cmake',S/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
maxpaths.update(p for p in (S/'cpp/scalar-functions').rglob('*') if p.is_file())
for directory,suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp'}),('schemas',{'.json'})]:maxpaths.update(p for p in (S/directory).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
norpaths=set((S/'cpp/include/atlas').rglob('*.hpp'));norpaths.update(p for p in (S/'cpp/scalar-functions').rglob('*') if p.is_file());norpaths.update(p for p in (S/'atlas').rglob('*.py') if '__pycache__' not in p.parts);norpaths.update((S/'schemas').rglob('*.json'));norpaths.update(S/p for p in ['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])
matchers={};expected=read(C/'qualification-support-v4/patched-source-manifests.json')['profiles']
for name,paths,count,digest in [('maxwell',maxpaths,149,'daf2bd8a62cc4d14a47f1ee2368873221c2e1da44482f3f3ac20fcc6a9353156'),('norsand',norpaths,121,'47e3b5d9b06bc131ac45770a62c4662a24b2fd12a3f6f18e988fea15c41b32dc')]:
 values={p.relative_to(S).as_posix():h(p.read_bytes()) for p in sorted(paths)};actual=h(json.dumps(values,sort_keys=True,separators=(',',':')).encode());check(name+' actual full membership and digest',len(values)==count and values==expected[name]['files'] and actual==digest);matchers[name]={'files':count,'sha256':actual}
p=read(D/'plan.json');steps=[x for row in p['profiles'] for x in row['steps']];check('seven profiles /65 commands',len(p['profiles'])==7 and len(steps)==65)
for i,x in enumerate(steps):
 check('old path explicit '+str(i),x['cwd']==str(O) and x['env']['ATLAS_QUALIFICATION_SOURCE']==str(O))
 check('bytecode disabled '+str(i),x['env']['PYTHONDONTWRITEBYTECODE']=='1')
 if '--build' in x['argv']:check('serial single-target '+str(i),x['argv'][-2:]==['--parallel','1'] and x['argv'].count('--target')==1)
 for a in x['argv']:
  if a.startswith(str(O)) and a.endswith(('.py','.mjs','.json')):check('executed input now present '+a,(S/Path(a).relative_to(O)).is_file())
for path in D.rglob('*.py'):ast.parse(path.read_text());checks.append('syntax '+path.name)
print(json.dumps({'identity':'independent-current-profile-plan-source-review-v1','passed':True,'checks':len(checks),'check_names':checks,'source_files':len(f),'old_files_unchanged':len(old),'exact_git_additions':len(add),'commands':len(steps),'matchers':matchers,'compiled_calls':0,'assessment_main_calls':0,'decision_scope':'Source closure and prospective plan only; separate explicit path-only rebind required before execution.'},indent=2))
