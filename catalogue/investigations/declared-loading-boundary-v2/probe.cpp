#include "atlas/solver.hpp"
#include "atlas/time.hpp"
#include <cstring>
#include <iostream>
#include <limits>

bool same(const atlas::State&a,const atlas::State&b){return a.size()==b.size()&&std::memcmp(a.data(),b.data(),a.size()*sizeof(double))==0;}
void row(const std::string&id,const std::string&phase,bool ok,bool unchanged){std::cout<<id<<','<<phase<<','<<ok<<','<<unchanged<<'\n';}
int main(){
 std::cout<<"id,phase,ok,inputs_unchanged\n";
 const double poison[]={std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};
 const char*label[]={"nan","posinf","neginf"};
 for(int m=0;m<int(atlas::models().size());++m){
  const bool timed=atlas::models()[m].physical_time;
  const auto z=atlas::initial_state(m),p=atlas::default_parameters(m);const auto z0=z,p0=p;
  for(int component=0;component<6;++component)for(int k=0;k<3;++k){
   for(int route=0;route<(timed?3:2);++route){
    const auto id=atlas::models()[m].id+"/eval"+std::to_string(route)+"/"+std::to_string(component)+"/"+label[k];
    for(int recovery=0;recovery<2;++recovery){
     atlas::Sym<double>d; if(!recovery)d.v[component]=poison[k];const auto d0=d;atlas::State out;
     const bool ok=atlas::evaluate_model(m,z,z,d,p,out,false,2.,route==1,route==2);
     row(id,recovery?"recovery":"invalid",ok,same(z,z0)&&same(p,p0)&&std::memcmp(d.v.data(),d0.v.data(),6*sizeof(double))==0);
    }
   }
   const auto id=atlas::models()[m].id+"/integrator/"+std::to_string(component)+"/"+label[k];
   for(int recovery=0;recovery<2;++recovery){
    atlas::Sym<double>d;if(!recovery)d.v[component]=poison[k];const auto d0=d;
    bool ok=false,preserved=false;
    if(timed){auto result=atlas::integrate_time(m,z,d,p,2.,1.);ok=result.ok;preserved=same(result.state,z);}
    else {auto result=atlas::integrate(m,z,d,p);ok=result.ok;preserved=same(result.state,z);}
    row(id,recovery?"recovery":"invalid",ok,preserved&&same(z,z0)&&same(p,p0)&&std::memcmp(d.v.data(),d0.v.data(),6*sizeof(double))==0);
   }
  }
  if(timed)for(int route=0;route<3;++route)for(int k=0;k<3;++k){
   const auto id=atlas::models()[m].id+"/clock"+std::to_string(route)+"/"+label[k];
   for(int recovery=0;recovery<2;++recovery){atlas::Sym<double>d;atlas::State out;bool ok=atlas::evaluate_model(m,z,z,d,p,out,false,recovery?2.:poison[k],route==1,route==2);row(id,recovery?"recovery":"invalid",ok,same(z,z0)&&same(p,p0));}
  }
 }

 for(int m=0;m<int(atlas::models().size());++m){
  auto z=atlas::initial_state(m),p=atlas::default_parameters(m);const auto z0=z,p0=p;
  const double values[]={-0.,std::numeric_limits<double>::denorm_min(),std::numeric_limits<double>::max(),-std::numeric_limits<double>::max()};
  const char* labels[]={"negative-zero","subnormal","max-finite","min-finite"};
  for(int route=0;route<(atlas::models()[m].physical_time?3:2);++route)for(int k=0;k<4;++k){
   atlas::Sym<double>d;for(auto&v:d.v)v=values[k];const auto d0=d;atlas::State out;
   bool ok=atlas::evaluate_model(m,z,z,d,p,out,false,2.,route==1,route==2);
   row(atlas::models()[m].id+"/finite"+std::to_string(route)+"/"+labels[k],"control",ok,same(z,z0)&&same(p,p0)&&std::memcmp(d.v.data(),d0.v.data(),6*sizeof(double))==0);
  }
 }
}
