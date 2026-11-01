from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;r=p.resolve().parents[2];backend=sys.argv[1];b=Path('/private/tmp/atlas-common-scalar-functions-v1/actual-root-'+backend+'-v1');out=p/'actual-root-v1';report=out/(backend+'-audit-v2.json');assert not report.exists();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
freeze=json.loads((out/'source-freeze.json').read_text())
for n,h in freeze['files'].items():assert sha(r/n)==h,n
cmds=json.loads((b/'compile_commands.json').read_text());targets=['atlas_scalar_functions','atlas_solver','atlas_scalar_probe']+(['atlas_numerical_tests','atlas_recorded_tests'] if backend=='native' else []);cmds=[c for c in cmds if any('CMakeFiles/'+t+'.dir/' in c['command'] for t in targets)];assert len(cmds)==(16 if backend=='native' else 14)
objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args);obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.is_file();row={'path':str(obj),'sha256':sha(obj)}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/('assembly-'+hashlib.sha256(str(obj).encode()).hexdigest()[:12]+'.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=sha(ap),fused_instructions=0)
 objects.append(row)
links={}
for t in targets[1:]:
 link=(b/('CMakeFiles/'+t+'.dir/link.txt')).read_text();responses={};skip=False
 for token in shlex.split(link):
  if skip:skip=False;continue
  if token=='-install_name':skip=True;continue
  if token.startswith('@'):
   f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
 assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values());links[t]={'command':link,'response_files':responses}
artifacts=[b/'atlas_solver',b/'atlas_numerical_tests',b/'atlas_recorded_tests',b/'libatlas_scalar_probe.dylib'] if backend=='native' else [b/'atlas.js',b/'atlas.wasm',b/'scalar-functions.js',b/'scalar-functions.wasm']
assert all(f.is_file() for f in artifacts)
cat=json.loads((b/'generated/models.json').read_text());assert len(cat['models'])==14 and cat['sha256']==freeze['catalogue_sha256']
assert (b/'generated/models.json').read_bytes()==(Path(json.loads((p/'engine-source-freeze-v1.json').read_text())['source'])/'generated/models.json').read_bytes()
report.write_text(json.dumps({'status':'passed','backend':backend,'source_freeze_sha256':sha(out/'source-freeze.json'),'commands':cmds,'objects':objects,'links':links,'artifacts':{str(f):sha(f) for f in artifacts},'catalogue_sha256':cat['sha256']},indent=2)+'\n');print(backend,len(cmds),'objects/source/generated/commonlinks verified')
