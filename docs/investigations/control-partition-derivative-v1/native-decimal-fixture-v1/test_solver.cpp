#include "atlas/solver.hpp"
#include <iostream>
#include <cstdlib>
#include <string>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <locale>

void require(bool value,const char*message){if(!value)throw std::runtime_error(message);}

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
void md_fixture_derivatives(int model,const atlas::State&z,const atlas::State&zn,const atlas::State&p,const atlas::State&scales,const atlas::Sym<double>&de,const std::vector<atlas::Jet>&r,bool decimal_reference=false){
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
    if(!decimal_reference)for(int j=0;j<14;++j){atlas::State v(14,0.);v[j]=1;direction(v,j>=7&&j<=9?5e-11:1e-6);}
    // Independent rank13 source tangent; no isotropic-alpha source claim.
    for(int j: {0,1,2,3,4,5,6,13}){atlas::State v(14,0.);v[j]=1;direction(v,1e-6);}
    atlas::State v(14,0.);v[7]=1/std::sqrt(2.);v[8]=-v[7];direction(v,1e-6);
    v.assign(14,0.);v[7]=v[8]=1/std::sqrt(6.);v[9]=-2/std::sqrt(6.);direction(v,1e-6);
    for(int j: {10,11,12}){v.assign(14,0.);v[j]=1;direction(v,1e-6);}
}

// Test-only transport. It exports actual generated Jet derivatives and actual
// endpoint probes; the independent frozen Decimal assessor decides accuracy.
void md_decimal_json_string(std::ostream&out,const std::string&value){
    const char*hex="0123456789abcdef";out<<'"';
    for(unsigned char c:value){
        if(c=='"'||c=='\\')out<<'\\'<<char(c);
        else if(c<32)out<<"\\u00"<<hex[c>>4]<<hex[c&15];
        else out<<char(c);
    }
    out<<'"';
}
void md_decimal_hex(std::ostream&out,double value){
    require(std::isfinite(value),"MD Decimal export nonfinite number");
    out<<'"'<<std::nouppercase<<std::hexfloat<<value<<std::defaultfloat<<'"';
}
void md_decimal_vector(std::ostream&out,const atlas::State&values){
    out<<'[';for(size_t i=0;i<values.size();++i){if(i)out<<',';md_decimal_hex(out,values[i]);}out<<']';
}
bool md_decimal_binding_valid(const char*value){
    if(!value||std::string(value).size()!=64)return false;
    for(const char*c=value;*c;++c)if(!((*c>='0'&&*c<='9')||(*c>='a'&&*c<='f')))return false;
    return true;
}
std::string md_decimal_export(int model,const atlas::State&z,const atlas::State&zn,const atlas::State&p,const atlas::State&scales,const atlas::Sym<double>&de,const std::vector<atlas::Jet>&r,const std::string&binding){
    require(z.size()==14&&zn.size()==14&&p.size()==17&&scales.size()==14&&r.size()==14,"MD Decimal export layout");
    const auto branch=md_fixture_branch(z,p);const auto&metadata=atlas::models()[model];
    std::ostringstream out;out.imbue(std::locale::classic());
    out<<"{\"identity\":\"md1997-decimal-ad-export-v1\",\"selector\":\"md1997-decimal-fd-reference-v1\",\"status\":\"exported-unassessed\",\"models\":"<<atlas::models().size()<<",\"bindings\":{";
    // Frozen oracle/source identities, not runtime-injectable requests.
    out<<"\"evaluator_sha256\":\"c0d7c733db1432f67370d832c6f4a9dc6db5b94ba2ddfa0955cec39aadf91668\"";
    out<<",\"policy_sha256\":\"79152e516054320064d67b9dc333be0945d6738362b4ab17b968ffaaf84f087c\"";
    out<<",\"base_source_freeze_sha256\":\"19a8d836efb0cc6b043dded7d2b06eb7d0bb61d6b9c7340349b39feb329ac54c\"";
    out<<",\"model_sha256\":\"28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064\"";
    out<<",\"request_sha256\":\"ee4158da6cc5f8f9bec55bb56183fd465e8ba1f710d83d1fa0f08d631e3bc098\"";
    out<<",\"reference_sha256\":\"74ae57a2b70b7042ef8e8408b589911d8fce723f8c27aac62accb34f4299e299\"";
    out<<",\"build_binding_sha256\":";md_decimal_json_string(out,binding);out<<"},\"base\":{\"layout\":[";
    for(size_t i=0;i<metadata.fields.size();++i){
        const auto&field=metadata.fields[i];if(i)out<<',';out<<"{\"name\":";md_decimal_json_string(out,field.name);out<<",\"shape\":";md_decimal_json_string(out,field.size==6?"sym":"scalar");out<<",\"offset\":"<<field.offset<<",\"size\":"<<field.size<<'}';
    }
    out<<"],\"state_hex\":";md_decimal_vector(out,z);out<<",\"previous_hex\":";md_decimal_vector(out,zn);
    atlas::State loading(6);for(int i=0;i<6;++i)loading[i]=de.v[i];out<<",\"loading_hex\":";md_decimal_vector(out,loading);out<<",\"parameters_hex\":{";
    require(metadata.parameters.size()==p.size(),"MD Decimal parameter layout");
    for(size_t i=0;i<p.size();++i){if(i)out<<',';md_decimal_json_string(out,metadata.parameters[i].name);out<<':';md_decimal_hex(out,p[i]);}
    out<<"},\"scales_hex\":";md_decimal_vector(out,scales);out<<"},\"endpoints\":[";
    bool first=true;
    for(int column=0;column<14;++column){
        atlas::State direction(14,0.);direction[column]=1.;const double h=column>=7&&column<=9?5e-11:1e-6;
        for(int level=0;level<2;++level){
            const double step=level?h/2:h;auto plus=z,minus=z;
            for(int j=0;j<14;++j){plus[j]+=step*scales[j]*direction[j];minus[j]-=step*scales[j]*direction[j];}
            require(md_fixture_branch(plus,p)==branch&&md_fixture_branch(minus,p)==branch,"MD FD branch changed");
            atlas::State rp,rm;require(atlas::evaluate_model(model,plus,zn,de,p,rp)&&atlas::evaluate_model(model,minus,zn,de,p,rm),"MD FD outside domain");
            require(rp.size()==14&&rm.size()==14&&atlas::finite(rp)&&atlas::finite(rm),"MD FD residual finite layout");
            for(int sign:{1,-1}){
                if(!first)out<<',';first=false;out<<"{\"column\":"<<column<<",\"level\":"<<level<<",\"sign\":"<<sign<<",\"step_hex\":";md_decimal_hex(out,step);
                out<<",\"direction_hex\":";md_decimal_vector(out,direction);out<<",\"state_hex\":";md_decimal_vector(out,sign==1?plus:minus);
                out<<",\"domain\":true,\"branch\":true}";
            }
        }
    }
    out<<"],\"ad_hex\":[";
    for(int row=0;row<14;++row){
        require(atlas::finite_value(r[row]),"MD Decimal export nonfinite Jet");if(row)out<<',';out<<'[';
        for(int column=0;column<14;++column){if(column)out<<',';md_decimal_hex(out,r[row].d[column]);}out<<']';
    }
    out<<']';return out.str(); // caller appends C++ check flags only after ALL checks
}

int main(){
    try{
        const char* profile=std::getenv("ATLAS_NATIVE_FIXTURES");
        require(!profile||(std::string(profile)=="explicit-gis20-v2"||std::string(profile)=="explicit-gis20-occ-v3"||(std::string(profile)=="explicit-gis20-occ-restart-v4"||std::string(profile)=="explicit-gis20-occ-restart-duncan-v5")),"unknown native fixture profile");
        const char* numerical_profile=std::getenv("ATLAS_NUMERICAL_FIXTURES");
        const bool md_decimal=numerical_profile&&std::string(numerical_profile)=="md1997-decimal-fd-reference-v1";
        const bool md_admissible=numerical_profile!=nullptr;
        require(!numerical_profile||std::string(numerical_profile)=="md1997-source-admissible-v1"||md_decimal,"unknown numerical fixture profile");
        const char*decimal_binding=std::getenv("ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256");
        std::string decimal_payload;
        if(md_admissible){
            require(profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5","MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5");
            int count=0;
            for(size_t m=0;m<atlas::models().size();++m)if(atlas::models()[m].id=="manzari-dafalias-1997-constant-m-be-v1"){
                ++count;const auto&fields=atlas::models()[m].fields;
                require(fields.size()==4&&fields[0].name=="sigma"&&fields[0].offset==0&&fields[0].size==6&&fields[1].name=="e"&&fields[1].offset==6&&fields[1].size==1&&fields[2].name=="alpha"&&fields[2].offset==7&&fields[2].size==6&&fields[3].name=="gamma"&&fields[3].offset==13&&fields[3].size==1&&fields[3].multiplier,"MD numerical fixture requires exact14 layout");
                const atlas::State expected={100000,160000,31400000,31400000,.6,1.14,1.14,.025,.8,3.975,2.,4.2,.07,1200,.05,2.64,.65};
                require(atlas::initial_state(int(m)).size()==14&&atlas::default_parameters(int(m))==expected,"MD numerical fixture parameter/layout identity");
            }
            require(count==1,"MD numerical fixture requires exactly one MD model");
        }
        require(!decimal_binding||md_decimal,"MD Decimal build binding requires Decimal profile");
        require(!md_decimal||md_decimal_binding_valid(decimal_binding),"MD Decimal build binding must be 64 lowercase hex characters");
        if(md_decimal)require(atlas::models().size()==16,"MD Decimal profile requires exactly 16 models");
        const bool explicit_fixtures=profile!=nullptr;
        if(!md_decimal)std::cout<<(md_admissible?"Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5":explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")<<"; models="<<atlas::models().size()<<'\n';
        // Independently finite-difference each generated residual/rate Jacobian.
        // This checks the AD implementation rather than merely matching its code.
        for(size_t model=0;model<atlas::models().size();++model){
            auto p=atlas::default_parameters(int(model)),z=atlas::initial_state(int(model)),zn=z;
            auto scales=atlas::model_scales(int(model),p);z[0]=110000;z[1]=95000;z[2]=100000;z[3]=500;
            for(const auto&f:atlas::models()[model].fields){if(f.multiplier)z[f.offset]=.0001;if(f.name=="h"&&f.size==6){z[f.offset]=.00002;z[f.offset+1]=-.00001;}}
            if(explicit_fixtures&&atlas::models()[model].id=="research-hp-extracted-asbs-gis-2024-v03"){
                bool found=false;
                for(const auto& f:atlas::models()[model].fields)if(f.name=="Omega"){
                    auto invalid=z;invalid[f.offset]=-1e-6*scales[f.offset];atlas::State values;
                    atlas::Sym<double> probe;probe.v={.00001,-.000005,-.000005,.000003,0,0};
                    require(!atlas::evaluate_model(int(model),invalid,zn,probe,p,values),"original negative Omega probe accepted");
                    z[f.offset]=.5;found=true;
                }
                require(found,"GIS derivative fixture requires declared Omega state");
            }
            if(profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5"&&atlas::models()[model].id=="duncan-chang-1970-endpoint-average")z[6]=50000.;
            const int n=int(z.size());std::vector<atlas::Jet>x(n),xn(n),r;atlas::Sym<double>de;de.v={.00001,-.000005,-.000005,.000003,0,0};atlas::Sym<atlas::Jet>d;
            for(int i=0;i<n;++i){x[i]=atlas::Jet(z[i]);x[i].d[i]=scales[i];xn[i]=atlas::Jet(zn[i]);}
            for(int i=0;i<6;++i)d.v[i]=atlas::Jet(de.v[i]);
            require(atlas::evaluate_model(int(model),x,xn,d,p,r),"AD test state outside domain");
            if(md_admissible&&atlas::models()[model].id=="manzari-dafalias-1997-constant-m-be-v1"){
                if(md_decimal){require(decimal_payload.empty(),"MD Decimal duplicate model export");decimal_payload=md_decimal_export(int(model),z,zn,p,scales,de,r,decimal_binding);}
                md_fixture_derivatives(int(model),z,zn,p,scales,de,r,md_decimal);
            }else for(int j=0;j<n;++j){
                double h=1e-6;auto plus=z,minus=z;plus[j]+=h*scales[j];minus[j]-=h*scales[j];atlas::State rp,rm;
                require(atlas::evaluate_model(int(model),plus,zn,de,p,rp)&&atlas::evaluate_model(int(model),minus,zn,de,p,rm),"FD test outside domain");
                for(int i=0;i<n;++i){double fd=(rp[i]-rm[i])/(2*h),ad=r[i].d[j];require(std::isfinite(ad)&&std::abs(fd-ad)<3e-5*std::max({1.,std::abs(fd),std::abs(ad)}),"AD/finite-difference residual Jacobian mismatch");}
            }
        }
        // A fixed 90-degree frame rotation permutes xx/yy and changes shear
        // signs. Isotropic kernels must commute with this change of basis.
        auto rotate=[](atlas::Sym<double>a){atlas::Sym<double>b;b.v={a.v[1],a.v[0],a.v[2],-a.v[3],a.v[5],-a.v[4]};return b;};
        for(size_t m=0;m<atlas::models().size();++m){
            auto p=atlas::default_parameters(int(m)),z=atlas::initial_state(int(m));z[0]=105000;z[1]=95000;z[3]=1000;
            // OCC source admissibility: overconsolidated packing for this anisotropic prestress.
            if(profile&&(std::string(profile)=="explicit-gis20-occ-v3"||(std::string(profile)=="explicit-gis20-occ-restart-v4"||std::string(profile)=="explicit-gis20-occ-restart-duncan-v5"))&&atlas::models()[m].id=="original-cam-clay-sw-electronic-log-recovery-v1")
                z[6]=2.5+.16*(1-std::log(150000./1000.))-.04*std::log(100000./1000.);
            const bool duncan_fixture=profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5"&&atlas::models()[m].id=="duncan-chang-1970-endpoint-average";
            if(duncan_fixture)z[6]=50000.;
            const bool md_rotation=md_admissible&&atlas::models()[m].id=="manzari-dafalias-1997-constant-m-be-v1";
            if(md_rotation){z[0]=640500;z[1]=639500;z[2]=640000;z[3]=100;z[4]=z[5]=0;}
            atlas::Sym<double>de;de.v={.0001,-.00002,.00001,.00003,.00001,-.00001};auto zr=z;
            if(atlas::models()[m].id=="ramberg-osgood-ansys242"){
                // Independently derived consistent source-compliance fixture.
                const double eps[]={0.0018750073153125002,0.0014583260180208333,0.0016666666666666668,4.166812972916667e-05,0.,0.};
                for(int j=0;j<6;++j)z[6+j]=eps[j];
                zr=z;atlas::put_tensor(zr,6,rotate(atlas::tensor_from(z,6)));
            }
            atlas::put_tensor(zr,0,rotate(atlas::tensor_from(z,0)));
            if(md_rotation){require(atlas::domain(int(m),z,p,true)&&atlas::domain(int(m),zr,p,true),"MD rotation initial domain");md_fixture_branch(z,p);md_fixture_branch(zr,p);}
            atlas::IntegrationSettings fixture_settings;
            if(explicit_fixtures&&atlas::models()[m].id=="research-hp-extracted-asbs-gis-2024-v03")fixture_settings.max_depth=20;
            auto a=atlas::integrate(int(m),z,de,p,fixture_settings),b=atlas::integrate(int(m),zr,rotate(de),p,fixture_settings);require(a.ok&&b.ok,"rotation integration failed");
            if(duncan_fixture)require(a.state.size()==7&&b.state.size()==7&&a.state[6]==50000.&&b.state[6]==50000.,"scalar maxhistory rotation fixture changed");
            if(md_rotation){
                require(a.state.size()==14&&b.state.size()==14&&atlas::finite(a.state)&&atlas::finite(b.state)&&atlas::domain(int(m),a.state,p)&&atlas::domain(int(m),b.state,p),"MD rotation final finite domain layout");
                require(md_fixture_branch(a.state,p)==md_fixture_branch(z,p)&&md_fixture_branch(b.state,p)==md_fixture_branch(zr,p),"MD rotation source branch changed");
                auto alpha=rotate(atlas::tensor_from(a.state,7));for(int i=0;i<6;++i)require(std::abs(alpha.v[i]-b.state[7+i])<=1e-9,"MD alpha rotation covariance failed");
                require(std::abs(a.state[6]-b.state[6])<=1e-10&&std::abs(a.state[13]-b.state[13])<=1e-10,"MD scalar rotation covariance failed");
            }
            auto want=rotate(atlas::tensor_from(a.state,0));for(int i=0;i<6;++i)require(std::abs(want.v[i]-b.state[i])<.01,"fixed-frame rotation covariance failed");
        }
        // Hidden zero-history crossing: both midpoint estimates sample unloading
        // and agree exactly, yet the true endpoint is on the loading branch.
        int igs=-1;for(size_t i=0;i<atlas::models().size();++i)
            if(atlas::models()[i].id=="hypoplastic-sand-igs97")igs=int(i);
        require(igs>=0,"IGS model missing");
        auto p=atlas::default_parameters(igs),z=atlas::initial_state(igs);
        z[10]=-7.862141684009169e-6;
        atlas::Sym<double>de;de.v={0,0,0,1e-5,0,0};
        atlas::State full,half,two,defect;
        require(atlas::midpoint(igs,z,de,p,full)&&atlas::midpoint(igs,z,.5*de,p,half)
                &&atlas::midpoint(igs,half,.5*de,p,two,&defect),"crossing probes failed");
        require(std::abs(full[10]-two[10])<1e-18,"crossing counterexample changed");
        require(std::abs(defect[10])>1e-8,"endpoint defect missed hidden branch");
        const double analytical=1.93701012831811e-6;
        require(std::abs(two[10]-analytical)>1e-7,"uncontrolled crossing should expose error");
        auto corrected=atlas::integrate(igs,z,de,p);
        require(corrected.ok&&corrected.diagnostics.rejected>0,"crossing was not refined");
        require(std::abs(corrected.state[10]-analytical)<1e-9,"crossing history inaccurate");
        double fraction=0;for(double f:corrected.diagnostics.increment_fractions)fraction+=f;
        require(fraction==1&&corrected.diagnostics.increment_fractions.size()==size_t(corrected.diagnostics.substeps),"crossing increment trace incomplete");
        // Settings are validated by the C++ entry point too, independently of
        // the CSV API. Failures retain the complete supplied parent.
        atlas::IntegrationSettings settings;
        settings.residual_tolerance=std::numeric_limits<double>::quiet_NaN();
        auto invalid=atlas::integrate(igs,z,de,p,settings);
        require(!invalid.ok&&invalid.state==z&&invalid.diagnostics.iterations==0&&invalid.diagnostics.substeps==0,"invalid settings advanced state");
        settings={};settings.max_substeps=1;
        auto one=atlas::integrate(igs,z,atlas::Sym<double>{},p,settings);
        require(!one.ok&&one.state==z&&one.diagnostics.substeps==0,"midpoint pair exceeded one-step budget");
        require(one.settings.max_substeps==1,"failed update lost requested settings");
        settings.max_substeps=2;
        auto two_budget=atlas::integrate(igs,z,atlas::Sym<double>{},p,settings);
        require(two_budget.ok&&two_budget.diagnostics.substeps==2,"exact midpoint pair budget rejected");
        settings.max_substeps=3;
        auto late=atlas::integrate(igs,z,de,p,settings);
        require(!late.ok&&late.state==z&&late.diagnostics.substeps==2,"odd budget lost late rollback or exceeded cap");
        settings={};settings.max_depth=0;
        auto shallow=atlas::integrate(igs,z,de,p,settings);
        require(!shallow.ok&&shallow.state==z&&shallow.diagnostics.substeps==0,"depth limit did not stop crossing refinement");
        settings={};settings.max_substeps=1;
        auto limited_run=atlas::run_protocol(igs,atlas::initial_state(igs),p,0,1e-5,1,0,settings);
        require(!limited_run.ok&&limited_run.points.size()==1&&limited_run.settings.max_substeps==1,"protocol failed to propagate material settings");
        if(md_decimal){require(!decimal_payload.empty(),"MD Decimal missing model export");std::cout<<decimal_payload<<",\"cpp_checks\":{\"rank13\":true,\"rotation\":true,\"other_models\":true}}\n";}
        else std::cout<<"AD Jacobians, fixed-frame rotation covariance and integration-settings checks passed\n";
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
