#include "atlas/linearize.hpp"
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace atlas;
int find(const char* id){for(size_t i=0;i<models().size();++i)if(models()[i].id==id)return int(i);throw std::runtime_error("missing model");}
void array(const State& a){std::cout<<"[";for(size_t i=0;i<a.size();++i){if(i)std::cout<<",";std::cout<<a[i];}std::cout<<"]";}
void matrix(const std::vector<State>& a){std::cout<<"[";for(size_t i=0;i<a.size();++i){if(i)std::cout<<",";array(a[i]);}std::cout<<"]";}
void require(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
int main(){try{
 std::cout<<std::setprecision(17)<<"[";bool comma=false;
 auto test=[&](const char* id,const Sym<double>& de,bool difference=true,bool preload=false){
   int model=find(id);auto p=default_parameters(model),parent=initial_state(model);
   if(preload){auto r=integrate(model,parent,make_sym(.001,-.0005,-.0005,0.,0.,0.),p);require(r.ok,"preload failed");parent=r.state;}
   auto saved=parent;auto r=linearize_update(model,parent,de,p);
   if(!r.tangent_ok)throw std::runtime_error(std::string(id)+": "+r.message);
   require(parent==saved,"linearization changed parent");
   std::vector<State> fd(parent.size(),State(6));double max_error=0;const double h=1e-7;
   if(difference)for(int j=0;j<6;++j){auto plus=de,minus=de;plus.v[j]+=h;minus.v[j]-=h;
     auto a=integrate(model,parent,plus,p),b=integrate(model,parent,minus,p);
     require(a.ok&&b.ok,"perturbed update failed");
     require(a.diagnostics.increment_fractions==r.advance.diagnostics.increment_fractions&&b.diagnostics.increment_fractions==r.advance.diagnostics.increment_fractions,"FD crosses adaptive partition");
     auto scales=model_scales(model,p);
     for(size_t i=0;i<parent.size();++i){fd[i][j]=(a.state[i]-b.state[i])/(2*h);
       double error=std::abs(fd[i][j]-r.state_tangent[i][j])/std::max(scales[i],std::abs(fd[i][j]));max_error=std::max(max_error,error);}
   }
   if(comma)std::cout<<",";comma=true;
   std::cout<<"{\"model\":\""<<id<<"\",\"preload\":"<<(preload?"true":"false")<<",\"parent\":";array(parent);
   std::cout<<",\"increment\":";array(State(de.v.begin(),de.v.end()));std::cout<<",\"state\":";array(r.advance.state);
   std::cout<<",\"tangent\":";matrix(r.state_tangent);std::cout<<",\"finite_difference\":";matrix(fd);
   std::cout<<",\"fd_checked\":"<<(difference?"true":"false")<<",\"h\":"<<h<<",\"max_normalized_error\":"<<max_error
     <<",\"reset_guard_at_zero\":"<<(r.reset_guard_at_zero?"true":"false")<<",\"fractions\":";array(r.advance.diagnostics.increment_fractions);std::cout<<"}";
 };
 test("linear-elastic",make_sym(.001,-.0002,.0003,.0004,-.0001,.0002));
 test("drucker-prager",make_sym(.005,-.0025,-.0025,.0005,-.0002,.0001));
 test("modified-cam-clay",make_sym(.012,.006,.006,0.,0.,0.));
 test("hypoplastic-sand-vw96",make_sym(.0001,-.00005,-.00005,.00002,0.,0.));
 test("hypoplastic-sand-igs97",make_sym(.0001,-.00005,-.00005,.00002,0.,0.));
 test("test-update-tangent-reset",make_sym(.1,.02,-.01,.03,0.,0.));
 test("test-update-tangent-implicit",make_sym(.3,0.,0.,0.,0.,0.));
 test("test-parent-reset-cutback",make_sym(-1.,0.,0.,0.,0.,0.));
 test("test-parent-reset-cutback",make_sym(0.,0.,0.,0.,0.,0.),false);
 test("research-sanisand-2004-parent-reset-be",make_sym(.0001,-.00005,-.00005,.00001,0.,0.));
 test("research-sanisand-2004-parent-reset-be",make_sym(-.0001,.00005,.00005,0.,0.,0.),true,true);
 int singular=find("test-update-tangent-singular");auto parent=initial_state(singular);
 auto unavailable=linearize_update(singular,parent,make_sym(0.,0.,0.,0.,0.,0.),default_parameters(singular));
 require(unavailable.advance.ok&&!unavailable.tangent_ok&&unavailable.state_tangent.empty(),"singular tangent changed update status");
 auto failed=linearize_update(-1,parent,make_sym(0.,0.,0.,0.,0.,0.),{});
 require(!failed.advance.ok&&!failed.tangent_ok&&failed.advance.state==parent,"failed update not preserved");
 std::cout<<"]\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
