from pathlib import Path
import json,hashlib,subprocess,sys,re,shlex
p=Path(__file__).parent;backend=sys.argv[1];b=Path('/private/tmp/atlas-common-scalar-functions-v1/generic-'+backend+'-v2');out=p/'generic-results-v1';report=out/(backend+'-build-audit.json');assert not report.exists()
for freeze in ['generic-regression-freeze-v2.json','generic-regression-gate-freeze-v1.json']:
 for name,h in json.loads((p/freeze).read_text())['files'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
cmds=json.loads((b/'compile_commands.json').read_text());assert len(cmds)==16;targets=['atlas_partition_analytical','atlas_partition_regression','atlas_spectral_multiplicity','atlas_recorded_retry_counter'];objects=[]
for c in cmds:
 args=shlex.split(c['command']);assert args.count('-ffp-contract=off')==1;assert not any(a in ['-ffast-math','-ffp-contract=fast','-ffp-contract=on','-flto'] for a in args);obj=Path(c['directory'])/args[args.index('-o')+1];assert obj.exists();row={'path':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
 if backend=='native':
  asm=subprocess.check_output(['otool','-tvV',str(obj)]);ap=out/(backend+'-'+obj.name+'-assembly.txt');ap.write_bytes(asm);assert not re.search(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',asm.decode());row.update(assembly=str(ap),assembly_sha256=hashlib.sha256(asm).hexdigest(),fused_instructions=0)
 objects.append(row)
links={}
for t in targets:
 link=(b/('CMakeFiles/'+t+'.dir/link.txt')).read_text();responses={};args=shlex.split(link)
 for i,token in enumerate(args):
  if token.startswith('@') and not (i and args[i-1]=='-install_name'):
   f=b/token[1:];assert f.is_file();responses[str(f)]=f.read_text()
 assert 'libatlas_scalar_functions.a' in link+' '.join(responses.values());links[t]={'command':link,'response_files':responses}
artifacts=[b/(t+suffix) for t in targets for suffix in ([''] if backend=='native' else ['.js','.wasm'])];assert all(f.exists() for f in artifacts)
report.write_text(json.dumps(dict(status='passed',backend=backend,scope='16actualcommands/objects;4actualcommonarchive linkclosures; exactsource/referencebindings; native noFMA',commands=cmds,objects=objects,links=links,artifacts={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}),indent=2)+'\n');print(backend,'16commands/objects and4links verified')
