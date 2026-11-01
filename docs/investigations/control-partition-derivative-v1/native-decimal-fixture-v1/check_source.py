"""Static protection and inverse proof. No C++ compilation/execution."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
import json,hashlib,ast
D=Path(__file__).resolve().parent;C=D.parent;S=Path('/private/tmp/atlas-md1997-decimal-fixture-v1/source');BASE=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read(D/'inputs.json').items():assert sha(Path(n))==h,n
old=(BASE/'tests/test_solver.cpp').read_text();new=(S/'tests/test_solver.cpp').read_text();overlay=read(D/'overlay.json');assert sha(S/'tests/test_solver.cpp')==overlay['new_sha256']==sha(D/'test_solver.cpp')
r=new
for change in reversed(overlay['changes']):assert r.count(change['replacement'])==1;r=r.replace(change['replacement'],change['original'],1)
assert r==old and overlay['base_sha256']==sha(BASE/'tests/test_solver.cpp')
base=read(D/'base-source-freeze.json')['files'];current={str(p.relative_to(S)):sha(p)for p in S.rglob('*')if p.is_file()};assert len(base)==len(current)==594 and [n for n in base if base[n]!=current[n]]==['tests/test_solver.cpp']
# Every old numerical inequality, lambda, rank13 direction and later check stays exact.
def part(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
assert part(old,'    auto direction=[&]','    // Full14')==part(new,'    auto direction=[&]','    // Full14')
rank='    // Independent rank13';end='\n}\n';a=old.index(rank);b=new.index(rank);assert old[a:old.index(end,a)+len(end)]==new[b:new.index(end,b)+len(end)]
assert part(old,'            }else for(int j=0;j<n;++j)','        // A fixed 90-degree')==part(new,'            }else for(int j=0;j<n;++j)','        // A fixed 90-degree')
assert part(old,'        // A fixed 90-degree','        std::cout<<"AD Jacobians')==part(new,'        // A fixed 90-degree','        if(md_decimal){require(!decimal_payload.empty()')
assert part(old,'        if(md_admissible){','        const bool explicit_fixtures')==part(new,'        if(md_admissible){','        require(!decimal_binding')
assert new.index('MD1997 numerical fixture requires')<new.index('MD Decimal build binding requires')
assert new.count('std::cout')==3 and 'if(!md_decimal)std::cout' in new
assert new.index('"protocol failed to propagate material settings"')<new.index('std::cout<<decimal_payload')
assert 'out<<'not in part(new,'        for(size_t model=0;','        // A fixed 90-degree') # no output before all tests
assert 'if(!decimal_reference)for(int j=0;j<14' in new
assert 'md_fixture_derivatives(int(model),z,zn,p,scales,de,r,md_decimal);'in new
assert 'md_decimal_hex(out,r[row].d[column])'in new
assert 'plus[j]+=step*scales[j]*direction[j];minus[j]-=step*scales[j]*direction[j];'in new
assert 'md_decimal_vector(out,sign==1?plus:minus)'in new
for key,value in overlay['frozen_bindings'].items():assert value in new
for p in D.glob('*.py'):ast.parse(p.read_text())
(D/'source-freeze.json').write_text(json.dumps(dict(identity='md1997-decimal-native-fixture-source-v1',directory=str(S),files=current),indent=2)+'\n')
result=dict(identity='md1997-decimal-native-static-checks-v1',passed=True,files=594,changed_only=['tests/test_solver.cpp'],inverse_exact=True,old_direction_lambda_exact=True,rank13_exact=True,other15_derivative_and_full_rotation_settings_blocks_exact=True,pairing_guard_before_binding=True,actual_scaled_jet_and_native_endpoints_dataflow_checked=True,buffered_single_newmode_stdout_after_all_checks=True,cpp_compilation_performed=False,compiled_calls=0)
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
