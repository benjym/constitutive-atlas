from pathlib import Path
import hashlib,json,re,struct
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):
 if not v:raise AssertionError(n)
 checks.append(n)
r=json.loads((O/'recipe.json').read_text());c=json.loads((O/'parent-case.json').read_text());g=json.loads((O/'GATES.json').read_text())
for p in r['source_inputs']+list(r['tools'].values())+c['parent_provenance']:
 path=Path(p['path']);ok(sha(path)==p['sha256']and path.stat().st_size==p['bytes'],'source/tool/nativeinput pin '+p['path'])
source=Path(g['source']['path']).read_text();start=source.index('inline bool controlled_step(');end=source.index('// Research range',start);original=source[start:end]
ok(original==(O/'original-controlled-step.txt').read_text(),'exact full original controller')
logged=(O/'logged-controlled-step.inc').read_text();stripped=re.sub(r'/\*TRACE_BEGIN\*/.*?/\*TRACE_END\*/','',logged,flags=re.S).replace('logged_controlled_step(','controlled_step(',1)
ok(stripped==original,'controller byteexact after removing logging and rename')
ok(len(re.findall(r'/\*TRACE_BEGIN\*/',logged))==4,'only4 logging insertions')
ok('consistent_control_derivative(trial,de,direction,h,'in logged,'unchanged original derivative function call')
cpp=(O/'trace.cpp').read_text()
for name in('representable','comparable','finite_slope','stable','base_substeps','probe_substeps','base_fractions','probe_fractions','base_partition_retries','probe_partition_retries'):
 ok(name in cpp,'diagnostic field '+name)
ok('return 0; // A completed diagnostic' in cpp,'diagnostic completion is not scientific pass')
for forbidden in('evaluate_model(','midpoint(','advance_recursive(','implicit_step('):ok(forbidden not in cpp,'no new materialkernel '+forbidden)
parent=json.loads(Path(c['parent_provenance'][1]['path']).read_text());last=parent['points'][-1]
ok(c['state']==last['state']and c['parameters']==parent['parameters'],'genuine native state+parameters exact')
ok(c['settings']==parent['integration_settings'],'original settings exact')
controls=[struct.unpack('>d',bytes.fromhex(x))[0]for x in parent['loading']['controls_bits']]
ok(c['axial']==controls[93]-controls[92]and c['native_parent_control']==controls[92]and c['current_axial']==last['strain'][0],'exact failed93 binary64 control subtraction')
ok(c['reference']==.5*(parent['initial'][1]+parent['initial'][2])==110000,'reference from original initial, not current residual')
lines=(O/'case.bits.txt').read_text().splitlines();state=[struct.unpack('>d',bytes.fromhex(x))[0]for x in lines[3].split()];params=[struct.unpack('>d',bytes.fromhex(x))[0]for x in lines[5].split()]
ok(state==c['state']and params==c['parameters'],'wire state/parameters binary64 exact')
ok([struct.unpack('>d',bytes.fromhex(x))[0]for x in lines[6].split()]==[c[n]for n in('axial','reference','current_axial')],'wire controls exact')
cm=(O/'CMakeLists.txt').read_text();ok(cm.count('add_executable(')==1 and 'add_subdirectory'not in cm,'one standalone diagnostic executable')
ok('STATIC IMPORTED'in cm and 'libatlas_scalar_functions.a'in cm,'reuse existing scalar library without build')
ok('cxx_std_20'in cm and '-ffp-contract=off'in cm and '-DCMAKE_BUILD_TYPE=Release'in r['configure_argv'],'original Release/O3/C++20/ffpcontract flags')
ok(r['build_argv'][-4:]==['--target','atlas_derivative_trace','--parallel','1'],'one serial explicit target recipe')
(O/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'compiled_or_material_execution':False},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
