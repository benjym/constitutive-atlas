#include "atlas/linearize.hpp"
#include <iostream>
#include <iomanip>
using namespace atlas;
void array(const State&z){std::cout<<'[';for(size_t i=0;i<z.size();++i){if(i)std::cout<<',';std::cout<<z[i];}std::cout<<']';}
void tensors(const std::vector<State>&z){std::cout<<'[';for(size_t i=0;i<z.size();++i){if(i)std::cout<<',';array(z[i]);}std::cout<<']';}
int main(){
 std::cout<<std::setprecision(17)<<std::boolalpha;
 const int model=9;auto p=default_parameters(model);State z(7,0.);z[6]=50./64.;Sym<double> de;de.v[0]=7./64.;IntegrationSettings settings;
 for(int mode=0;mode<5;++mode){
  auto s=settings;if(mode==1)s.max_depth=0;if(mode==2)s.max_substeps=1;if(mode==3)s.max_substeps=10;
  auto input=mode==4?State{100000,100000,100000,0,0,0,0}:z;
  auto r=integrate(mode==4?5:model,input,de,mode==4?default_parameters(5):p,s);auto d=r.diagnostics;auto repeat=integrate(mode==4?5:model,input,de,mode==4?default_parameters(5):p,s);
  bool exact_replay=r.ok==repeat.ok&&r.state==repeat.state&&d.increment_fractions==repeat.diagnostics.increment_fractions&&d.accepted_increments==repeat.diagnostics.accepted_increments&&d.attempted_substeps==repeat.diagnostics.attempted_substeps
   &&d.iterations==repeat.diagnostics.iterations&&d.substeps==repeat.diagnostics.substeps&&d.rejected==repeat.diagnostics.rejected
   &&d.nonmonotone_restarts==repeat.diagnostics.nonmonotone_restarts&&d.rounding_corrections==repeat.diagnostics.rounding_corrections
   &&d.discarded_substeps==repeat.diagnostics.discarded_substeps&&d.partition_retries==repeat.diagnostics.partition_retries
   &&d.first_attempt_substeps==repeat.diagnostics.first_attempt_substeps&&d.error==repeat.diagnostics.error
   &&d.partition_defect==repeat.diagnostics.partition_defect&&d.discarded_increment_fractions==repeat.diagnostics.discarded_increment_fractions
   &&d.discarded_increments==repeat.diagnostics.discarded_increments;
  std::cout<<"{\"mode\":"<<mode<<",\"exact_replay\":"<<exact_replay<<",\"ok\":"<<r.ok<<",\"state\":";array(r.state);
  std::cout<<",\"substeps\":"<<d.substeps<<",\"attempted\":"<<d.attempted_substeps<<",\"discarded\":"<<d.discarded_substeps<<",\"first\":"<<d.first_attempt_substeps<<",\"retries\":"<<d.partition_retries<<",\"fractions\":";array(d.increment_fractions);
  std::cout<<",\"increments\":";tensors(d.accepted_increments);std::cout<<",\"discarded_fractions\":";array(d.discarded_increment_fractions);std::cout<<",\"discarded_increments\":";tensors(d.discarded_increments);std::cout<<",\"defect\":";array(d.partition_defect);std::cout<<"}\n";
 }
 auto a=linearize_update(model,z,de,p,settings);std::cout<<"{\"kind\":\"tangent\",\"ok\":"<<a.tangent_ok<<",\"state\":";array(a.advance.state);std::cout<<",\"matrix\":";tensors(a.state_tangent);std::cout<<"}\n";
 State trial;Diagnostics d;bool first=advance_recursive(model,z,de,p,trial,d,0,settings);
 std::cout<<"{\"kind\":\"original\",\"ok\":"<<first<<",\"substeps\":"<<d.substeps<<"}\n";
 Sym<double> left,right;State defect;bool normal=alternate_partition(de,left,right,defect);auto tiny=de;tiny.v[1]=std::numeric_limits<double>::denorm_min();bool underflow=alternate_partition(tiny,left,right,defect);auto invalid=de;invalid.v[1]=std::numeric_limits<double>::infinity();bool nonfinite=alternate_partition(invalid,left,right,defect);
 std::cout<<"{\"kind\":\"guards\",\"normal\":"<<normal<<",\"underflow\":"<<underflow<<",\"nonfinite\":"<<nonfinite<<"}\n";
 return 0;
}
