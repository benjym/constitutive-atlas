"""Exact test-only overlay; never compiles or executes C++."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
import json,hashlib,difflib
D=Path(__file__).resolve().parent;C=D.parent;O=C/'native-decimal-reference-v1';S=Path('/private/tmp/atlas-md1997-decimal-fixture-v1/source');BASE=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
src=(BASE/'tests/test_solver.cpp').read_text();r=read(O/'reference.json');bindings={k:r[k]for k in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256']};bindings.update(request_sha256=sha(O/'requests.json'),reference_sha256=sha(O/'reference.json'))
statements=[]
for i,(name,value)in enumerate(bindings.items()):
 key=(','if i else'')+json.dumps(name)+':'+json.dumps(value);statements.append('    out<<'+json.dumps(key)+';')
helper=(D/'export_helpers.cpp.txt').read_text().replace('    /* FROZEN_BINDINGS */','\n'.join(statements))
replacements=[]
def edit(a,b):
 global src
 assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b,1);replacements.append(dict(original=a,replacement=b))
edit('#include <stdexcept>','#include <stdexcept>\n#include <sstream>\n#include <iomanip>\n#include <locale>')
edit('const std::vector<atlas::Jet>&r){\n    const auto branch=', 'const std::vector<atlas::Jet>&r,bool decimal_reference=false){\n    const auto branch=')
edit('for(int j=0;j<14;++j){atlas::State v(14,0.);v[j]=1;direction(v,j>=7&&j<=9?5e-11:1e-6);}', 'if(!decimal_reference)for(int j=0;j<14;++j){atlas::State v(14,0.);v[j]=1;direction(v,j>=7&&j<=9?5e-11:1e-6);}')
edit('\nint main(){','\n'+helper+'int main(){')
edit('const bool md_admissible=numerical_profile!=nullptr;', '''const bool md_decimal=numerical_profile&&std::string(numerical_profile)=="md1997-decimal-fd-reference-v1";
        const bool md_admissible=numerical_profile!=nullptr;''')
edit('require(!numerical_profile||std::string(numerical_profile)=="md1997-source-admissible-v1","unknown numerical fixture profile");', '''require(!numerical_profile||std::string(numerical_profile)=="md1997-source-admissible-v1"||md_decimal,"unknown numerical fixture profile");
        const char*decimal_binding=std::getenv("ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256");
        std::string decimal_payload;''')
edit('            require(count==1,"MD numerical fixture requires exactly one MD model");\n        }', '            require(count==1,"MD numerical fixture requires exactly one MD model");\n        }\n        require(!decimal_binding||md_decimal,"MD Decimal build binding requires Decimal profile");\n        require(!md_decimal||md_decimal_binding_valid(decimal_binding),"MD Decimal build binding must be 64 lowercase hex characters");\n        if(md_decimal)require(atlas::models().size()==16,"MD Decimal profile requires exactly 16 models");')
edit('std::cout<<(md_admissible?', 'if(!md_decimal)std::cout<<(md_admissible?')
edit('md_fixture_derivatives(int(model),z,zn,p,scales,de,r);', '''if(md_decimal){require(decimal_payload.empty(),"MD Decimal duplicate model export");decimal_payload=md_decimal_export(int(model),z,zn,p,scales,de,r,decimal_binding);}
                md_fixture_derivatives(int(model),z,zn,p,scales,de,r,md_decimal);''')
edit('std::cout<<"AD Jacobians, fixed-frame rotation covariance and integration-settings checks passed\\n";','if(md_decimal){require(!decimal_payload.empty(),"MD Decimal missing model export");std::cout<<decimal_payload<<",\\"cpp_checks\\":{\\"rank13\\":true,\\"rotation\\":true,\\"other_models\\":true}}\\n";}\n        else std::cout<<"AD Jacobians, fixed-frame rotation covariance and integration-settings checks passed\\n";')
p=S/'tests/test_solver.cpp';p.write_text(src);(D/'test_solver.cpp').write_text(src)
reverse=src
for change in reversed(replacements):
 assert reverse.count(change['replacement'])==1;reverse=reverse.replace(change['replacement'],change['original'],1)
assert reverse==(BASE/'tests/test_solver.cpp').read_text()
(D/'overlay.json').write_text(json.dumps(dict(identity='md1997-decimal-fixture-exact-overlay-v1',changes=replacements,base_sha256=sha(BASE/'tests/test_solver.cpp'),new_sha256=sha(p),inverse_exact=True,frozen_bindings=bindings),indent=2)+'\n');(D/'test_solver.cpp.diff').write_text(''.join(difflib.unified_diff((BASE/'tests/test_solver.cpp').read_text().splitlines(True),src.splitlines(True),fromfile='base/tests/test_solver.cpp',tofile='decimal/tests/test_solver.cpp')))
print(str(len(replacements))+' exact overlay edits; inverse restores old source')
