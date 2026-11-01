#include "models.hpp"
#include "history.hpp"
#include "expression.hpp"
#include <bit>
#include <iostream>
#include <cstdint>
#include <limits>
#include <cstring>
using namespace atlas;
int main(){
  std::uint64_t bits;int index=0;
  while(std::cin>>bits){Sym<double>a; a.v[0]=std::bit_cast<double>(bits);
    for(unsigned i=1;i<6;++i){if(!(std::cin>>bits))return 2;a.v[i]=std::bit_cast<double>(bits);}
    if(!(std::cin>>bits))return 2;double width=std::bit_cast<double>(bits);
    bool ok=true;const bool d=emitted(a,width,ok);const bool dok=ok;
    Sym<Jet>j;for(int i=0;i<6;++i){j.v[i]=Jet(a.v[i]);for(int n=0;n<38;++n)j.v[i].d[n]=(i+1)*(n+1)*.001;}
    Jet w(width);for(int n=0;n<38;++n)w.d[n]=n+1;
    ok=true;const bool v=emitted(j,w,ok);const bool jok=ok;
    std::vector<double>z(12),out{923.};for(int i=0;i<6;++i)z[i]=a.v[i];const auto before=z;
    std::vector<double>params;for(const auto& p:models()[0].parameters)params.push_back(p.name=="p_ref"?width:p.value);
    const bool init=evaluate_model(0,z,z,Sym<double>{},params,out,true,0.,true);
    bool unchanged=z==before&&out==std::vector<double>{923.};
    std::vector<double>raw;const bool raw_ok=evaluate_model(0,z,z,Sym<double>{},params,raw);
    std::vector<double>obs;const bool observed=evaluate_model(0,z,z,Sym<double>{},params,obs,false,0.,false,true);
    std::cout<<index++<<' '<<dok<<' '<<d<<' '<<jok<<' '<<v<<' '<<init<<' '<<unchanged<<' '<<raw_ok<<' '<<observed<<'\n';
  }
  // Every component/primal and all38 tensor/scalar seeds: NaN and both infinities.
  int rejected=0;bool negative_ok=true;
  const double poisons[]={std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};
  for(int field=0;field<7;++field)for(int column=-1;column<38;++column)for(double poison:poisons){
    Sym<Jet>a;Jet w(2.);if(field<6){if(column<0)a.v[field].v=poison;else a.v[field].d[column]=poison;}else{if(column<0)w.v=poison;else w.d[column]=poison;}
    bool out=true;const bool valid=centered_middle_accuracy::checked(a,w,out);negative_ok=negative_ok&&!valid&&out;
    bool flag=true;(void)emitted_masked(a,w,flag);negative_ok=negative_ok&&!flag;
    Sym<Jet>good;Jet gw(0.);bool recovery=false;negative_ok=negative_ok&&centered_middle_accuracy::checked(good,gw,recovery)&&!recovery;
    ++rejected;
  }
  Sym<double>a;bool out=true;negative_ok=negative_ok&&!centered_middle_accuracy::checked(a,-1.,out)&&out;
  bool flag=true;negative_ok=negative_ok&&emitted_lazy(a,-1.,flag)==7.&&flag;
  flag=false;(void)emitted(a,0.,flag);negative_ok=negative_ok&&!flag;
  std::vector<double>parent{1.,2.,3.,4.,5.,6.},inputs(7);inputs[6]=1.;const auto saved=parent;
  const auto failure=history::run_1(parent,inputs,7,3);inputs[6]=0.;const auto recovery=history::run_1(parent,inputs,7,3);
  const bool history_ok=!failure.ok&&failure.values==saved&&failure.generation==7&&failure.epoch==3&&failure.events.empty()&&recovery.ok&&parent==saved;
  std::cout<<"summary "<<index<<' '<<rejected<<' '<<negative_ok<<' '<<history_ok<<'\n';
  return negative_ok&&history_ok?0:3;
}
