#include "atlas/time.hpp"
#include <chrono>
#include <iomanip>
#include <iostream>
#include <map>
#include <cstdlib>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define ATLAS_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define ATLAS_EXPORT
#endif

namespace {
std::string output;
std::string quote(const std::string& s){std::string t="\"";for(unsigned char c:s){if(c=='"'||c=='\\'){t+='\\';t+=c;}else if(c=='\n')t+="\\n";else if(c<32)t+=' ';else t+=c;}return t+'"';}
void array(std::ostream&o,const atlas::State&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';if(!std::isfinite(v[i]))throw std::runtime_error("nonfinite output");o<<v[i];}o<<']';}
atlas::State parse_csv(const char*s){atlas::State v;if(!s||!*s)return v;std::istringstream in(s);std::string item;while(std::getline(in,item,',')){size_t pos=0;double x=std::stod(item,&pos);if(pos!=item.size()||!std::isfinite(x))throw std::runtime_error("invalid numeric CSV");v.push_back(x);}if(s[std::string(s).size()-1]==',')throw std::runtime_error("trailing comma");return v;}
int model_index(const char*id){if(!id)throw std::runtime_error("missing model");const auto&ms=atlas::models();for(size_t i=0;i<ms.size();++i)if(ms[i].id==id)return int(i);throw std::runtime_error("unknown model");}
const char* failure(const std::string&message){output="{\"ok\":false,\"message\":"+quote(message)+"}";return output.c_str();}
atlas::State params_for(int m,const char*s){auto p=parse_csv(s);if(p.empty())p=atlas::default_parameters(m);if(!atlas::valid_parameters(m,p))throw std::runtime_error("parameter length, bounds or finiteness invalid");return p;}
atlas::State state_for(int m,const char*s){auto z=parse_csv(s);if(z.empty())z=atlas::initial_state(m);if(z.size()!=atlas::initial_state(m).size())throw std::runtime_error("state length invalid");return z;}
}

extern "C" ATLAS_EXPORT const char* atlas_describe(){return atlas::describe_models();}
extern "C" ATLAS_EXPORT const char* atlas_run(const char*id,const char*parameters,const char*initial,int protocol,double target,int steps,int cycles){
    try{
        int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial);
        const auto start=std::chrono::steady_clock::now();auto run=atlas::run_protocol(m,z,p,protocol,target,steps,cycles);
        const double elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(run.ok?"true":"false")<<",\"message\":"<<quote(run.message)<<",\"schema_version\":\"0.1\",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())<<",\"model\":"<<quote(id)<<",\"elapsed_ms\":"<<elapsed<<",\"parameters\":";array(o,p);o<<",\"initial\":";array(o,z);
        o<<",\"protocol\":"<<protocol<<",\"target\":"<<target<<",\"steps\":"<<steps<<",\"cycles\":"<<cycles<<",\"points\":[";
        for(size_t i=0;i<run.points.size();++i){if(i)o<<',';const auto&point=run.points[i];const auto&v=point.state;auto sigma=atlas::tensor_from(v,0);
            o<<"{\"control\":"<<point.control<<",\"strain\":";array(o,atlas::State(point.strain.v.begin(),point.strain.v.end()));o<<",\"state\":";array(o,v);
            o<<",\"p\":"<<atlas::trace(sigma)/3<<",\"q\":"<<std::sqrt(1.5*atlas::dot(atlas::dev(sigma),atlas::dev(sigma)))<<",\"q_signed\":"<<v[0]-.5*(v[1]+v[2])<<",\"u\":"<<point.pore_pressure<<",\"iterations\":"<<point.diagnostics.iterations<<",\"substeps\":"<<point.diagnostics.substeps<<",\"rejected\":"<<point.diagnostics.rejected<<",\"error\":"<<point.diagnostics.error<<'}';
        }
        o<<"]}";output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_evaluate(const char*id,const char*parameters,const char*current,const char*previous,const char*strain){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,current),zn=state_for(m,previous),d=parse_csv(strain);if(d.size()!=6)throw std::runtime_error("six Mandel strain components required");atlas::State out;
        if(!atlas::evaluate_model(m,z,zn,atlas::tensor_from(d,0),p,out)||!atlas::finite(out))return failure("invalid model domain or nonfinite equation value");
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":true,\"values\":";array(o,out);o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_integrate(const char*id,const char*parameters,const char*initial,const char*strain){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial),d=parse_csv(strain);if(d.size()!=6)throw std::runtime_error("six Mandel strain components required");auto result=atlas::integrate(m,z,atlas::tensor_from(d,0),p);
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(result.ok?"true":"false")<<",\"message\":"<<quote(result.message)<<",\"state\":";array(o,result.state);o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_evaluate_time(const char*id,const char*parameters,const char*current,const char*rate,double time){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,current),d=parse_csv(rate);
        if(!atlas::models()[m].physical_time)throw std::runtime_error("physical-time ODE model required");
        if(d.size()!=6)throw std::runtime_error("six Mandel strain-rate components required");
        atlas::State out;
        if(!atlas::evaluate_model(m,z,z,atlas::tensor_from(d,0),p,out,false,time)||!atlas::finite(out))return failure("invalid model domain or nonfinite rate");
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":true,\"values\":";array(o,out);o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
// Versioned additive API: existing untimed callers keep their original contract.
extern "C" ATLAS_EXPORT const char* atlas_integrate_time(const char*id,const char*parameters,const char*initial,const char*rate,double start_time,double duration,double rtol,double atol,double min_step,double max_step,int max_substeps){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial),d=parse_csv(rate);
        if(d.size()!=6)throw std::runtime_error("six Mandel strain-rate components required");
        atlas::TimeSettings settings;settings.relative_tolerance=rtol;settings.absolute_tolerance=atol;
        settings.minimum_step=min_step;settings.maximum_step=max_step;settings.maximum_substeps=max_substeps;
        auto result=atlas::integrate_time(m,z,atlas::tensor_from(d,0),p,start_time,duration,settings);
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(result.ok?"true":"false")<<",\"schema_version\":\"0.2\",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())<<",\"model\":"<<quote(id)<<",\"message\":"<<quote(result.message)<<",\"time\":";
        if(std::isfinite(result.time))o<<result.time;else o<<"null";
        o<<",\"state\":";array(o,result.state);
        o<<",\"parameters\":";array(o,p);o<<",\"initial\":";array(o,z);o<<",\"strain_rate\":";array(o,d);
        o<<",\"start_time\":";if(std::isfinite(start_time))o<<start_time;else o<<"null";
        o<<",\"duration\":";if(std::isfinite(duration))o<<duration;else o<<"null";
        // Invalid nonfinite settings are reported as failure, without emitting invalid JSON.
        auto setting=[&](const char* name,double value){o<<",\""<<name<<"\":";if(std::isfinite(value))o<<value;else o<<"null";};
        o<<",\"solver\":{\"method\":\"midpoint-step-doubling\"";
        setting("relative_tolerance",rtol);setting("absolute_scale_fraction",atol);
        setting("minimum_step",min_step);setting("maximum_step",max_step);o<<",\"maximum_substeps\":"<<max_substeps<<",\"maximum_depth\":"<<settings.maximum_depth<<'}';
        o<<",\"substeps\":"<<result.diagnostics.substeps<<",\"rejected\":"<<result.diagnostics.rejected<<",\"temporal_error_norm\":"<<result.diagnostics.error<<'}';
        output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
#ifndef __EMSCRIPTEN__
int main(int argc,char**argv){
    if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<atlas_describe()<<'\n';return 0;}
    if(argc==2&&std::string(argv[1])=="--list"){for(const auto&m:atlas::models())std::cout<<m.id<<'\n';return 0;}
    std::map<std::string,std::string> args;const char*response=nullptr;
    try{
        for(int i=1;i<argc;i+=2){if(i+1>=argc)throw std::runtime_error("arguments require --key value pairs");std::string key=argv[i];if(args.count(key))throw std::runtime_error("duplicate option");args[key]=argv[i+1];}
        const std::vector<std::string> known={"--model","--parameters","--initial","--protocol","--target","--steps","--cycles","--mode","--current","--strain","--strain-rate","--start-time","--duration","--rtol","--atol","--min-time-step","--max-time-step","--max-substeps"};
        for(const auto&arg:args)if(std::find(known.begin(),known.end(),arg.first)==known.end())throw std::runtime_error("unknown option: "+arg.first);
        auto get=[&](const std::string&key,const std::string&fallback=""){auto i=args.find(key);return i==args.end()?fallback:i->second;};
        auto num=[&](const std::string&key,const std::string&fallback){auto s=get(key,fallback);size_t pos=0;double v=std::stod(s,&pos);if(pos!=s.size()||!std::isfinite(v))throw std::runtime_error("invalid number: "+key);return v;};
        auto integer=[&](const std::string&key,const std::string&fallback){double x=num(key,fallback);if(x!=std::floor(x)||std::abs(x)>1000000)throw std::runtime_error("invalid integer: "+key);return int(x);};
        auto id=get("--model"),p=get("--parameters"),z=get("--initial"),mode=get("--mode","run"),d=get("--strain"),current=get("--current");
        const std::vector<std::string> temporal={"--strain-rate","--start-time","--duration","--rtol","--atol","--min-time-step","--max-time-step","--max-substeps"};
        const bool timed=mode=="integrate-time"||mode=="evaluate-time";
        for(const auto& arg:args){
            const bool time_option=std::find(temporal.begin(),temporal.end(),arg.first)!=temporal.end();
            if(!timed&&time_option)throw std::runtime_error("physical-time options require a timed mode");
            if(timed&&!time_option&&arg.first!="--model"&&arg.first!="--mode"&&arg.first!="--parameters"&&arg.first!="--initial")throw std::runtime_error("option unsupported by timed mode: "+arg.first);
            if(mode=="evaluate-time"&&time_option&&arg.first!="--strain-rate"&&arg.first!="--start-time")throw std::runtime_error("integration settings are unsupported by rate evaluation");
        }
        if(mode=="evaluate-time")response=atlas_evaluate_time(id.c_str(),p.c_str(),z.c_str(),get("--strain-rate").c_str(),num("--start-time","nan"));
        else if(mode=="integrate-time")response=atlas_integrate_time(id.c_str(),p.c_str(),z.c_str(),get("--strain-rate").c_str(),num("--start-time","0"),num("--duration","nan"),num("--rtol","1e-6"),num("--atol","1e-9"),num("--min-time-step","1e-12"),num("--max-time-step","1e6"),integer("--max-substeps","20000"));
        else if(mode=="evaluate")response=atlas_evaluate(id.c_str(),p.c_str(),current.c_str(),z.c_str(),d.c_str());
        else if(mode=="integrate")response=atlas_integrate(id.c_str(),p.c_str(),z.c_str(),d.c_str());
        else if(mode=="run")response=atlas_run(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),num("--target","0.01"),integer("--steps","100"),integer("--cycles","0"));
        else throw std::runtime_error("unknown mode");
    }catch(const std::exception&e){response=failure(e.what());}
    std::cout<<response<<'\n';return output.find("\"ok\":true")!=std::string::npos?0:1;
}
#endif
