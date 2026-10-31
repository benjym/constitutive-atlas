from pathlib import Path
import hashlib,json
stage=Path(__file__).parent;root=Path('/Users/bmar5496/code/constitutive-atlas')
a=(stage/'prior/solver.hpp').read_text();b=(stage/'proposed/cpp/include/atlas/solver.hpp').read_text()
b=b[:b.index('\n// Legacy producers')].removesuffix('\n')+ '\n}\n'
b=b.replace('inline Run run_protocol_impl(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings,const State*controls){','inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){')
b=b.replace('Point committed;committed.control=controls?controls->front():0.;committed.state=initial;','Point committed;committed.state=initial;')
b=b.replace('double control=controls?(*controls)[i]:(cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps);','double control=cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps;')
if b!=a:raise RuntimeError('original loop reversal mismatch')
print(json.dumps({'passed':True,'original_header_sha256':hashlib.sha256(a.encode()).hexdigest(),'exact_original_loop_reversal':True}))
