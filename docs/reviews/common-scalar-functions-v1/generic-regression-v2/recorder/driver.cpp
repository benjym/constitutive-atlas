#include "atlas/recorded.hpp"
#include <iostream>
using namespace atlas;
int main(){
 State z(7,0.);z[6]=50./64.;auto p=default_parameters(9);RecordedPath path;
 for(int i=0;i<6;++i)path.controls[i].coefficients.v[i]=1.;
 path.knots.push_back({0,{0,0,0,0,0,0}});path.knots.push_back({1,{7./64.,0,0,0,0,0}});
 auto run=replay_recorded(9,z,p,path);bool expected=run.ok&&run.points.size()==2&&run.material_trials==1&&run.attempted_substeps==12;
 if(run.points.size()==2){const auto&d=run.points.back().diagnostics;expected=expected&&d.partition_retries==1&&d.substeps==3&&d.discarded_substeps==9&&d.attempted_substeps==12&&std::abs(run.state[0]-77./96.)<=2e-10&&run.state[6]==run.state[0];}
 std::cout<<std::boolalpha<<"{\"pass\":"<<expected<<",\"ok\":"<<run.ok<<",\"material_trials\":"<<run.material_trials<<",\"attempted_substeps\":"<<run.attempted_substeps<<"}\n";
 return expected?0:1;
}
