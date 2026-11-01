from pathlib import Path
import hashlib,json,subprocess,re
p=Path(__file__).parent;b=Path('/private/tmp/atlas-duncan-portable-controls-v1/native');s=b.parent/'source'
assert not (p/'build-audit.json').exists()
commands=json.loads((b/'compile_commands.json').read_text());selected=[];objects=[]
for c in commands:
 if 'CMakeFiles/atlas_solver.dir/' not in c['command']:continue
 assert '-ffp-contract=off' in c['command'];assert '-ffast-math' not in c['command'];assert '-ffp-contract=fast' not in c['command'];assert '-flto' not in c['command']
 selected.append(c);m=re.search(r' -o (\S+) ',c['command']);assert m,c;obj=Path(c['directory'])/m.group(1);assert obj.exists();objects.append(obj)
assert len(selected)==13,len(selected)
assert sum(c['file'].endswith('cpp/main.cpp') for c in selected)==1
assert {Path(c['file']).name for c in selected}=={'main.cpp','pow.c','pow_data.c','exp_data.c','__math_xflow.c','__math_uflow.c','__math_oflow.c','__math_invalid.c','sin.c','__sin.c','__cos.c','__rem_pio2.c','__rem_pio2_large.c'}
audit=[]
for obj in objects:
 raw=subprocess.check_output(['otool','-tvV',str(obj)]);out=p/(obj.name+'-assembly.txt');out.write_bytes(raw);text=raw.decode();fused=re.findall(r'\b(?:fmadd|fmsub|fnmadd|fnmsub|fmla|fmls)\b',text);assert not fused,(obj,fused[:3]);audit.append({'object':str(obj),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'assembly':str(out),'assembly_sha256':hashlib.sha256(raw).hexdigest(),'fused_instructions':0})
assert (b/'generated/models.json').read_bytes()==(p.parent/'frozen/generated/models.json').read_bytes()
for f,h in json.loads((p/'source-freeze.json').read_text())['files'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
for f in (p/'adapted').glob('*'):
 target=s/('cpp/include/atlas/'+f.name if f.name=='tensor.hpp' or f.name=='solver.hpp' else 'CMakeLists.txt' if f.name=='CMakeLists.txt' else 'diagnostic_pow/'+f.name)
 assert target.read_bytes()==f.read_bytes(),str(target)
assert (s/'cpp/include/atlas/tensor.hpp').read_bytes()==(p.parent/'portable-power-v1/adapted/tensor.hpp').read_bytes()
(p/'selected-compile-commands.json').write_text(json.dumps(selected,indent=2)+'\n')
nm=subprocess.check_output(['nm',str(b/'atlas_solver')]);(p/'symbols.txt').write_bytes(nm);assert b' T _atlas_diagnostic_pow\n' in nm;assert b' T _atlas_diagnostic_sin\n' in nm
(p/'build-audit.json').write_text(json.dumps({'scope':'actualtarget13commands/objects; nearest-default binary64 diagnostic, no production approval','commands':selected,'objects':audit,'generated_catalogue_exact':True,'candidate_source_exact':True,'executable_sha256':hashlib.sha256((b/'atlas_solver').read_bytes()).hexdigest(),'new_power_symbol_present':True,'new_control_sine_symbol_present':True},indent=2)+'\n')
print('13target-specific commands/objects: no fusedinstructions; exactcandidate/source/generated catalogue; new power symbol linked')
