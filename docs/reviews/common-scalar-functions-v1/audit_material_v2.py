from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;backend=sys.argv[1];b=Path('/private/tmp/atlas-common-scalar-functions-v1/material-'+backend+'-v1');out=p/'material-results-v1';report=out/(backend+'-build-audit-v2.json');assert not report.exists()
freeze=json.loads((p/'material-source-freeze-v1.json').read_text())
for name,h in freeze['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
cmds=json.loads((b/'compile_commands.json').read_text());assert len(cmds)==14;assert {Path(c['file']).name for c in cmds if c['file'].endswith('.cpp')}=={'main.cpp','inspector.cpp'};objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args);obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.exists();row={'path':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/(backend+'-'+obj.name+'-assembly.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=hashlib.sha256(asm).hexdigest(),fused_instructions=0)
 objects.append(row)
link=(b/'CMakeFiles/atlas_duncan_api.dir/link.txt').read_text();responses={}
linkargs=shlex.split(link)
for i,token in enumerate(linkargs):
 if token.startswith('@') and not (i and linkargs[i-1]=='-install_name'):
  f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values())
artifacts=[b/'libatlas_duncan_api.dylib'] if backend=='native' else [b/'duncan.js',b/'duncan.wasm'];assert all(f.exists() for f in artifacts)
if backend=='native':
 nm=subprocess.check_output(['nm',str(artifacts[0])]);(out/'native-symbols.txt').write_bytes(nm)
 for symbol in [b' T _atlas_scalar_power\n',b' T _atlas_cyclic_sine\n',b' T _atlas_study_jacobian\n']:assert symbol in nm
report.write_text(json.dumps(dict(status='passed',scope='Actual14commands/objects/common library linkage; native noFMA; exact63material sourcebindings',backend=backend,commands=cmds,objects=objects,link=link,response_files=responses,artifacts={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}),indent=2)+'\n');print(backend,'14commands/objects/link/source verified')
