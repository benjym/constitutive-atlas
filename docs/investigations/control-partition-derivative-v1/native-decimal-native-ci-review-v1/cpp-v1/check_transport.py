"""Source literal decoding and frozen synthetic saved-data replay only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,re,hashlib,importlib.util
D=Path(__file__).resolve().parent;C=D.parent.parent;A=C/'native-decimal-fixture-v1';O=C/'native-decimal-reference-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
for n,v in read(A/'inputs.json').items():ck('frozen dependency '+n,sha(Path(n))==v)
text=(A/'test_solver.cpp').read_text();literal=re.search(r'std::cout<<decimal_payload<<("(?:\\.|[^"\\])*")',text).group(1);suffix=json.loads(literal);ck('actual complete JSON suffix',json.loads('{"ad_hex":[]'+suffix)=={'ad_hex':[],'cpp_checks':{'rank13':True,'rotation':True,'other_models':True}})
chunk=text[text.index('// Frozen oracle/source identities'):text.index('    out<<",\\"build_binding_sha256')];literals=re.findall(r'out<<("(?:\\.|[^"\\])*");',chunk);bindings=json.loads('{'+''.join(json.loads(x)for x in literals)+'}');ref=read(O/'reference.json');expected={k:ref[k]for k in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256','request_sha256']};expected['reference_sha256']=sha(O/'reference.json');ck('all frozen binding literals exact',bindings==expected)
sys.path.insert(0,str(O));spec=importlib.util.spec_from_file_location('cpp_review_assessor',O/'assess_saved.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);M=A/'format-mocks';result=m.assess(O/'requests.json',O/'reference.json',M/'process.json',M/'build-binding.json',sha(M/'build-binding.json'));ck('explicit synthetic purpose only',result['purpose']=='synthetic-test-only');ck('synthetic588 result allpass',result['passed']is True and result['comparisons']==len(result['results'])==588 and result['failures']==[]and all(x['passed']is True for x in result['results']));ck('frozen format result identical',result==read(A/'format-mock-assessment.json'))
# Byte recovery already covers all unaffected code. Explicit slices make inherited protections easy to assess.
base=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source/tests/test_solver.cpp').read_text()
for name,start,end in [('direction lambda','    auto direction=','    // Full14 ambient'),('rank13','    // Independent rank13','\n}\n'),('other15 derivatives','            }else for(int j=0;j<n;++j)','        // A fixed 90-degree'),('rotation/settings','        // A fixed 90-degree','        std::cout<<"AD Jacobians')]:
 oldstart=base.index(start);oldend=base.index(end,oldstart);newstart=text.index(start);newend=text.index(end,newstart)if name!='rotation/settings'else text.index('        if(md_decimal){require(!decimal_payload.empty()',newstart);ck('unchanged '+name,base[oldstart:oldend]==text[newstart:newend])
ck('closed binding guard source','if(!value||std::string(value).size()!=64)return false;'in text and "(*c>='0'&&*c<='9')||(*c>='a'&&*c<='f')"in text)
ck('no original positive output new mode','if(!md_decimal)std::cout<<'in text and 'else std::cout<<"AD Jacobians'in text)
ck('status explicitly unassessed','exported-unassessed'in text)
print(json.dumps({'identity':'independent-decimal-cpp-transport-source-review-v1','checks':len(checks),'check_names':checks,'format_evidence':'static and synthetic only; no compiled C++ observations','builds':0,'compiled_calls':0},indent=2))
