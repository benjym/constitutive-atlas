#include "atlas/solver.hpp"
#include <iomanip>
#include <iostream>
int main(){
  using namespace atlas;
  std::cout<<std::setprecision(17)<<"[";bool comma=false;
  for(int path=0;path<3;++path)for(int steps:{16,32,64}){
    auto state=initial_state(0);const auto parameters=default_parameters(0);
    auto strain=path==0?make_sym(.002,-.001,-.001,0.,0.,0.):
                path==1?make_sym(-.002,.001,.001,0.,0.,0.):
                        make_sym(.001,-.0003,-.0007,.001,-.0004,.0002);
    strain=strain/double(steps);
    for(int step=0;step<steps;++step){
      auto result=integrate(0,state,strain,parameters);
      if(comma)std::cout<<",";comma=true;
      std::cout<<"{\"path\":"<<path<<",\"steps\":"<<steps<<",\"step\":"<<step
               <<",\"ok\":"<<(result.ok?"true":"false")<<",\"substeps\":"<<result.diagnostics.substeps
               <<",\"state\":[";
      for(std::size_t i=0;i<result.state.size();++i){if(i)std::cout<<",";std::cout<<result.state[i];}
      std::cout<<"]}";
      if(!result.ok){std::cout<<"]\n";return 1;}
      state=result.state;
    }
  }
  std::cout<<"]\n";
}
