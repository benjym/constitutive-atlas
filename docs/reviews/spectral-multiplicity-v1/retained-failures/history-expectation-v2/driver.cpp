#include "models.hpp"
#include "history.hpp"
#include "expression.hpp"
#include <iostream>
#include <iomanip>
#include <bit>
#include <limits>
using namespace atlas;
using State=std::vector<double>;
void output(const Jet&x,bool ok){if(!ok){std::cout<<"null";return;}std::cout<<"{\"value\":"<<x.v<<",\"derivatives\":[";for(int n=0;n<38;++n){if(n)std::cout<<',';std::cout<<x.d[n];}std::cout<<"]}";}
int main(){
 std::cout<<std::setprecision(17);std::uint64_t bits;unsigned index=0;
 while(std::cin>>bits){
  Sym<Jet>A;A.v[0].v=std::bit_cast<double>(bits);
  for(int k=1;k<6;++k){if(!(std::cin>>bits))return 2;A.v[k].v=std::bit_cast<double>(bits);}
  for(int n=0;n<38;++n)for(int k=0;k<6;++k){if(!(std::cin>>bits))return 2;A.v[k].d[n]=std::bit_cast<double>(bits);}
  bool rmax=false,rmin=false;
  const bool cok=spectral_multiplicity_accuracy::checked(A,true,rmax)&&spectral_multiplicity_accuracy::checked(A,false,rmin);
  bool hiok=true,look=true;const auto hi=emitted_maximum(A,hiok),lo=emitted_minimum(A,look);
  Sym<double>a;for(int k=0;k<6;++k)a.v[k]=A.v[k].v;
  bool dhok=true,dlok=true;double dh=emitted_maximum(a,dhok),dl=emitted_minimum(a,dlok);
  bool parity=hiok==dhok&&look==dlok&&(!hiok||hi.v==dh)&&(!look||lo.v==dl);
  std::vector<Jet>z(7);for(int k=0;k<6;++k)z[k]=A.v[k];z[6]=Jet(.7);
  std::vector<double>params;for(const auto&p:models()[0].parameters)params.push_back(p.value);
  std::vector<Jet>out;const bool mok=evaluate_model(0,z,z,Sym<Jet>{},params,out);
  bool structure=!mok||out.size()==7;
  if(mok){for(int k=1;k<7;++k){const Jet target=k<3?out[0]:Jet(0.);structure=structure&&out[k].v==target.v;for(int n=0;n<38;++n)structure=structure&&out[k].d[n]==target.d[n];}}
  const State parent{11,12,13,14,15,16};State inputs;for(int k=0;k<6;++k)inputs.push_back(a.v[k]);inputs.push_back(1.);
  const auto hist=history::programs()[0].advance(parent,inputs,7,3);
  const bool rollback=hist.ok||(hist.values==parent&&hist.generation==7&&hist.epoch==3&&hist.events.empty());
  inputs[6]=0.;const auto recovery=history::programs()[0].advance(parent,inputs,7,3);
  const bool recover=recovery.ok&&recovery.values==State({1,1,1,0,0,0})&&recovery.generation==8&&recovery.epoch==3&&recovery.events.empty()&&parent==State({11,12,13,14,15,16});
  bool hstructure=!hist.ok||hist.values.size()==6;
  if(hist.ok)for(int k=1;k<6;++k)hstructure=hstructure&&hist.values[k]==(k<3?hist.values[0]:0.);
  std::cout<<"{\"index\":"<<index++<<",\"classifier_ok\":"<<cok<<",\"repeated\":["<<rmax<<','<<rmin<<"],\"double_jet_parity\":"<<parity<<",\"hi\":";output(hi,hiok);std::cout<<",\"lo\":";output(lo,look);
  std::cout<<",\"model_ok\":"<<mok<<",\"model\":";if(mok)output(out[0],true);else std::cout<<"null";
  std::cout<<",\"history_ok\":"<<hist.ok<<",\"history_value\":";if(hist.ok)std::cout<<hist.values[0];else std::cout<<"null";
  std::cout<<",\"model_structure\":"<<structure<<",\"history_structure\":"<<hstructure<<",\"history_rollback\":"<<rollback<<",\"history_recovery\":"<<recover<<"}\n";
 }
 unsigned failures=0;bool valid=true;
 const double poison[]={std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};
 for(int k=0;k<6;++k)for(int n=-1;n<38;++n)for(double p:poison)for(bool maximum:{false,true}){
  Sym<Jet>a;if(n<0)a.v[k].v=p;else a.v[k].d[n]=p;
  bool sentinel=true;const bool ok=spectral_multiplicity_accuracy::checked(a,maximum,sentinel);valid=valid&&!ok&&sentinel;
  bool flag=true;(void)emitted_masked(a,flag);valid=valid&&!flag;
  flag=true;const auto lazy=emitted_lazy(a,flag);valid=valid&&flag&&lazy.v==7.;
  Sym<Jet>good;bool recovery=false;valid=valid&&spectral_multiplicity_accuracy::checked(good,maximum,recovery)&&recovery;
  ++failures;
 }
 Sym<Jet>good;bool sticky=false;(void)emitted_maximum(good,sticky);valid=valid&&!sticky;
 Sym<Jet>hydro;for(int k=0;k<3;++k)hydro.v[k]=Jet(3.);
 spectral_candidate::Diagnostic diag;Jet sentinel(923.);valid=valid&&!spectral_candidate::scalar_checked(hydro,spectral_candidate::Operation::max,sentinel,diag)&&sentinel.v==923.;
 std::cout<<"{\"summary\":true,\"cases\":"<<index<<",\"nonfinite_checks\":"<<failures<<",\"controls_pass\":"<<valid<<"}\n";
 return valid?0:3;
}
