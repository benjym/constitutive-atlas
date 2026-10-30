#include "atlas/solver.hpp"
#include <iostream>
#include <stdexcept>

void require(bool value,const char*message){if(!value)throw std::runtime_error(message);}
int main(){
    try{
        // Independently finite-difference each generated residual/rate Jacobian.
        // This checks the AD implementation rather than merely matching its code.
        for(size_t model=0;model<atlas::models().size();++model){
            auto p=atlas::default_parameters(int(model)),z=atlas::initial_state(int(model)),zn=z;
            auto scales=atlas::model_scales(int(model),p);z[0]=110000;z[1]=95000;z[2]=100000;z[3]=500;
            for(const auto&f:atlas::models()[model].fields){if(f.multiplier)z[f.offset]=.0001;if(f.name=="h"){z[f.offset]=.00002;z[f.offset+1]=-.00001;}}
            const int n=int(z.size());std::vector<atlas::Jet>x(n),xn(n),r;atlas::Sym<double>de;de.v={.00001,-.000005,-.000005,.000003,0,0};atlas::Sym<atlas::Jet>d;
            for(int i=0;i<n;++i){x[i]=atlas::Jet(z[i]);x[i].d[i]=scales[i];xn[i]=atlas::Jet(zn[i]);}
            for(int i=0;i<6;++i)d.v[i]=atlas::Jet(de.v[i]);
            require(atlas::evaluate_model(int(model),x,xn,d,p,r),"AD test state outside domain");
            for(int j=0;j<n;++j){
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
            atlas::Sym<double>de;de.v={.0001,-.00002,.00001,.00003,.00001,-.00001};auto zr=z;
            atlas::put_tensor(zr,0,rotate(atlas::tensor_from(z,0)));
            auto a=atlas::integrate(int(m),z,de,p),b=atlas::integrate(int(m),zr,rotate(de),p);require(a.ok&&b.ok,"rotation integration failed");
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
        std::cout<<"AD Jacobians and fixed-frame rotation covariance passed for all executable models\n";
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
