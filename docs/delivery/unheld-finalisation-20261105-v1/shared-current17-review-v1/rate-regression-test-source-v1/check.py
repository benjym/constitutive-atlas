from pathlib import Path
import json,hashlib,re,struct,difflib
N=Path('docs/delivery/unheld-finalisation-20261105-v1');P=N/'rate-control-regression-test-plan-v1';Q=N/'shared-current17-review-v1/rate-regression-test-source-v1';old=Path('/private/tmp/atlas-baseline-delivery-20261105/source/tests/test_solver.cpp');new=P/'proposed/tests/test_solver.cpp';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
g=json.loads((P/'GATES.json').read_text());ck('exact preimage hash',sha(old)==g['preimage_sha256']=='5df371dd65eced3befa16f7790cabe0eec7150c1910106e8d7496b5055a7fa00');ck('exact candidate hash',sha(new)==g['sha256']=='da2b0ed473cdb186fafac04033350b17ff25d287a804abb1c63cb46addd88b90')
a=old.read_text();b=new.read_text();ops=[x for x in difflib.SequenceMatcher(None,a.splitlines(True),b.splitlines(True),autojunk=False).get_opcodes()if x[0]!='equal'];ck('single insertion no replace/delete',len(ops)==1 and ops[0][0]=='insert')
_,i,j,k,l=ops[0];insert=''.join(b.splitlines(True)[k:l]);ck('insertion reversal exact full bytes',''.join(b.splitlines(True)[:k]+b.splitlines(True)[l:])==a)
ck('all old require assertions byteexact',[x for x in a.splitlines()if 'require('in x]==[x for x in (b.replace(insert,'',1)).splitlines()if 'require('in x])
case=json.loads((N/'current17-igs97-native-replay-v2/plan.json').read_text());doc=json.loads(Path(case['input_document']).read_text());spec=doc['specification']
ck('exact public input document',sha(Path(case['input_document']))==case['input_document_sha256']=='85fe1b386b804a632815e881561482a9c06536b07f09bb3670b8dac85fedbf49')
for name,want in [('edited_parameters',spec['parameters']),('edited_initial',spec['initial'])]:
 text=re.search(r'const atlas::State '+name+r'=\{([^}]+)\}',insert).group(1);actual=[float(v)for v in text.split(',')];ck('exact binary64 '+name,[struct.pack('>d',x)for x in actual]==[struct.pack('>d',x)for x in want])
ck('exact model protocol target steps cycles','id=="hypoplastic-sand-igs97"'in insert and 'edited_parameters,1,.01,100,0,edited_settings)'in insert and spec['model']=='hypoplastic-sand-igs97' and (spec['protocol'],spec['target'],spec['steps'],spec['cycles'])==(1,.01,100,0))
settings=(N/'current17-runtime-source-v1/source/cpp/include/atlas/settings.hpp').read_text()
for field,want in spec['integration_settings'].items():
 if field in ('version','norm'):continue
 actual=float(re.search(r'\b'+field+r'=([^;]+);',settings).group(1));ck('default setting '+field,actual==want)
ck('no overridden settings','const atlas::IntegrationSettings edited_settings{};'in insert)
controls=spec['loading']['controls_bits'];bits=lambda x:struct.pack('>d',x).hex();ck('all101 exact IEEE control bits',[bits(.01*float(i)/100.)for i in range(101)]==controls)
ck('full101 success gate','require(edited_run.ok&&edited_run.points.size()==101,'in insert)
ck('initial preservation gate','require(edited_run.points.front().state==edited_initial,'in insert)
ck('all states finite and full13','require(point.state.size()==13&&atlas::finite(point.state),'in insert)
ck('exact generated control gate','require(point.control==.01*double(i)/100.,'in insert)
ck('existing controller relative residual bound','require(std::abs(.5*(point.state[1]+point.state[2])-110000)<110000*1e-8,'in insert and 'std::abs(residual)<std::max(1.,std::abs(reference))*1e-8'in (N/'current17-runtime-source-v1/source/cpp/include/atlas/solver.hpp').read_text())
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_calls':0,'inserted_lines':l-k},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks)}))
