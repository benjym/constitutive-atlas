from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;backend=sys.argv[1];b=Path('/private/tmp/atlas-common-scalar-functions-v1/scalar-probe-'+backend+'-v1');out=p/'scalar-probe-results-v1';report=out/(backend+'-build-audit-v2.json');assert not report.exists()
for name,h in json.loads((p/'scalar-probe-source-freeze-v1.json').read_text())['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
cmds=json.loads((b/'compile_commands.json').read_text());assert len(cmds)==13;assert sum(c['file'].endswith('scalar_probe.cpp') for c in cmds)==1
objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args)
 obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.exists();row={'path':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/('native-'+obj.name+'-assembly.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=hashlib.sha256(asm).hexdigest(),fused_instructions=0)
 objects.append(row)
link=(b/'CMakeFiles/atlas_scalar_probe.dir/link.txt').read_text();responses={}
for token in shlex.split(link):
 if token.startswith('@'):
  f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values())
artifacts=list(b.glob('libatlas_scalar_probe.dylib')) if backend=='native' else [b/'scalar-functions.js',b/'scalar-functions.wasm'];assert artifacts and all(f.exists() for f in artifacts)
if backend=='native':
 nm=subprocess.check_output(['nm',str(artifacts[0])]);(out/'native-symbols.txt').write_bytes(nm)
 for symbol in [b' T _atlas_scalar_power\n',b' T _atlas_cyclic_sine\n']:assert symbol in nm
report.write_text(json.dumps(dict(status='passed',scope='Actual13commands/objects; linked common library; native noFMA object disassembly; bounded391scalar qualification only',backend=backend,commands=cmds,objects=objects,link_command=link,link_response_files=responses,artifacts={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}),indent=2)+'\n');print(backend,'13commands/objects and linkage verified')
