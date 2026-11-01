from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;key=sys.argv[1];backend,name=key.split('/');cs=json.loads((p/'consumer-commands-v1.json').read_text())[key];b=Path(cs['build'][2]);out=p/'consumer-results-v1'/backend/name;out.mkdir(parents=True,exist_ok=True);report=out/'build-audit.json';assert not report.exists()
for f,h in json.loads((p/'consumer-source-freeze-v1.json').read_text())['files'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
cmds=json.loads((b/'compile_commands.json').read_text());assert len(cmds)==13;objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args);obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.exists();row={'path':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/(obj.name+'-assembly.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=hashlib.sha256(asm).hexdigest(),fused_instructions=0)
 objects.append(row)
link=(b/('CMakeFiles/'+cs['target']+'.dir/link.txt')).read_text();args=shlex.split(link);responses={}
for i,token in enumerate(args):
 if token.startswith('@') and not (i and args[i-1]=='-install_name'):
  f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values())
artifacts=([b/cs['target']] if (b/cs['target']).is_file() else [b/('lib'+cs['target']+'.dylib')]) if backend=='native' else [*b.glob('*.js'),*b.glob('*.mjs'),*b.glob('*.wasm')];assert artifacts and all(f.is_file() for f in artifacts)
report.write_text(json.dumps(dict(status='passed',scope='Consumer compiler/link qualification only, no scientific/material/preset/browser approval; unused archive objects may be deadstripped',consumer=key,commands=cmds,objects=objects,link=link,response_files=responses,artifacts={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}),indent=2)+'\n');print(key,'13commands/objects/librarylink verified')
