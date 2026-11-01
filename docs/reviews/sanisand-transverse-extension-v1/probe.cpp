// Generic generated-residual/Jet adapter; no constitutive equations or integration.
#include "models.hpp"
#include <iostream>
#include <iomanip>
int main(){
  int count;if(!(std::cin>>count)||count<1)return 2;
  std::cout<<std::setprecision(17);
  for(int k=0;k<count;++k){
    std::vector<double> p(16);std::vector<atlas::Jet> z(26),zn(26),out;atlas::Sym<atlas::Jet> de;
    for(auto&v:p)if(!(std::cin>>v))return 3;
    for(auto&v:z)if(!(std::cin>>v.v))return 3;
    for(auto&v:zn)if(!(std::cin>>v.v))return 3;
    for(auto&v:de.v)if(!(std::cin>>v.v))return 3;
    for(auto&v:z)if(!(std::cin>>v.d[0]))return 3;
    for(auto&v:zn)if(!(std::cin>>v.d[0]))return 3;
    for(auto&v:de.v)if(!(std::cin>>v.d[0]))return 3;
    bool ok=atlas::evaluate_model(0,z,zn,de,p,out);
    for(const auto&v:out)ok=ok&&atlas::finite_value(v);
    std::cout<<"{\"ok\":"<<(ok?"true":"false")<<",\"values\":[";
    if(ok)for(size_t i=0;i<out.size();++i){if(i)std::cout<<',';std::cout<<out[i].v;}
    std::cout<<"],\"directional\":[";
    if(ok)for(size_t i=0;i<out.size();++i){if(i)std::cout<<',';std::cout<<out[i].d[0];}
    std::cout<<"]}\n";
  }
}
