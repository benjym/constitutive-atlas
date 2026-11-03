"""One-shot test-fixture installation; no constitutive runtime edits."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
old='explicit-gis20-occ-restart-duncan-v5';new='explicit-gis20-occ-restart-duncan-sclay1-v6'
for name in ['tests/test_solver.cpp','tests/test_recorded.cpp']:
 p=ROOT/name;s=p.read_text();s=s.replace('std::string(profile)=="'+old+'"','(std::string(profile)=="'+old+'"||std::string(profile)=="'+new+'")');p.write_text(s)
p=ROOT/'tests/test_solver.cpp';s=p.read_text();s=s.replace('const bool explicit_fixtures=profile!=nullptr;', 'const bool explicit_fixtures=profile!=nullptr;\n        const bool sclay_fixture=profile&&std::string(profile)=="'+new+'";')
needle='            const int n=int(z.size());'
insert='''            int fabric_offset=-1;
            if(sclay_fixture&&atlas::models()[model].id=="s-clay1"){
                for(const auto& f:atlas::models()[model].fields)if(f.name=="fabric"&&f.size==6)fabric_offset=f.offset;
                require(fabric_offset>=0,"S-CLAY1 fabric field absent");
                auto invalid=z;invalid[fabric_offset]+=1e-6;atlas::State values;atlas::Sym<double> probe;
                require(!atlas::evaluate_model(int(model),invalid,zn,probe,p,values),"nondeviatoric fabric probe accepted");
            }
'''
assert s.count(needle)==1;s=s.replace(needle,insert+needle)
needle='                require(atlas::evaluate_model(int(model),plus,zn,de,p,rp)'
insert='''                const bool fabric_normal=fabric_offset>=0&&j>=fabric_offset&&j<fabric_offset+3;
                if(fabric_normal)for(int k=0;k<3;++k){plus[fabric_offset+k]-=h*scales[j]/3;minus[fabric_offset+k]+=h*scales[j]/3;}
''';assert s.count(needle)==1;s=s.replace(needle,insert+needle)
needle='ad=r[i].d[j];require('
s=s.replace(needle,'ad=r[i].d[j];if(fabric_normal)for(int k=0;k<3;++k)ad-=scales[j]*r[i].d[fabric_offset+k]/(3*scales[fabric_offset+k]);require(');assert 'if(fabric_normal)for' in s
needle='            atlas::put_tensor(zr,0,rotate(atlas::tensor_from(z,0)));'
insert='''            int rotated_fabric=-1;
            if(sclay_fixture&&atlas::models()[m].id=="s-clay1"){
                z=atlas::initial_state(int(m));zr=z;
                for(const auto& f:atlas::models()[m].fields)if(f.name=="fabric"&&f.size==6)rotated_fabric=f.offset;
                require(rotated_fabric>=0,"S-CLAY1 rotation fabric absent");
                atlas::put_tensor(zr,rotated_fabric,rotate(atlas::tensor_from(z,rotated_fabric)));
            }
''';assert s.count(needle)==1;s=s.replace(needle,insert+needle)
needle='            auto want=rotate(atlas::tensor_from(a.state,0));for(int i=0;i<6;++i)require(std::abs(want.v[i]-b.state[i])<.01,"fixed-frame rotation covariance failed");'
assert s.count(needle)==1;s=s.replace(needle,needle+'''
            if(rotated_fabric>=0){
                const auto fabric_want=rotate(atlas::tensor_from(a.state,rotated_fabric));
                for(int i=0;i<6;++i)require(std::abs(fabric_want.v[i]-b.state[rotated_fabric+i])<1e-9,"fabric rotation covariance failed");
                for(const auto& f:atlas::models()[m].fields)if(f.size==1&&!f.transient)require(std::abs(a.state[f.offset]-b.state[f.offset])<=2e-8*std::max(1.,std::abs(a.state[f.offset])),"scalar history rotation covariance failed");
            }
''');p.write_text(s)
p=ROOT/'tools/check_native_fixture_contracts.py';s=p.read_text();needle="RAMBERG_HASH='c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2'";assert needle in s;s=s.replace(needle,needle+"\nSCLAY='s-clay1'\nSCLAY_HASH='2d1518c1aee44d9adec35229adc83b32a9f39d9175f307c8ddfd90cdfbd1caec'")
s=s.replace('    if RAMBERG in definitions:\n',"    if SCLAY in definitions:\n        assert definitions=={**PRIOR_THIRTEEN,DUNCAN:DUNCAN_HASH,RAMBERG:RAMBERG_HASH,SCLAY:SCLAY_HASH}, 'unqualified strict sixteen-model catalogue'\n    elif RAMBERG in definitions:\n",1)
s=s.replace("return ('current-fifteen Ramberg/Duncan/OCC'", "return ('current-sixteen SCLAY1/Ramberg/Duncan/OCC' if SCLAY in definitions else 'current-fifteen Ramberg/Duncan/OCC'");p.write_text(s)
p=ROOT/'.github/workflows/qualification.yml';s=p.read_text();assert old in s;s=s.replace(old,new+' # includes '+old+' semantics')
# Shell command values cannot contain inline prose; retain the compatibility note separately.
s=s.replace(new+' # includes '+old+' semantics ctest',new+' ctest').replace('ATLAS_NATIVE_FIXTURES: '+new+' # includes '+old+' semantics','ATLAS_NATIVE_FIXTURES: '+new)
s=s.replace('    - name: Native checks and full exact archival replay','    # v6 inherits explicit-gis20-occ-restart-duncan-v5 and adds constrained S-CLAY1 fixtures.\n    - name: Native checks and full exact archival replay');p.write_text(s)
print('Installed distinct v6 native fixture; original profiles and gates retained')
