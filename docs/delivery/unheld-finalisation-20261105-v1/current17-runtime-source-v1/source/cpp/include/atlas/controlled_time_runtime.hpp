#pragma once
#include <algorithm>
#include <cmath>
#include <functional>
#include <limits>
#include <vector>
namespace atlas { namespace controlled_time {
struct Binding {int offset,size,order;}; // offset -1 is physical time
using Evaluator=std::function<bool(const std::vector<double>&,const std::vector<double>&,const std::vector<double>&,std::vector<double>&,std::vector<double>&,std::vector<double>&,bool)>;
struct Definition {int controls;std::vector<int> constraints;std::vector<Binding> bindings;Evaluator evaluate;};
struct Context {std::vector<double> state;double time;std::vector<double> controls,rates,parameters;};
struct Settings {double absolute,relative,min_step,max_step;int max_depth,max_trials;};
struct Diagnostics {double trials=0,accepted=0,rejected=0,error=0;};
inline bool finite(const std::vector<double>& v){return std::all_of(v.begin(),v.end(),[](double x){return std::isfinite(x);});}
inline bool settings_valid(const Settings&s){return std::isfinite(s.absolute)&&s.absolute>0&&std::isfinite(s.relative)&&s.relative>0&&std::isfinite(s.min_step)&&s.min_step>0&&std::isfinite(s.max_step)&&s.max_step>=s.min_step&&s.max_depth>=1&&s.max_depth<=60&&s.max_trials>=1&&s.max_trials<=1000000;}
inline bool inputs(const Definition&d,double time,const std::vector<double>&v,const std::vector<double>&r,std::vector<double>&out){
 if(!std::isfinite(time)||v.size()!=size_t(d.controls)||r.size()!=v.size()||d.constraints.size()!=v.size()||!finite(v)||!finite(r))return false;
 for(size_t i=0;i<v.size();++i)if((d.constraints[i]==1&&v[i]<=0)||(d.constraints[i]==2&&v[i]<0))return false;
 std::vector<double>x;
 for(auto b:d.bindings){if(b.offset==-1){x.push_back(time);continue;}if(b.offset<0||b.size<1||b.offset+b.size>d.controls||(b.order!=0&&b.order!=1))return false;const auto&a=b.order?r:v;for(int j=0;j<b.size;++j)x.push_back(a[b.offset+j]);}
 out=std::move(x);return true;
}
inline bool evaluate(const Definition&d,const Context&p,bool initial,std::vector<double>&rr,std::vector<double>&oo,std::vector<double>&ss){std::vector<double>i;if(!inputs(d,p.time,p.controls,p.rates,i)||!finite(p.state)||!finite(p.parameters))return false;return d.evaluate(p.state,p.parameters,i,rr,oo,ss,initial)&&rr.size()==p.state.size()&&ss.size()==p.state.size()&&finite(rr)&&finite(oo)&&finite(ss)&&std::all_of(ss.begin(),ss.end(),[](double x){return x>0;});}
inline bool advance(const Definition&d,const Context&p,double duration,const std::vector<double>&start,const std::vector<double>&end,const Settings&s,Context&output,std::vector<double>&observed,Diagnostics&diagnostics){
 if(!settings_valid(s)||!std::isfinite(duration)||duration<=0||start!=p.controls||start.size()!=size_t(d.controls)||end.size()!=start.size()||!finite(start)||!finite(end))return false;
 const double endpoint=p.time+duration;if(!std::isfinite(endpoint)||!(endpoint>p.time))return false;
 std::vector<double>rr,oo,scales;if(!evaluate(d,p,false,rr,oo,scales))return false;
 std::vector<double>rates(end.size());for(size_t i=0;i<rates.size();++i){const double delta=end[i]-start[i];rates[i]=delta/duration;if(!std::isfinite(delta)||!std::isfinite(rates[i]))return false;}
 auto rhs=[&](const std::vector<double>&y,double offset,std::vector<double>&rate,std::vector<double>&obs){
  const double fraction=offset/duration;if(!std::isfinite(fraction)||fraction<0||fraction>1)return false;
  std::vector<double>values(end.size()),ss;
  for(size_t i=0;i<values.size();++i)values[i]=fraction==0?start[i]:fraction==1?end[i]:start[i]+fraction*(end[i]-start[i]);
  Context stage{y,p.time+offset,values,rates,p.parameters};return evaluate(d,stage,false,rate,obs,ss);
 };
 if(!rhs(p.state,0,rr,oo))return false;
 auto midpoint=[&](const std::vector<double>&y,double t,double h,std::vector<double>&out){std::vector<double>a,b,unused,mid(y.size()),candidate(y.size());if(!rhs(y,t,a,unused))return false;for(size_t i=0;i<y.size();++i)mid[i]=y[i]+h*.5*a[i];if(!rhs(mid,t+h*.5,b,unused))return false;for(size_t i=0;i<y.size();++i)candidate[i]=y[i]+h*b[i];if(!rhs(candidate,t+h,a,unused))return false;out=std::move(candidate);return true;};
 Diagnostics diag;
 std::function<bool(const std::vector<double>&,double,double,int,std::vector<double>&)> integrate;
 integrate=[&](const std::vector<double>&y,double t,double h,int depth,std::vector<double>&out){
  if(++diag.trials>s.max_trials||!(t+h>t)||!(p.time+t+h>p.time+t)||!(t+h*.5>t)||!(p.time+t+h*.5>p.time+t))return false;
  double error=std::numeric_limits<double>::infinity();std::vector<double>candidate;
  if(h<=s.max_step){std::vector<double>full,half;if(midpoint(y,t,h,full)&&midpoint(y,t,h*.5,half)&&midpoint(half,t+h*.5,h*.5,candidate)){error=0;for(size_t i=0;i<y.size();++i){const double w=3*(s.absolute*scales[i]+s.relative*std::max(std::abs(y[i]),std::abs(candidate[i])));const double diff=std::abs(full[i]-candidate[i]);if(!std::isfinite(w)||w<=0||!std::isfinite(diff)){error=std::numeric_limits<double>::infinity();break;}error=std::max(error,diff/w);}}}
  if(error<=1){out=std::move(candidate);diag.accepted+=2;diag.error=error;return true;}
  ++diag.rejected;if(depth>=s.max_depth||h*.5<s.min_step)return false;
  std::vector<double>left;return integrate(y,t,h*.5,depth+1,left)&&integrate(left,t+h*.5,h*.5,depth+1,out);
 };
 std::vector<double>result;if(!integrate(p.state,0,duration,0,result)||!rhs(result,duration,rr,oo))return false;
 Context committed{result,endpoint,end,rates,p.parameters};output=std::move(committed);observed=std::move(oo);diagnostics=diag;return true;
}
}}
