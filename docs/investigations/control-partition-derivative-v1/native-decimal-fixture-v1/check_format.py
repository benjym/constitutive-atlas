"""Static C++ string/framing and Python format-contract mocks. Never runs C++."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
import json,hashlib,re,sys,copy
D=Path(__file__).resolve().parent;O=D.parent/'native-decimal-reference-v1';sys.path.insert(0,str(O));import assess_saved as A
read=A.read;sha=A.sha;write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n');source=(D/'test_solver.cpp').read_text();overlay=read(D/'overlay.json');q=read(O/'requests.json');r=read(O/'reference.json');M=D/'format-mocks';M.mkdir(exist_ok=True)
# Decode the actual authored C++ JSON suffix rather than trusting manual escape counts.
match=re.search(r'std::cout<<decimal_payload<<("(?:\\.|[^"\\])*")',source);suffix=json.loads(match.group(1));assert json.loads('{"ad_hex":[]'+suffix)=={'ad_hex':[],'cpp_checks':{'rank13':True,'rotation':True,'other_models':True}}
# Lexical bracket balance after removing strings/chars/comments, not a compiler check.
clean=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/','',source,flags=re.S);stack=[];matching={')':'(',']':'[','}':'{'}
for c in clean:
 if c in '([{':stack.append(c)
 elif c in ')]}':assert stack and stack.pop()==matching[c]
assert not stack
# All frozen binding string literals in C++ decode to the exact oracle binding object.
chunk=source[source.index('// Frozen oracle/source identities'):source.index('    out<<",\\"build_binding_sha256')];parts=re.findall(r'out<<("(?:\\.|[^"\\])*");',chunk);parsed=json.loads('{'+''.join(json.loads(x)for x in parts)+'}');assert parsed==overlay['frozen_bindings']
def trimmed(x):
 h=float(x).hex();left,right=h.split('p');left=left.rstrip('0').rstrip('.')if'.'in left else left;return left+'p'+right
for x in [0.,-0.,1.,-1.,5e-11,2.5e-11,.65,160000.,.0001]:assert A.hexfloat(trimmed(x)).hex()==float(x).hex()
artifact=M/'not-an-executable.txt';artifact.write_text('Synthetic serialization fixture only. Never compiled or executed.\n');binding=dict(identity='md1997-decimal-native-build-binding-v1',purpose='synthetic-test-only',source_freeze_sha256=sha(D/'source-freeze.json'),fixture_sha256=sha(D/'test_solver.cpp'),generated_catalogue_sha256='2'*64,executable_sha256=sha(artifact),executable_path=str(artifact),working_directory=str(M),model_sha256=q['model_sha256']);write(M/'build-binding.json',binding)
base=copy.deepcopy({k:q[k]for k in ['layout','state_hex','previous_hex','loading_hex','parameters_hex','scales_hex']})
for k in ['state_hex','previous_hex','loading_hex','scales_hex']:base[k]=[trimmed(float.fromhex(x))for x in base[k]]
base['parameters_hex']={k:trimmed(float.fromhex(x))for k,x in base['parameters_hex'].items()}
z=[float.fromhex(x)for x in q['state_hex']];scales=[float.fromhex(x)for x in q['scales_hex']];endpoints=[]
for column in range(14):
 v=[float(i==column)for i in range(14)];h=5e-11 if 7<=column<=9 else 1e-6
 for level in range(2):
  step=h/2 if level else h;plus=z.copy();minus=z.copy()
  for j in range(14):plus[j]+=step*scales[j]*v[j];minus[j]-=step*scales[j]*v[j]
  for sign in [1,-1]:endpoints.append(dict(column=column,level=level,sign=sign,step_hex=trimmed(step),direction_hex=[trimmed(x)for x in v],state_hex=[trimmed(x)for x in(plus if sign==1 else minus)],domain=True,branch=True))
env=dict(identity='md1997-decimal-ad-export-v1',selector='md1997-decimal-fd-reference-v1',status='exported-unassessed',models=16,bindings={**parsed,'build_binding_sha256':sha(M/'build-binding.json')},base=base,endpoints=endpoints,ad_hex=[[trimmed(float(r['data']['120']['secants'][2*col][row]))for col in range(14)]for row in range(14)])
# Append the source-decoded C++ suffix and assess the resulting synthetic wire.
wire=json.dumps(env,separators=(',',':'))[:-1]+suffix;(M/'stdout').write_text(wire);(M/'stderr').write_text('')
process=dict(identity='md1997-decimal-direct-process-v1',purpose='synthetic-test-only',argv=[str(artifact)],cwd=str(M),returncode=0,stdout=dict(path=str(M/'stdout'),sha256=sha(M/'stdout')),stderr=dict(path=str(M/'stderr'),sha256=sha(M/'stderr')),selectors={'ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-decimal-fd-reference-v1','PYTHONOPTIMIZE':'0'},executable_sha256=sha(artifact));write(M/'process.json',process)
report=A.assess(O/'requests.json',O/'reference.json',M/'process.json',M/'build-binding.json',sha(M/'build-binding.json'));assert report['passed']is True and report['comparisons']==588 and report['purpose']=='synthetic-test-only';write(D/'format-mock-assessment.json',report)
# Source routing policy mocks: inspect exact guard order separately in check_source.py.
NEW='md1997-decimal-fd-reference-v1';OLD='md1997-source-admissible-v1';V5='explicit-gis20-occ-restart-duncan-v5';PAIR='MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5';HASH='MD Decimal build binding must be 64 lowercase hex characters'
allowed={'explicit-gis20-v2','explicit-gis20-occ-v3','explicit-gis20-occ-restart-v4',V5}
def routing(native,numerical,b):
 if native is not None and native not in allowed:return 'unknown native fixture profile'
 if numerical is not None and numerical not in [OLD,NEW]:return 'unknown numerical fixture profile'
 if numerical is not None and native!=V5:return PAIR
 if b is not None and numerical!=NEW:return 'MD Decimal build binding requires Decimal profile'
 if numerical==NEW and(type(b)is not str or re.fullmatch('[0-9a-f]{64}',b)is None):return HASH
 return 'new exported-unassessed route'if numerical==NEW else 'old route unchanged'
cases=[(None,NEW,None,PAIR),('explicit-gis20-occ-restart-v4',NEW,None,PAIR),(V5,NEW,None,HASH),(V5,NEW,'a'*64,'new exported-unassessed route'),(V5,OLD,None,'old route unchanged'),(None,None,None,'old route unchanged'),(V5,None,'a'*64,'MD Decimal build binding requires Decimal profile'),(V5,'unknown',None,'unknown numerical fixture profile'),('unknown',NEW,None,'unknown native fixture profile')]
for invalid in ['', 'a'*63,'a'*65,'A'*64,'g'*64]:cases.append((V5,NEW,invalid,HASH))
for native,num,b,expected in cases:assert routing(native,num,b)==expected
write(D/'format-checks.json',dict(passed=True,source_suffix_decoded=True,source_binding_literals_exact=True,lexical_balance=True,trimmed_hex_values_checked=9,synthetic_endpoint_records=56,synthetic_external_comparisons=588,routing_policy_mocks=len(cases),synthetic_only=True,cpp_compilation_performed=False,compiled_calls=0))
print('PASS static framing,56trimmedhex endpoint mocks,588syntheticcomparisons,14routingpolicy mocks; no C++ execution')
