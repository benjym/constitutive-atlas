from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;backend=sys.argv[1];b=Path('/private/tmp/atlas-common-scalar-functions-v1/engine-'+backend+'-v1');out=p/'engine-results-v1';report=out/(backend+'-build-audit.json');assert not report.exists()
freeze=json.loads((p/'engine-source-freeze-v1.json').read_text())
for name,h in freeze['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
for name,h in json.loads((p/'engine-gate-freeze-v2.json').read_text())['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
allcmds=json.loads((b/'compile_commands.json').read_text());targets=['atlas_scalar_functions','atlas_solver']+(['atlas_numerical_tests','atlas_recorded_tests'] if backend=='native' else []);cmds=[c for c in allcmds if any('CMakeFiles/'+t+'.dir/' in c['command'] for t in targets)];assert len(cmds)==(15 if backend=='native' else 13)
objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args);obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.exists();row={'path':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/(backend+'-'+obj.name+'-assembly.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=hashlib.sha256(asm).hexdigest(),fused_instructions=0)
 objects.append(row)
links={}
for t in targets[1:]:
 link=(b/('CMakeFiles/'+t+'.dir/link.txt')).read_text();responses={}
 for token in shlex.split(link):
  if token.startswith('@'):
   f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
 assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values());links[t]={'command':link,'response_files':responses}
artifacts=[b/t for t in targets[1:]] if backend=='native' else [b/'atlas.js',b/'atlas.wasm'];assert all(f.exists() for f in artifacts)
if backend=='native':
 for f in artifacts:
  nm=subprocess.check_output(['nm',str(f)]);(out/(f.name+'-symbols.txt')).write_bytes(nm)
  for symbol in [b' T _atlas_scalar_power\n',b' T _atlas_cyclic_sine\n']:assert symbol in nm
source=Path(freeze['source']);assert (b/'generated/models.json').read_bytes()==(source/'generated/models.json').read_bytes();cat=json.loads((b/'generated/models.json').read_text());assert len(cat['models'])==14 and cat['sha256']==freeze['catalogue_sha256']
report.write_text(json.dumps(dict(status='passed',scope='Actual selected commands/objects+common library linkage; native noFMA; exact479source/98gate bindings/generated14catalogue',backend=backend,commands=cmds,objects=objects,links=links,catalogue_sha256=cat['sha256'],artifacts={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}),indent=2)+'\n');print(backend,len(cmds),'commands/objects/link/source/generated verified')
