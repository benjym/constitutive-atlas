#pragma once
#include <bit>
#include <cstdint>
namespace atlas {
inline bool outer_same_bits(double a,double b){return std::bit_cast<std::uint64_t>(a)==std::bit_cast<std::uint64_t>(b);}
inline bool outer_same_state(const State&a,const State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(!outer_same_bits(a[i],b[i]))return false;return true;}
inline bool outer_same_settings(const IntegrationSettings&a,const IntegrationSettings&b){
 return outer_same_bits(a.residual_tolerance,b.residual_tolerance)&&outer_same_bits(a.rate_tolerance,b.rate_tolerance)&&outer_same_bits(a.increment_tolerance,b.increment_tolerance)&&a.max_iterations==b.max_iterations&&a.max_depth==b.max_depth&&a.max_substeps==b.max_substeps&&a.max_backtracks==b.max_backtracks&&a.positive_stress_metric==b.positive_stress_metric;
}
struct OuterReuseCounts{int executed=0,hits=0,misses=0,outer_iterations=0,seeded_trials=0,failed_seed_trials=0;};
// Local one-use complete transaction. Never an implicit root or cross-call cache.
struct OuterTransaction {
 bool occupied=false;int model=-1;State parent,parameters;Sym<double>increment;IntegrationSettings settings;Advance value;
 void retain(int m,const State&zn,const Sym<double>&de,const State&p,const IntegrationSettings&s,const Advance&v){
  occupied=false;if(!v.ok)return;model=m;parent=zn;increment=de;parameters=p;settings=s;value=v;occupied=true;
 }
 bool take(int m,const State&zn,const Sym<double>&de,const State&p,const IntegrationSettings&s,Advance&out){
  bool had=occupied;occupied=false;if(!had||m!=model||!outer_same_state(zn,parent)||!outer_same_state(p,parameters)||!outer_same_settings(s,settings))return false;
  for(int i=0;i<6;++i)if(!outer_same_bits(de.v[i],increment.v[i]))return false;
  out=value;return true;
 }
};
}
