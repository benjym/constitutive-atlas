from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[3];p=Path(__file__).parent;o=p/'actual-root-v1';o.mkdir(exist_ok=False)
b=Path('/private/tmp/atlas-common-scalar-functions-v1');native=b/'actual-root-native-v1';wasm=b/'actual-root-wasm-v1'
commands={}
for backend,d in [('native',native),('wasm',wasm)]:
 commands[backend+'_configure']=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(r),'-B',str(d),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
 for target in (['atlas_solver','atlas_numerical_tests','atlas_recorded_tests','atlas_scalar_probe'] if backend=='native' else ['atlas_solver','atlas_scalar_probe']):commands[backend+'_build_'+target]=['cmake','--build',str(d),'--target',target,'--parallel','1']
gates=json.loads((p/'engine-gates-v2.json').read_text())
for row in gates.values():
 row['command']=[x.replace('engine-native-v1','actual-root-native-v1').replace('engine-wasm-v1','actual-root-wasm-v1').replace('engine-results-v1','actual-root-v1') for x in row['command']]
gates['scalar_native']={'command':['python3','-B','tools/test_scalar_functions.py',str(native/'libatlas_scalar_probe.dylib'),'--output-dir',str(o/'scalar-native')]}
gates['scalar_wasm_collect']={'command':['node','tools/collect_scalar_functions_wasm.mjs',str(wasm/'atlas_scalar_probe.mjs'),str(o/'scalar-wasm-raw.json')]}
gates['scalar_wasm_assess']={'command':['python3','-B','tools/check_scalar_functions.py',str(o/'scalar-wasm-raw.json'),str(o/'scalar-wasm-assessment.json')]}
for name,d in [('commands',commands),('gates',gates)]: (o/(name+'.json')).write_text(json.dumps(d,indent=2)+'\n')
print('Prepared exact-root commands; source freeze after installation, before configure/build/execution. Same frozen engine+391scalar gates.')
