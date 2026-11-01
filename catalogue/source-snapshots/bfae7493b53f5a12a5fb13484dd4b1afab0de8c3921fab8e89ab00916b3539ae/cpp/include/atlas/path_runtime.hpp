#pragma once
#include <algorithm>
#include <cmath>
#include <functional>
#include <vector>
#include <limits>
namespace atlas { namespace controlled_path {
struct Binding { int control; int order; }; // -1 denotes the coordinate
using Evaluator=std::function<bool(const std::vector<double>&,const std::vector<double>&,const std::vector<double>&,std::vector<double>&,std::vector<double>&,std::vector<double>&,bool)>;
struct Definition { int controls; std::vector<Binding> bindings; Evaluator evaluate; };
struct Context { std::vector<double> state; double coordinate; std::vector<double> controls,parameters; };
struct Settings { double absolute=1e-10,relative=1e-8,min_step=1e-12,max_step=.001; int max_depth=40,max_trials=100000; };
inline bool finite(const std::vector<double>& a) { return std::all_of(a.begin(),a.end(),[](double x){return std::isfinite(x);}); }
inline bool settings_valid(const Settings& s) {return std::isfinite(s.absolute)&&s.absolute>0&&std::isfinite(s.relative)&&s.relative>0&&std::isfinite(s.min_step)&&s.min_step>0&&std::isfinite(s.max_step)&&s.max_step>=s.min_step&&s.max_depth>=1&&s.max_depth<=60&&s.max_trials>=1&&s.max_trials<=1000000;}
inline bool stage_inputs(const Definition& d,double coordinate,const std::vector<double>& a,const std::vector<double>& b,double fraction,double progress,std::vector<double>& inputs) {
    if(!std::isfinite(coordinate)||!std::isfinite(fraction)||fraction<0||fraction>1||a.size()!=size_t(d.controls)||b.size()!=a.size()||!finite(a)||!finite(b)) return false;
    std::vector<double> result;
    for(const auto& binding:d.bindings) {
        if(binding.control==-1) {result.push_back(coordinate);continue;}
        if(binding.control<0||binding.control>=d.controls||(binding.order!=0&&binding.order!=1))return false;
        const auto i=binding.control;const double delta=b[i]-a[i];
        const double value=binding.order?(progress?delta/progress:0):(fraction==0?a[i]:fraction==1?b[i]:a[i]+fraction*delta);
        if(!std::isfinite(delta)||!std::isfinite(value))return false;
        result.push_back(value);
    }
    inputs=std::move(result);return true;
}
inline bool advance(const Definition& d,const Context& parent,double progress,const std::vector<double>& start,const std::vector<double>& end,const Settings& settings,Context& output,std::vector<double>& observables) {
    if(!settings_valid(settings)||!std::isfinite(parent.coordinate)||!std::isfinite(progress)||progress<0||start!=parent.controls||!finite(parent.state)||!finite(parent.parameters)||!finite(start)||!finite(end)||start.size()!=size_t(d.controls)||end.size()!=start.size()) return false;
    const double endpoint=parent.coordinate+progress;
    if(!std::isfinite(endpoint)||(progress>0&&!(endpoint>parent.coordinate))||(progress==0&&start!=end))return false;
    std::vector<double> inputs,rates,obs,scales;
    if(!stage_inputs(d,parent.coordinate,start,start,0,0,inputs)||!d.evaluate(parent.state,parent.parameters,inputs,rates,obs,scales,true)||rates.size()!=parent.state.size()||scales.size()!=parent.state.size())return false;
    for(double v:scales)if(!std::isfinite(v)||v<=0)return false;
    auto rhs=[&](const std::vector<double>& y,double offset,std::vector<double>& rate,std::vector<double>& observed) {
        std::vector<double> local_inputs,local_scales;
        if(!stage_inputs(d,parent.coordinate+offset,start,end,progress?offset/progress:0,progress,local_inputs))return false;
        return d.evaluate(y,parent.parameters,local_inputs,rate,observed,local_scales,false)&&rate.size()==parent.state.size()&&finite(rate);
    };
    if(!rhs(parent.state,0,rates,obs))return false;
    if(progress==0){output=parent;observables=obs;return true;}
    auto midpoint=[&](const std::vector<double>& y,double t,double h,std::vector<double>& out) {
        std::vector<double> a,b,unused,mid(y.size()),candidate(y.size());
        if(!rhs(y,t,a,unused))return false;
        for(size_t i=0;i<y.size();++i)mid[i]=y[i]+h*.5*a[i];
        if(!rhs(mid,t+h*.5,b,unused))return false;
        for(size_t i=0;i<y.size();++i)candidate[i]=y[i]+h*b[i];
        if(!rhs(candidate,t+h,a,unused))return false;
        out=std::move(candidate);return true;
    };
    int trials=0;
    std::function<bool(const std::vector<double>&,double,double,int,std::vector<double>&)> integrate;
    integrate=[&](const std::vector<double>& y,double t,double h,int depth,std::vector<double>& out) {
        if(++trials>settings.max_trials||!(t+h>t)||!(parent.coordinate+t+h>parent.coordinate+t))return false;
        double error=std::numeric_limits<double>::infinity();std::vector<double> candidate;
        if(h<=settings.max_step) {
            std::vector<double> full,half;
            if(midpoint(y,t,h,full)&&midpoint(y,t,h*.5,half)&&midpoint(half,t+h*.5,h*.5,candidate)) {
                error=0;
                for(size_t i=0;i<y.size();++i) {
                    const double weight=3*(settings.absolute*scales[i]+settings.relative*std::max(std::abs(y[i]),std::abs(candidate[i])));
                    const double difference=std::abs(full[i]-candidate[i]);
                    if(!std::isfinite(weight)||weight<=0||!std::isfinite(difference)){error=std::numeric_limits<double>::infinity();break;}
                    error=std::max(error,difference/weight);
                }
            }
        }
        if(error<=1){out=std::move(candidate);return true;}
        if(depth>=settings.max_depth||h*.5<settings.min_step)return false;
        std::vector<double> left;
        return integrate(y,t,h*.5,depth+1,left)&&integrate(left,t+h*.5,h*.5,depth+1,out);
    };
    std::vector<double> result;
    if(!integrate(parent.state,0,progress,0,result)||!rhs(result,progress,rates,obs))return false;
    Context committed{result,endpoint,end,parent.parameters};output=std::move(committed);observables=std::move(obs);return true;
}
}}
