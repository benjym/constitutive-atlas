"""Exact source582 clone and single-file prospective fixture implementation; no compilation."""
import json,hashlib,difflib
from pathlib import Path
D=Path(__file__).resolve().parent; R=Path('/private/tmp/atlas-md1997-native-fixture-v1/source'); S=Path('/private/tmp/atlas-control-partition-v1/source')
F=Path('docs/investigations/control-partition-derivative-v1/implementation-v1/source-freeze.json')
sha=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads(F.read_text()); assert len(f['source_files'])==582
assert not R.exists(),'fresh clone required'
for name,digest in f['source_files'].items():
 b=(S/name).read_bytes();assert sha(b)==digest,name
 q=R/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
old=(R/'tests/test_solver.cpp').read_text(); new=old
helper=r'''
// Source-only fixture diagnostics: branch signs, singular margins and complete
// declared residual domain. This never substitutes for generated evaluation.
std::array<bool,4> md_fixture_branch(const atlas::State& z,const atlas::State& p){
    require(z.size()==14&&p.size()==17&&atlas::finite(z)&&atlas::finite(p),"MD fixture finite layout");
    const double pressure=(z[0]+z[1]+z[2])/3, S=std::sqrt(2./3.);
    require(pressure>0&&z[6]>0&&z[13]>=-1e-10&&std::abs(z[7]+z[8]+z[9])<=1e-10&&p[5]>p[14]&&p[6]>p[14],"MD fixture domain");
    std::array<double,6> n{};double rr=0;
    for(int i=0;i<6;++i){n[i]=(z[i]-(i<3?pressure:0))/pressure-z[7+i];rr+=n[i]*n[i];}
    require(std::isfinite(rr)&&rr>0,"MD fixture normal branch");
    for(double&v:n)v/=std::sqrt(rr);
    const double q=std::sqrt(2.);double N[3][3]={{n[0],n[3]/q,n[5]/q},{n[3]/q,n[1],n[4]/q},{n[5]/q,n[4]/q,n[2]}};
    double cubic=0;for(int i=0;i<3;++i)for(int j=0;j<3;++j)for(int k=0;k<3;++k)cubic+=N[i][j]*N[j][k]*N[k][i];
    const double angular=std::sqrt(6.)*cubic,psi=z[6]-p[8]+p[7]*std::log(pressure/p[1]);
    auto g=[&](double c){double denominator=1+c-(1-c)*angular;require(std::isfinite(denominator)&&denominator>0,"MD fixture angular singularity");return 2*c/denominator;};
    const double gc=g(p[6]/p[5]),gb=g(p[10]/p[9]),gd=g(p[12]/p[11]);
    double an=0;for(int i=0;i<6;++i)an+=z[7+i]*n[i];
    const double abc=p[5]+p[9]*std::max(-psi,0.)-p[14];
    const double bn=S*(gc*p[5]+gb*p[9]*std::max(-psi,0.)-p[14])-an;
    const double draw=p[15]*(S*(gc*p[5]+gd*p[11]*psi-p[14])-an);
    const double yield=(pressure*std::sqrt(rr)-S*p[14]*pressure)/p[1];
    require(std::isfinite(psi)&&std::isfinite(bn)&&std::isfinite(draw)&&abc>0&&2*S*abc>std::abs(bn),"MD fixture hardening domain");
    require(psi!=0&&bn!=0&&draw!=0&&std::isfinite(yield)&&std::hypot(z[13],yield)>0,"MD fixture nondifferentiable branch");
    return {rr>0,psi>0,bn>0,draw>0};
}
void md_fixture_derivatives(int model,const atlas::State&z,const atlas::State&zn,const atlas::State&p,const atlas::State&scales,const atlas::Sym<double>&de,const std::vector<atlas::Jet>&r){
    const auto branch=md_fixture_branch(z,p);require(r.size()==14&&scales.size()==14,"MD derivative layout");
    auto direction=[&](const atlas::State&v,double h){
        std::array<atlas::State,2> fd;
        for(int level=0;level<2;++level){
            const double step=level?h/2:h;auto plus=z,minus=z;
            for(int j=0;j<14;++j){plus[j]+=step*scales[j]*v[j];minus[j]-=step*scales[j]*v[j];}
            require(md_fixture_branch(plus,p)==branch&&md_fixture_branch(minus,p)==branch,"MD FD branch changed");
            atlas::State rp,rm;require(atlas::evaluate_model(model,plus,zn,de,p,rp)&&atlas::evaluate_model(model,minus,zn,de,p,rm),"MD FD outside domain");
            require(rp.size()==14&&rm.size()==14&&atlas::finite(rp)&&atlas::finite(rm),"MD FD residual finite layout");
            fd[level].resize(14);
            for(int i=0;i<14;++i){double ad=0;for(int j=0;j<14;++j)ad+=r[i].d[j]*v[j];
                fd[level][i]=(rp[i]-rm[i])/(2*step);
                require(std::isfinite(ad)&&std::isfinite(fd[level][i])&&std::abs(fd[level][i]-ad)<3e-5*std::max({1.,std::abs(fd[level][i]),std::abs(ad)}),"MD AD/FD residual Jacobian mismatch");}
        }
        for(int i=0;i<14;++i)require(std::abs(fd[0][i]-fd[1][i])<1.5e-5*std::max({1.,std::abs(fd[0][i]),std::abs(fd[1][i])}),"MD FD h/h2 mismatch");
    };
    // Full14 ambient implementation columns, including the finite trace band.
    for(int j=0;j<14;++j){atlas::State v(14,0.);v[j]=1;direction(v,j>=7&&j<=9?5e-11:1e-6);}
    // Independent rank13 source tangent; no isotropic-alpha source claim.
    for(int j: {0,1,2,3,4,5,6,13}){atlas::State v(14,0.);v[j]=1;direction(v,1e-6);}
    atlas::State v(14,0.);v[7]=1/std::sqrt(2.);v[8]=-v[7];direction(v,1e-6);
    v.assign(14,0.);v[7]=v[8]=1/std::sqrt(6.);v[9]=-2/std::sqrt(6.);direction(v,1e-6);
    for(int j: {10,11,12}){v.assign(14,0.);v[j]=1;direction(v,1e-6);}
}
'''
new=new.replace('int main(){',helper+'\nint main(){',1)
anchor='        const bool explicit_fixtures=profile!=nullptr;'
selector=r'''        const char* numerical_profile=std::getenv("ATLAS_NUMERICAL_FIXTURES");
        const bool md_admissible=numerical_profile!=nullptr;
        require(!numerical_profile||std::string(numerical_profile)=="md1997-source-admissible-v1","unknown numerical fixture profile");
        if(md_admissible){
            require(profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5","MD numerical fixture requires exact v5 pairing");
            int count=0;
            for(size_t m=0;m<atlas::models().size();++m)if(atlas::models()[m].id=="manzari-dafalias-1997-constant-m-be-v1"){
                ++count;const auto&fields=atlas::models()[m].fields;
                require(fields.size()==4&&fields[0].name=="sigma"&&fields[0].offset==0&&fields[0].size==6&&fields[1].name=="e"&&fields[1].offset==6&&fields[1].size==1&&fields[2].name=="alpha"&&fields[2].offset==7&&fields[2].size==6&&fields[3].name=="gamma"&&fields[3].offset==13&&fields[3].size==1&&fields[3].multiplier,"MD numerical fixture requires exact14 layout");
                const atlas::State expected={100000,160000,31400000,31400000,.6,1.14,1.14,.025,.8,3.975,2.,4.2,.07,1200,.05,2.64,.65};
                require(atlas::initial_state(int(m)).size()==14&&atlas::default_parameters(int(m))==expected,"MD numerical fixture parameter/layout identity");
            }
            require(count==1,"MD numerical fixture requires exactly one MD model");
        }
'''
new=new.replace(anchor,selector+anchor,1)
new=new.replace('            for(int j=0;j<n;++j){','            if(md_admissible&&atlas::models()[model].id=="manzari-dafalias-1997-constant-m-be-v1"){\n                md_fixture_derivatives(int(model),z,zn,p,scales,de,r);\n            }else for(int j=0;j<n;++j){',1)
anchor='            atlas::Sym<double>de;de.v={.0001,-.00002,.00001,.00003,.00001,-.00001};auto zr=z;'
new=new.replace(anchor,'            const bool md_rotation=md_admissible&&atlas::models()[m].id=="manzari-dafalias-1997-constant-m-be-v1";\n            if(md_rotation){z[0]=640500;z[1]=639500;z[2]=640000;z[3]=100;z[4]=z[5]=0;}\n'+anchor,1)
anchor='            atlas::IntegrationSettings fixture_settings;'
new=new.replace(anchor,'            if(md_rotation){require(atlas::domain(int(m),z,p,true)&&atlas::domain(int(m),zr,p,true),"MD rotation initial domain");md_fixture_branch(z,p);md_fixture_branch(zr,p);}\n'+anchor,1)
anchor='            auto want=rotate(atlas::tensor_from(a.state,0));'
addition='''            if(md_rotation){
                require(a.state.size()==14&&b.state.size()==14&&atlas::finite(a.state)&&atlas::finite(b.state)&&atlas::domain(int(m),a.state,p)&&atlas::domain(int(m),b.state,p),"MD rotation final finite domain layout");
                require(md_fixture_branch(a.state,p)==md_fixture_branch(z,p)&&md_fixture_branch(b.state,p)==md_fixture_branch(zr,p),"MD rotation source branch changed");
                auto alpha=rotate(atlas::tensor_from(a.state,7));for(int i=0;i<6;++i)require(std::abs(alpha.v[i]-b.state[7+i])<=1e-9,"MD alpha rotation covariance failed");
                require(std::abs(a.state[6]-b.state[6])<=1e-10&&std::abs(a.state[13]-b.state[13])<=1e-10,"MD scalar rotation covariance failed");
            }
'''
new=new.replace(anchor,addition+anchor,1)
assert new!=old
(R/'tests/test_solver.cpp').write_text(new)
(D/'test_solver.cpp').write_text(new);(D/'original_test_solver.cpp').write_text(old)
(D/'fixture.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='source582/tests/test_solver.cpp',tofile='fixture-source/tests/test_solver.cpp')))
freeze={str(x.relative_to(R)):sha(x.read_bytes())for x in sorted(R.rglob('*'))if x.is_file()}
assert len(freeze)==582 and [n for n in freeze if freeze[n]!=f['source_files'][n]]==['tests/test_solver.cpp']
(D/'source-freeze.json').write_text(json.dumps(dict(identity='md1997-native-fixture-implementation-v1',source_directory=str(R),original_receipt=str(F),original_receipt_sha256=sha(F.read_bytes()),source_files=freeze,changed=['tests/test_solver.cpp'],compiled_calls=0),indent=2)+'\n')
print(json.dumps(dict(files=len(freeze),changed=['tests/test_solver.cpp'],compiled_calls=0)))
