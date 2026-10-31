from pathlib import Path
import hashlib,json,re,struct,sys
stage=Path(__file__).resolve().parent
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/private/tmp/atlas-explicit-laboratory-controls-v1')
files=['proposed/cpp/main.cpp','proposed/cpp/include/atlas/solver.hpp','check.mjs','CONTRACT.md','POLICY.md','source_check.py','prior/solver.hpp']
checks=[]
def test(name,ok):
 checks.append({'name':name,'passed':bool(ok)})
 if not ok:raise AssertionError(name)
main=(source/files[0]).read_text(); solver=(source/files[1]).read_text()
# Independent grammar model. This is a source contract check, never C++ execution.
def decode(wire):
 if not 33<=len(wire)<=85016:raise ValueError()
 items=wire.split(',')
 if not 2<=len(items)<=5001:raise ValueError()
 out=[]
 for token in items:
  if re.fullmatch('[0-9a-f]{16}',token) is None:raise ValueError()
  b=int(token,16)
  if b&0x7ff0000000000000==0x7ff0000000000000:raise ValueError()
  out.append(struct.unpack('>d',b.to_bytes(8,'big'))[0])
 return out
z='0000000000000000'; sub='0000000000000001'; negz='8000000000000000'
for i,wire in enumerate([z+','+z,negz+','+sub+','+'8000000000000001',','.join([z]*5001)]):
 vals=decode(wire)
 test('valid_wire_'+str(i),len(vals)==len(wire.split(',')))
 test('bits_roundtrip_'+str(i),','.join(struct.pack('>d',x).hex() for x in vals)==wire)
for i,wire in enumerate(['',z,z+',',z+',0',z+','+'0'*17,z+','+'7FF0000000000000',z+','+'7ff0000000000000',z+','+'fff0000000000000',z+','+'7ff0000000000001',z+','+'7ff8000000000000',z+',,'+z,' '+z+','+z,z+','+z+'\n',','.join([z]*5002),z+','+z+'\0suffix']):
 try:decode(wire)
 except ValueError:test('invalid_wire_'+str(i),True)
 else:test('invalid_wire_'+str(i),False)
# Preserve the original source-level witness: c_str -> string discards suffix.
full=(z+','+sub).encode()+b'\0unparsed bytes'
prefix=full.split(b'\0',1)[0].decode()
test('nul_full_contract_rejects',b'\0' in full)
test('nul_c_string_prefix_valid',len(decode(prefix))==2)
# Proof of loop preservation using literal reversal, without executing solver.
reversed=solver[:solver.index('\n// Legacy producers')].removesuffix('\n')+'\n}\n'
reversed=reversed.replace('inline Run run_protocol_impl(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings,const State*controls){','inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){')
reversed=reversed.replace('Point committed;committed.control=controls?controls->front():0.;committed.state=initial;','Point committed;committed.state=initial;')
reversed=reversed.replace('double control=controls?(*controls)[i]:(cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps);','double control=cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps;')
test('original_controller_loop_exact',reversed==(source/'prior/solver.hpp').read_text())
test('finite_bits_rejected_before_memcpy',main.index('bits&0x7ff0000000000000ULL')<main.index('double value;std::memcpy'))
test('binary64_static_requirements',all(x in main for x in ['is_iec559','digits==53','radix==2']))
test('new_api_export_annotation','extern "C" ATLAS_EXPORT const char* atlas_run_controls_with_settings' in main)
test('delta_shared_controller','control-previous.control' in solver)
test('first_sign_preserved','committed.control=controls?controls->front():0.' in solver)
test('cli_rejects_embedded_nul', "controls.find('\\0')!=std::string::npos" in main)
# Size arithmetic is exact and integer conversion bounded.
test('maximum_wire_length',5001*16+5000==85016)
test('minimum_wire_length',2*16+1==33)
test('size_guard_before_front','controls.size()<2||controls.size()>5001||controls.front()!=0' in solver)
report={'scope':'source-only; no candidate calls/builds/Atlas imports','checks':len(checks),'passed':all(c['passed'] for c in checks),'items':checks,'nul_witness':{'full_file_hex':full.hex(),'c_string_prefix':prefix,'interpretation':'original CLI truncation witness; fixed CLI must reject before C ABI'},'source_pins':{x:hashlib.sha256((source/x).read_bytes()).hexdigest() for x in files}}
(stage/'source-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':report['checks']}))
