#include "atlas/solver.hpp"
#include <iostream>
using namespace atlas;
int main(){static_assert(outer_control_budget==1);int m=0;auto p=default_parameters(m);State parent{60000,60000,60000,0,0,0,13,0};IntegrationSettings s;s.increment_tolerance=1e-7;s.positive_stress_metric=true;s.max_depth=0;s.max_substeps=200000;Sym<double>prior;prior.v[0]=1e-12;prior.v[1]=prior.v[2]=-1e8;Sym<double>a,b;Advance cold,warm;OuterReuseCounts c,w;bool ca=controlled_step(m,parent,p,1,1e-12,60000,0,a,cold,s,true,&c,nullptr,false),wa=controlled_step(m,parent,p,1,1e-12,60000,0,b,warm,s,true,&w,&prior,true);bool ok=ca&&!wa&&w.failed_seed_trials==1&&w.outer_iterations==1&&w.executed==1&&warm.state.empty();std::cout<<"{\"checks\":1,\"passed\":"<<(ok?"true":"false")<<"}\n";return ok?0:1;}
