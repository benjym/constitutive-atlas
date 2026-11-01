#include "atlas/schedule.hpp"
#include "atlas/recorded.hpp"
#include "atlas/stress_observables.hpp"
#include <fstream>
#include <cctype>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <map>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <limits>
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
// Exact finite binary64 wire, independent of decimal conversion and libm.
// Canonical lowercase uint64 hexadecimal, 16 digits per cumulative control.
atlas::State parse_control_bits(const char*csv){
    static_assert(sizeof(double)==sizeof(std::uint64_t)&&std::numeric_limits<double>::is_iec559&&std::numeric_limits<double>::digits==53&&std::numeric_limits<double>::radix==2,"binary64 controls require IEEE double");
    if(!csv)throw std::runtime_error("missing explicit control bits");
    const std::string wire(csv);atlas::State controls;
    if(wire.size()<33||wire.size()>85016)throw std::runtime_error("explicit controls require 2..5001 binary64 hex values");
    size_t start=0;
    while(start<wire.size()){
        const size_t end=wire.find(',',start),count=(end==std::string::npos?wire.size():end)-start;
        if(count!=16||controls.size()>=5001)throw std::runtime_error("control bits require exactly 16 lowercase hex digits");
        std::uint64_t bits=0;
        for(size_t j=start;j<start+16;++j){const char c=wire[j];
            if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))throw std::runtime_error("control bits require exactly 16 lowercase hex digits");
            bits=(bits<<4)|std::uint64_t(c<='9'?c-'0':c-'a'+10);
        }
        if((bits&0x7ff0000000000000ULL)==0x7ff0000000000000ULL)throw std::runtime_error("explicit controls must be finite");
        double value;std::memcpy(&value,&bits,sizeof value);
        if(!std::isfinite(value))throw std::runtime_error("explicit controls must be finite");
        controls.push_back(value);
        if(end==std::string::npos)break;
        start=end+1;if(start==wire.size())throw std::runtime_error("trailing control comma");
    }
    return controls;
}
void control_bits(std::ostream&o,const atlas::State&controls){
    o<<'[';for(size_t i=0;i<controls.size();++i){if(i)o<<',';std::uint64_t bits;std::memcpy(&bits,&controls[i],sizeof bits);
        std::ostringstream hex;hex<<std::hex<<std::setfill('0')<<std::setw(16)<<bits;o<<quote(hex.str());}o<<']';
}
int model_index(const char*id){if(!id)throw std::runtime_error("missing model");const auto&ms=atlas::models();for(size_t i=0;i<ms.size();++i)if(ms[i].id==id)return int(i);throw std::runtime_error("unknown model");}
const char* failure(const std::string&message){output="{\"ok\":false,\"message\":"+quote(message)+"}";return output.c_str();}
atlas::State params_for(int m,const char*s){auto p=parse_csv(s);if(p.empty())p=atlas::default_parameters(m);if(!atlas::valid_parameters(m,p))throw std::runtime_error("parameter length, bounds or finiteness invalid");return p;}
atlas::State state_for(int m,const char*s){auto z=parse_csv(s);if(z.empty()){if(atlas::explicit_initialization_required(m))throw std::runtime_error("v0.3 requires explicit state; initial literals are examples only");z=atlas::initial_state(m);}if(z.size()!=atlas::initial_state(m).size())throw std::runtime_error("state length invalid");return z;}
atlas::IntegrationSettings settings_for(const char* csv){
    atlas::IntegrationSettings s;auto v=parse_csv(csv);if(v.empty())return s;
    if(v.size()!=6)throw std::runtime_error("six integration settings required");
    for(int i=2;i<6;++i)if(v[i]!=std::floor(v[i])||v[i]<0||v[i]>1000000)throw std::runtime_error("invalid integer integration setting");
    s.residual_tolerance=v[0];s.rate_tolerance=v[1];s.max_iterations=int(v[2]);
    s.max_depth=int(v[3]);s.max_substeps=int(v[4]);s.max_backtracks=int(v[5]);
    if(!atlas::valid_settings(s))throw std::runtime_error("invalid integration settings");return s;
}
void require_incremental_stress_contract(int model,bool scope_aware,const std::string& kind="laboratory"){
    const auto& m=atlas::models().at(model);
    if(m.physical_time||m.fields.empty()||m.fields.front().name!="sigma"||m.fields.front().offset!=0||m.fields.front().size!=6||m.fields.front().transient)
        throw std::runtime_error(kind+" requires incremental persistent Cauchy state sigma");
    if(!scope_aware&&m.stress_scope!=atlas::StressScope::effective)
        throw std::runtime_error("legacy "+kind+" contract requires effective stress");
    if(scope_aware&&m.stress_scope!=atlas::StressScope::effective&&m.stress_scope!=atlas::StressScope::total)
        throw std::runtime_error("scoped "+kind+" contract requires declared effective or total stress");
}
void write_laboratory_scope(std::ostream& o,int model,int protocol){
    const auto scope=atlas::models().at(model).stress_scope;
    o<<",\"api_version\":\"experimental-laboratory-scope-0.1\",\"stress\":{\"source\":\"state\",\"name\":\"sigma\",\"measure\":\"cauchy\",\"scope\":"
     <<quote(scope==atlas::StressScope::effective?"effective":"total")<<",\"tensor_representation\":\"mandel\",\"sign\":\"compression_positive\"},\"pore_pressure\":{\"quantity\":\"change\",\"availability\":";
    if(atlas::laboratory_pore_reconstruction(scope,protocol))
        o<<"\"reconstructed\",\"assumption\":\"fixed_radial_total_stress_incompressible_fluid_and_grains\"}";
    else o<<"\"unavailable\",\"reason\":"<<quote(scope==atlas::StressScope::total?"total_stress_without_pore_pressure_law":"not_reconstructed_for_protocol")<<'}';
}
void write_settings(std::ostream& o,const atlas::IntegrationSettings& s){
    o<<"{\"version\":\"incremental-settings-0.1\",\"norm\":\"scaled_component_max\",\"residual_tolerance\":"<<s.residual_tolerance
      <<",\"rate_tolerance\":"<<s.rate_tolerance<<",\"max_iterations\":"<<s.max_iterations<<",\"max_depth\":"<<s.max_depth
      <<",\"max_substeps\":"<<s.max_substeps<<",\"max_backtracks\":"<<s.max_backtracks<<'}';
}
}

extern "C" ATLAS_EXPORT const char* atlas_describe(){return atlas::describe_models();}
static const char* run_response(const char*id,const char*parameters,const char*initial,int protocol,double target,int steps,int cycles,const char*settings_csv,const atlas::State*controls=nullptr,bool research_range=false,bool scope_aware=false){
    try{
        int m=model_index(id);require_incremental_stress_contract(m,scope_aware);auto p=params_for(m,parameters),z=state_for(m,initial);
        const auto settings=settings_for(settings_csv);
        const auto start=std::chrono::steady_clock::now();auto run=controls?atlas::run_protocol_controls(m,z,p,protocol,*controls,settings,research_range?atlas::LaboratoryRange::ResearchQuarterStrain:atlas::LaboratoryRange::Interactive):atlas::run_protocol(m,z,p,protocol,target,steps,cycles,settings);
        const double elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(run.ok?"true":"false")<<",\"message\":"<<quote(run.message)<<",\"schema_version\":\"0.1\",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())<<",\"model\":"<<quote(id)<<",\"elapsed_ms\":"<<elapsed<<",\"parameters\":";array(o,p);o<<",\"initial\":";array(o,z);
        if(settings_csv){o<<",\"integration_settings\":";write_settings(o,run.settings);}
        o<<",\"protocol\":"<<protocol;
        if(scope_aware)write_laboratory_scope(o,m,protocol);
        if(research_range)o<<",\"research_scope\":{\"version\":\"quarter-strain-operational-0.1\",\"maximum_strain_amplitude\":0.25,\"finite_kinematics_verified\":false}";
        if(controls){if(!scope_aware)o<<",\"api_version\":\"experimental-laboratory-controls-0.1\"";o<<",\"loading\":{\"version\":\"laboratory-controls-0.1\",\"controls\":";array(o,*controls);o<<",\"encoding\":\"ieee754-binary64-hex\",\"controls_bits\":";control_bits(o,*controls);o<<"},\"steps\":"<<(controls->empty()?0:controls->size()-1);}
        else o<<",\"target\":"<<target<<",\"steps\":"<<steps<<",\"cycles\":"<<cycles;
        o<<",\"points\":[";
        for(size_t i=0;i<run.points.size();++i){if(i)o<<',';const auto&point=run.points[i];const auto&v=point.state;auto sigma=atlas::tensor_from(v,0);
            o<<"{\"control\":"<<point.control<<",\"strain\":";array(o,atlas::State(point.strain.v.begin(),point.strain.v.end()));o<<",\"state\":";array(o,v);
            o<<",\"p\":"<<atlas::trace(sigma)/3<<",\"q\":"<<atlas::deviatoric_stress_magnitude(sigma)<<",\"q_signed\":"<<v[0]-.5*(v[1]+v[2])<<",\"u\":";if(scope_aware&&!atlas::laboratory_pore_reconstruction(atlas::models()[m].stress_scope,protocol))o<<"null";else o<<point.pore_pressure;o<<",\"iterations\":"<<point.diagnostics.iterations<<",\"substeps\":"<<point.diagnostics.substeps<<",\"rejected\":"<<point.diagnostics.rejected<<",\"error\":"<<point.diagnostics.error<<'}';
        }
        o<<"]}";output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_run(const char*id,const char*parameters,const char*initial,int protocol,double target,int steps,int cycles){return run_response(id,parameters,initial,protocol,target,steps,cycles,nullptr);}
extern "C" ATLAS_EXPORT const char* atlas_run_with_settings(const char*id,const char*parameters,const char*initial,int protocol,double target,int steps,int cycles,const char*settings){return run_response(id,parameters,initial,protocol,target,steps,cycles,settings?settings:"");}
extern "C" ATLAS_EXPORT const char* atlas_run_controls_with_settings(const char*id,const char*parameters,const char*initial,int protocol,const char*controls_csv,const char*settings){
    try{auto controls=parse_control_bits(controls_csv);return run_response(id,parameters,initial,protocol,0,0,0,settings?settings:"",&controls);}
    catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_run_scope_with_settings(const char*id,const char*parameters,const char*initial,int protocol,double target,int steps,int cycles,const char*settings){
    return run_response(id,parameters,initial,protocol,target,steps,cycles,settings?settings:"",nullptr,false,true);
}
extern "C" ATLAS_EXPORT const char* atlas_run_controls_scope_with_settings(const char*id,const char*parameters,const char*initial,int protocol,const char*controls_csv,const char*settings){
    try{auto controls=parse_control_bits(controls_csv);return run_response(id,parameters,initial,protocol,0,0,0,settings?settings:"",&controls,false,true);}
    catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_evaluate(const char*id,const char*parameters,const char*current,const char*previous,const char*strain){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,current),zn=state_for(m,previous),d=parse_csv(strain);if(d.size()!=6)throw std::runtime_error("six Mandel strain components required");atlas::State out;
        if(!atlas::evaluate_model(m,z,zn,atlas::tensor_from(d,0),p,out)||!atlas::finite(out))return failure("invalid model domain or nonfinite equation value");
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":true,\"values\":";array(o,out);o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
static const char* integrate_response(const char*id,const char*parameters,const char*initial,const char*strain,const char*settings_csv){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial),d=parse_csv(strain);if(d.size()!=6)throw std::runtime_error("six Mandel strain components required");auto settings=settings_for(settings_csv);auto result=atlas::integrate(m,z,atlas::tensor_from(d,0),p,settings);
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(result.ok?"true":"false")<<",\"message\":"<<quote(result.message)<<",\"state\":";array(o,result.state);o<<",\"diagnostics\":{\"iterations\":"<<result.diagnostics.iterations<<",\"substeps\":"<<result.diagnostics.substeps<<",\"rejected\":"<<result.diagnostics.rejected<<",\"increment_fractions\":";array(o,result.diagnostics.increment_fractions);o<<'}';
        if(settings_csv){o<<",\"integration_settings\":";write_settings(o,result.settings);
            o<<",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())<<",\"model\":"<<quote(id)<<",\"parameters\":";array(o,p);
            o<<",\"initial\":";array(o,z);o<<",\"strain\":";array(o,d);}
        o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_integrate(const char*id,const char*parameters,const char*initial,const char*strain){return integrate_response(id,parameters,initial,strain,nullptr);}
extern "C" ATLAS_EXPORT const char* atlas_integrate_with_settings(const char*id,const char*parameters,const char*initial,const char*strain,const char*settings){return integrate_response(id,parameters,initial,strain,settings?settings:"");}
static const char* linearize_response(const char*id,const char*parameters,const char*initial,const char*strain,const char*settings_csv){
    try{
        int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial),d=parse_csv(strain);
        if(d.size()!=6)throw std::runtime_error("six Mandel strain components required");
        const auto settings=settings_for(settings_csv);
        const auto result=atlas::linearize_update(m,z,atlas::tensor_from(d,0),p,settings);
        const auto& a=result.advance;const auto& diag=a.diagnostics;
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(a.ok?"true":"false")
          <<",\"tangent_ok\":"<<(result.tangent_ok?"true":"false")
          <<",\"api_version\":\"experimental-update-linearization-0.1\",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())
          <<",\"model\":"<<quote(id)<<",\"message\":"<<quote(a.message)<<",\"tangent_message\":"<<quote(result.message)
          <<",\"partition_policy\":\"accepted_fixed\",\"branch_policy\":\"selected_fixed\""
          <<",\"reset_guard_at_zero\":"<<(result.reset_guard_at_zero?"true":"false")<<",\"parameters\":";array(o,p);
        o<<",\"initial\":";array(o,z);o<<",\"strain\":";array(o,d);o<<",\"state\":";array(o,a.state);
        o<<",\"state_fields\":[";const auto& fields=atlas::models()[m].fields;
        for(size_t i=0;i<fields.size();++i){if(i)o<<',';o<<"{\"name\":"<<quote(fields[i].name)<<",\"offset\":"<<fields[i].offset<<",\"size\":"<<fields[i].size<<'}';}
        o<<"],\"tangent_columns\":[\"xx\",\"yy\",\"zz\",\"sqrt2_xy\",\"sqrt2_yz\",\"sqrt2_xz\"],\"state_tangent\":";
        if(!result.tangent_ok)o<<"null";
        else{ o<<'[';for(size_t i=0;i<result.state_tangent.size();++i){if(i)o<<',';array(o,result.state_tangent[i]);}o<<']'; }
        o<<",\"diagnostics\":{\"iterations\":"<<diag.iterations<<",\"substeps\":"<<diag.substeps<<",\"rejected\":"<<diag.rejected<<",\"increment_fractions\":";
        array(o,diag.increment_fractions);o<<",\"error\":";if(std::isfinite(diag.error))o<<diag.error;else o<<"null";
        o<<'}';if(settings_csv){o<<",\"integration_settings\":";write_settings(o,a.settings);}o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception& e){
        output="{\"ok\":false,\"tangent_ok\":false,\"state_tangent\":null,\"message\":"+quote(e.what())+"}";
        return output.c_str();
    }
}
extern "C" ATLAS_EXPORT const char* atlas_linearize(const char*id,const char*parameters,const char*initial,const char*strain){return linearize_response(id,parameters,initial,strain,nullptr);}
extern "C" ATLAS_EXPORT const char* atlas_linearize_with_settings(const char*id,const char*parameters,const char*initial,const char*strain,const char*settings){return linearize_response(id,parameters,initial,strain,settings?settings:"");}
// Numeric wire: 6 rows of (stress tag, six coefficients), and 2..5001
// rows of (coordinate, six absolute targets). No file I/O in the C/Wasm API.
static const char* recorded_response(const char*id,const char*parameters,const char*initial,
        const char*initial_strain,const char*controls,const char*knots,const char*material_settings,const char*control_settings,const char*restart_settings,const char*requested_scope=nullptr){
    try{
        int m=model_index(id);require_incremental_stress_contract(m,requested_scope!=nullptr,"recorded");
        if(requested_scope&&std::string(requested_scope)!=(atlas::models()[m].stress_scope==atlas::StressScope::effective?"effective":"total"))
            throw std::runtime_error("recorded stress scope does not match model");
        auto p=params_for(m,parameters),z=state_for(m,initial);
        auto e=parse_csv(initial_strain),c=parse_csv(controls),k=parse_csv(knots),v=parse_csv(control_settings);
        if(e.size()!=6||c.size()!=42||k.size()<14||k.size()>35007||k.size()%7)
            throw std::runtime_error("invalid recorded wire layout");
        atlas::RecordedPath path;path.initial_strain=atlas::tensor_from(e,0);
        for(int i=0;i<6;++i){
            if(c[7*i]!=0&&c[7*i]!=1)throw std::runtime_error("recorded stress tag must be 0 or 1");
            path.controls[i].stress=c[7*i]==1;
            for(int j=0;j<6;++j)path.controls[i].coefficients.v[j]=c[7*i+1+j];
        }
        for(size_t i=0;i<k.size();i+=7){atlas::RecordedKnot knot;knot.coordinate=k[i];
            for(int j=0;j<6;++j)knot.targets[j]=k[i+1+j];path.knots.push_back(knot);}
        atlas::RecordedSettings settings;settings.material=settings_for(material_settings);
        if(!v.empty()){
            if(v.size()!=5)throw std::runtime_error("five recorded control settings required");
            for(int i=1;i<4;++i)if(v[i]!=std::floor(v[i])||v[i]<0||v[i]>1000000)
                throw std::runtime_error("invalid integer recorded control setting");
            settings.control_tolerance=v[0];settings.max_iterations=int(v[1]);settings.max_backtracks=int(v[2]);
            settings.max_material_trials=int(v[3]);settings.finite_difference_step=v[4];
        }
        if(restart_settings){
            auto restarts=parse_csv(restart_settings);
            if(restarts.size()!=3||restarts[0]!=std::floor(restarts[0])||restarts[0]<0||restarts[0]>16||
               restarts[2]!=std::floor(restarts[2])||restarts[2]<1||restarts[2]>16)
                throw std::runtime_error("three valid recorded restart settings required");
            settings.max_restarts=int(restarts[0]);settings.restart_step=restarts[1];settings.restart_levels=int(restarts[2]);
        }
        if(!atlas::valid_recorded_settings(settings))throw std::runtime_error("invalid recorded settings");
        auto run=atlas::replay_recorded(m,z,p,path,settings);
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(run.ok?"true":"false")
          <<",\"api_version\":"<<quote(requested_scope?"experimental-recorded-replay-0.2":"experimental-recorded-replay-0.1")<<",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())
          <<",\"model\":"<<quote(id)<<",\"message\":"<<quote(run.message)<<",\"failed_knot\":"<<run.failed_knot
          <<",\"parameters\":";array(o,p);o<<",\"initial\":";array(o,z);o<<",\"initial_strain\":";array(o,e);
        if(requested_scope)o<<",\"stress\":{\"source\":\"state\",\"name\":\"sigma\",\"measure\":\"cauchy\",\"scope\":"<<quote(requested_scope)<<",\"tensor_representation\":\"mandel\",\"sign\":\"compression_positive\"}";
        o<<",\"controls_wire\":";array(o,c);o<<",\"knots_wire\":";array(o,k);
        o<<",\"integration_settings\":";write_settings(o,settings.material);
        o<<",\"control_settings\":{\"control_tolerance\":"<<settings.control_tolerance
          <<",\"max_iterations\":"<<settings.max_iterations<<",\"max_backtracks\":"<<settings.max_backtracks
          <<",\"max_material_trials\":"<<settings.max_material_trials<<",\"finite_difference_step\":"<<settings.finite_difference_step
          <<"}";
        if(restart_settings)o<<",\"restart_settings\":{\"max_restarts\":"<<settings.max_restarts
          <<",\"restart_step\":"<<settings.restart_step<<",\"restart_levels\":"<<settings.restart_levels
          <<"},\"restart_diagnostics\":{\"searches\":"<<run.restart_searches<<",\"material_trials\":"<<run.restart_trials
          <<",\"accepted\":"<<run.accepted_restarts<<"}";
        o<<",\"state\":";array(o,run.state);o<<",\"strain\":";array(o,atlas::State(run.strain.v.begin(),run.strain.v.end()));
        o<<",\"material_trials\":"<<run.material_trials<<",\"finite_difference_probes\":"<<run.finite_difference_probes
          <<",\"attempted_substeps\":"<<run.attempted_substeps<<",\"last_control_error\":";
        if(std::isfinite(run.last_control_error))o<<run.last_control_error;else o<<"null";
        o<<",\"last_trial_increment\":";array(o,atlas::State(run.last_trial_increment.v.begin(),run.last_trial_increment.v.end()));
        o<<",\"points\":[";
        for(size_t i=0;i<run.points.size();++i){if(i)o<<',';const auto& point=run.points[i];
            o<<"{\"coordinate\":"<<point.coordinate<<",\"state\":";array(o,point.state);
            o<<",\"strain\":";array(o,atlas::State(point.strain.v.begin(),point.strain.v.end()));
            o<<",\"control_error\":"<<point.control_error<<",\"diagnostics\":{\"iterations\":"<<point.diagnostics.iterations
              <<",\"substeps\":"<<point.diagnostics.substeps<<",\"rejected\":"<<point.diagnostics.rejected<<",\"error\":";
            if(std::isfinite(point.diagnostics.error))o<<point.diagnostics.error;else o<<"null";
            o<<",\"increment_fractions\":";array(o,point.diagnostics.increment_fractions);o<<"}}";
        }
        o<<"]}";output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
// Legacy endpoint keeps identical defaults and response shape. The additive
// endpoint requires explicit restart settings and reports their resolved policy.
extern "C" ATLAS_EXPORT const char* atlas_replay_recorded(const char*id,const char*p,const char*z,
        const char*e,const char*c,const char*k,const char*m,const char*control){
    return recorded_response(id,p,z,e,c,k,m,control,nullptr);
}
extern "C" ATLAS_EXPORT const char* atlas_replay_recorded_with_restarts(const char*id,const char*p,const char*z,
        const char*e,const char*c,const char*k,const char*m,const char*control,const char*restarts){
    return recorded_response(id,p,z,e,c,k,m,control,restarts?restarts:"");
}
// Scope must be supplied explicitly; a missing scope cannot select legacy.
extern "C" ATLAS_EXPORT const char* atlas_replay_recorded_scope(const char*id,const char*p,const char*z,
        const char*e,const char*c,const char*k,const char*m,const char*control,const char*scope){
    return recorded_response(id,p,z,e,c,k,m,control,nullptr,scope?scope:"");
}
extern "C" ATLAS_EXPORT const char* atlas_replay_recorded_scope_with_restarts(const char*id,const char*p,const char*z,
        const char*e,const char*c,const char*k,const char*m,const char*control,const char*restarts,const char*scope){
    return recorded_response(id,p,z,e,c,k,m,control,restarts?restarts:"",scope?scope:"");
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
extern "C" ATLAS_EXPORT const char* atlas_observe_time(const char*id,const char*parameters,const char*current,const char*rate,double time){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,current),d=parse_csv(rate);atlas::State values;
        if(!atlas::models()[m].physical_time||d.size()!=6||!atlas::observables(m,z,atlas::tensor_from(d,0),p,time,values))return failure("invalid observable input or domain");
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":true,\"values\":";array(o,values);o<<'}';output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
extern "C" ATLAS_EXPORT const char* atlas_run_schedule(const char*id,const char*parameters,const char*initial,const char*strain,const char*rate,const char*controls,const char*ids,double start,double rtol,double atol,double min_step,double max_step,int budget,double nonlinear_tolerance,int max_iterations){
    try{int m=model_index(id);auto p=params_for(m,parameters),z=state_for(m,initial),e=parse_csv(strain),d=parse_csv(rate),wire=parse_csv(controls);
        if(e.empty())e.assign(6,0);if(d.empty())d.assign(6,0);
        if(e.size()!=6||d.size()!=6||wire.empty()||wire.size()%20||wire.size()>2000)throw std::runtime_error("invalid schedule wire layout");
        std::vector<std::string> names;std::istringstream names_in(ids?ids:"");std::string name;
        while(std::getline(names_in,name,','))names.push_back(name);
        if(names.size()!=wire.size()/20)throw std::runtime_error("one segment ID per control row required");
        std::vector<atlas::Segment> segments;
        for(size_t row=0;row<names.size();++row){const size_t offset=row*20;atlas::Segment seg;seg.id=names[row];seg.duration=wire[offset];
            double samples=wire[offset+1];if(samples!=std::floor(samples)||samples<1||samples>5000)throw std::runtime_error("invalid sample count");seg.samples=int(samples);
            if(seg.id.empty()||seg.id.size()>64||!std::all_of(seg.id.begin(),seg.id.end(),[](unsigned char c){return std::isalnum(c)||c=='-'||c=='_';}))throw std::runtime_error("invalid segment ID");
            for(int j=0;j<6;++j){const size_t i=offset+2+3*j;double q=wire[i],kind=wire[i+1];if((q!=0&&q!=1)||kind!=std::floor(kind)||kind<0||kind>2)throw std::runtime_error("invalid component control tag");seg.controls[j]={q==1,int(kind),wire[i+2]};}
            segments.push_back(seg);
        }
        atlas::ScheduleSettings settings;settings.time.relative_tolerance=rtol;settings.time.absolute_tolerance=atol;settings.time.minimum_step=min_step;settings.time.maximum_step=max_step;settings.time.maximum_substeps=budget;settings.nonlinear_tolerance=nonlinear_tolerance;settings.maximum_iterations=max_iterations;
        if(!std::isfinite(start)||!atlas::valid_schedule_settings(settings))throw std::runtime_error("invalid physical time or numerical settings");
        auto run=atlas::run_schedule(m,z,p,atlas::tensor_from(e,0),atlas::tensor_from(d,0),start,segments,settings);
        std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":"<<(run.ok?"true":"false")<<",\"schema_version\":\"0.2\",\"units\":\"SI\",\"model\":"<<quote(id)<<",\"catalogue_hash\":"<<quote(atlas::catalogue_hash())<<",\"message\":"<<quote(run.message)<<",\"start_time\":"<<start<<",\"parameters\":";array(o,p);o<<",\"initial\":";array(o,z);o<<",\"initial_strain\":";array(o,e);o<<",\"initial_strain_rate\":";array(o,d);
        o<<",\"solver\":{\"method\":\"backward-euler-step-doubling\",\"relative_tolerance\":"<<rtol<<",\"absolute_scale_fraction\":"<<atol<<",\"minimum_step\":"<<min_step<<",\"maximum_step\":"<<max_step<<",\"maximum_substeps\":"<<budget<<",\"nonlinear_tolerance\":"<<nonlinear_tolerance<<",\"maximum_iterations\":"<<max_iterations<<",\"maximum_depth\":"<<settings.time.maximum_depth<<"},\"segments\":[";
        for(size_t i=0;i<segments.size();++i){if(i)o<<',';const auto& seg=segments[i];o<<"{\"id\":"<<quote(seg.id)<<",\"duration\":"<<seg.duration<<",\"samples\":"<<seg.samples<<",\"controls\":[";
            for(int j=0;j<6;++j){if(j)o<<',';const auto& c=seg.controls[j];o<<"{\"quantity\":"<<quote(c.stress?"stress":"strain")<<",\"kind\":"<<quote(c.kind==0?"hold":c.kind==1?"rate":"target");if(c.kind)o<<",\"value\":"<<c.value;o<<'}';}o<<"]}";}
        o<<"],\"points\":[";
        for(size_t i=0;i<run.points.size();++i){if(i)o<<',';const auto& pt=run.points[i];o<<"{\"time\":"<<pt.time<<",\"segment\":"<<pt.segment<<",\"side\":"<<quote(pt.transition?"right":"left")<<",\"state\":";array(o,pt.state);o<<",\"strain\":";array(o,atlas::State(pt.strain.v.begin(),pt.strain.v.end()));o<<",\"strain_rate\":[";
            for(int j=0;j<6;++j){if(j)o<<',';if(pt.transition&&pt.stress_controls[j])o<<"null";else o<<pt.rate.v[j];}o<<"],\"observables\":";array(o,pt.observables);
            o<<",\"iterations\":"<<pt.diagnostics.iterations<<",\"substeps\":"<<pt.diagnostics.substeps<<",\"rejected\":"<<pt.diagnostics.rejected<<",\"temporal_error_norm\":"<<pt.diagnostics.error<<",\"nonlinear_residual_norm\":"<<pt.nonlinear_error<<'}';}
        o<<"]}";output=o.str();return output.c_str();
    }catch(const std::exception&e){return failure(e.what());}
}
#ifndef __EMSCRIPTEN__
int main(int argc,char**argv){
    if(argc==2&&std::string(argv[1])=="--describe"){std::cout<<atlas_describe()<<'\n';return 0;}
    if(argc==2&&std::string(argv[1])=="--list"){for(const auto&m:atlas::models())std::cout<<m.id<<'\n';return 0;}
    std::map<std::string,std::string> args;const char*response=nullptr;
    try{
        for(int i=1;i<argc;i+=2){if(i+1>=argc)throw std::runtime_error("arguments require --key value pairs");std::string key=argv[i];if(args.count(key))throw std::runtime_error("duplicate option");args[key]=argv[i+1];}
        const std::vector<std::string> known={"--model","--parameters","--initial","--protocol","--target","--steps","--cycles","--mode","--current","--strain","--strain-rate","--start-time","--duration","--rtol","--atol","--min-time-step","--max-time-step","--max-substeps","--segments","--segment-ids","--initial-strain","--initial-strain-rate","--nonlinear-tolerance","--max-iterations","--integration-settings","--recorded-controls-file","--recorded-knots-file","--recorded-settings","--recorded-restarts","--recorded-stress-scope","--laboratory-controls-file","--response-contract"};
        for(const auto&arg:args)if(std::find(known.begin(),known.end(),arg.first)==known.end())throw std::runtime_error("unknown option: "+arg.first);
        auto get=[&](const std::string&key,const std::string&fallback=""){auto i=args.find(key);return i==args.end()?fallback:i->second;};
        auto num=[&](const std::string&key,const std::string&fallback){auto s=get(key,fallback);size_t pos=0;double v=std::stod(s,&pos);if(pos!=s.size()||!std::isfinite(v))throw std::runtime_error("invalid number: "+key);return v;};
        auto integer=[&](const std::string&key,const std::string&fallback){double x=num(key,fallback);if(x!=std::floor(x)||std::abs(x)>1000000)throw std::runtime_error("invalid integer: "+key);return int(x);};
        auto id=get("--model"),p=get("--parameters"),z=get("--initial"),mode=get("--mode","run"),d=get("--strain"),current=get("--current");
        const bool scope_aware=args.count("--response-contract")!=0;
        if(scope_aware&&((mode!="run"&&mode!="run-controls")||get("--response-contract")!="stress-scope-0.1"))
            throw std::runtime_error("response contract requires run/run-controls and stress-scope-0.1");
        if(args.count("--integration-settings")&&mode!="run"&&mode!="integrate"&&mode!="linearize"&&mode!="recorded"&&mode!="run-controls"&&mode!="run-research-controls")throw std::runtime_error("incremental settings require run, run-controls, integrate, linearize or recorded mode");
        if(mode!="run-controls"&&mode!="run-research-controls"&&args.count("--laboratory-controls-file"))throw std::runtime_error("laboratory controls file requires run-controls mode");
        if(mode=="run-controls"||mode=="run-research-controls"){
            const std::vector<std::string> allowed={"--mode","--model","--parameters","--initial","--protocol","--integration-settings","--laboratory-controls-file","--response-contract"};
            for(const auto& arg:args)if(std::find(allowed.begin(),allowed.end(),arg.first)==allowed.end())throw std::runtime_error("option unsupported by run-controls mode: "+arg.first);
        }
        if(mode=="linearize"){
            const std::vector<std::string> allowed={"--mode","--model","--parameters","--initial","--strain","--integration-settings"};
            for(const auto& arg:args)if(std::find(allowed.begin(),allowed.end(),arg.first)==allowed.end())
                throw std::runtime_error("option unsupported by linearize mode: "+arg.first);
        }
        const std::vector<std::string> temporal={"--strain-rate","--start-time","--duration","--rtol","--atol","--min-time-step","--max-time-step","--max-substeps","--segments","--segment-ids","--initial-strain","--initial-strain-rate","--nonlinear-tolerance","--max-iterations"};
        const bool timed=mode=="integrate-time"||mode=="evaluate-time"||mode=="observe-time"||mode=="schedule";
        for(const auto& arg:args){
            const bool time_option=std::find(temporal.begin(),temporal.end(),arg.first)!=temporal.end();
            if(!timed&&time_option&&!(mode=="recorded"&&arg.first=="--initial-strain"))throw std::runtime_error("physical-time options require a timed mode");
            if(timed&&!time_option&&arg.first!="--model"&&arg.first!="--mode"&&arg.first!="--parameters"&&arg.first!="--initial")throw std::runtime_error("option unsupported by timed mode: "+arg.first);
            if((mode=="evaluate-time"||mode=="observe-time")&&time_option&&arg.first!="--strain-rate"&&arg.first!="--start-time")throw std::runtime_error("integration settings are unsupported by rate evaluation");
        }
        for(const auto& arg:args){
            const std::vector<std::string> schedule_options={"--segments","--segment-ids","--initial-strain","--initial-strain-rate","--nonlinear-tolerance","--max-iterations"};
            if(mode!="schedule"&&!(mode=="recorded"&&arg.first=="--initial-strain")&&std::find(schedule_options.begin(),schedule_options.end(),arg.first)!=schedule_options.end())throw std::runtime_error("schedule option requires schedule mode");
            if(mode=="schedule"&&(arg.first=="--duration"||arg.first=="--strain-rate"))throw std::runtime_error("schedule duration and rates belong to its segments");
        }
        const std::vector<std::string> recorded_options={"--recorded-controls-file","--recorded-knots-file","--recorded-settings","--recorded-restarts","--recorded-stress-scope"};
        for(const auto& arg:args)if(mode!="recorded"&&std::find(recorded_options.begin(),recorded_options.end(),arg.first)!=recorded_options.end())
            throw std::runtime_error("recorded option requires recorded mode");
        if(mode=="recorded"){
            const std::vector<std::string> allowed={"--mode","--model","--parameters","--initial","--initial-strain","--integration-settings","--recorded-controls-file","--recorded-knots-file","--recorded-settings","--recorded-restarts","--recorded-stress-scope"};
            for(const auto& arg:args)if(std::find(allowed.begin(),allowed.end(),arg.first)==allowed.end())throw std::runtime_error("option unsupported by recorded mode: "+arg.first);
            auto read_wire=[&](const char* key){
                std::ifstream in(get(key),std::ios::binary);if(!in)throw std::runtime_error(std::string("cannot read ")+key);
                std::string data;char ch;while(in.get(ch)){
                    if(data.size()>=2000000)throw std::runtime_error("recorded wire file exceeds 2 MB");data+=ch;
                }
                if(!in.eof())throw std::runtime_error("recorded wire read failed");return data;
            };
            auto c=read_wire("--recorded-controls-file"),k=read_wire("--recorded-knots-file");
            response=recorded_response(id.c_str(),p.c_str(),z.c_str(),get("--initial-strain").c_str(),c.c_str(),k.c_str(),get("--integration-settings").c_str(),get("--recorded-settings").c_str(),args.count("--recorded-restarts")?get("--recorded-restarts").c_str():nullptr,args.count("--recorded-stress-scope")?get("--recorded-stress-scope").c_str():nullptr);
        }
        else if(mode=="run-controls"||mode=="run-research-controls"){
            std::ifstream in(get("--laboratory-controls-file"),std::ios::binary);
            if(!in)throw std::runtime_error("cannot read --laboratory-controls-file");
            std::string controls;char ch;
            while(in.get(ch)){if(controls.size()>=2000000)throw std::runtime_error("laboratory controls file exceeds 2 MB");controls+=ch;}
            if(!in.eof())throw std::runtime_error("laboratory controls read failed");
            if(controls.find('\0')!=std::string::npos)throw std::runtime_error("laboratory controls file contains NUL");
            if(mode=="run-research-controls"){
                auto values=parse_control_bits(controls.c_str());
                response=run_response(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),0,0,0,get("--integration-settings").c_str(),&values,true);
            }else response=(scope_aware?atlas_run_controls_scope_with_settings:atlas_run_controls_with_settings)(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),controls.c_str(),get("--integration-settings").c_str());
        }
        else if(mode=="schedule")response=atlas_run_schedule(id.c_str(),p.c_str(),z.c_str(),get("--initial-strain").c_str(),get("--initial-strain-rate").c_str(),get("--segments").c_str(),get("--segment-ids").c_str(),num("--start-time","0"),num("--rtol","1e-6"),num("--atol","1e-9"),num("--min-time-step","1e-12"),num("--max-time-step","1e6"),integer("--max-substeps","20000"),num("--nonlinear-tolerance","1e-10"),integer("--max-iterations","40"));
        else if(mode=="observe-time")response=atlas_observe_time(id.c_str(),p.c_str(),z.c_str(),get("--strain-rate").c_str(),num("--start-time","nan"));
        else if(mode=="evaluate-time")response=atlas_evaluate_time(id.c_str(),p.c_str(),z.c_str(),get("--strain-rate").c_str(),num("--start-time","nan"));
        else if(mode=="integrate-time")response=atlas_integrate_time(id.c_str(),p.c_str(),z.c_str(),get("--strain-rate").c_str(),num("--start-time","0"),num("--duration","nan"),num("--rtol","1e-6"),num("--atol","1e-9"),num("--min-time-step","1e-12"),num("--max-time-step","1e6"),integer("--max-substeps","20000"));
        else if(mode=="evaluate")response=atlas_evaluate(id.c_str(),p.c_str(),current.c_str(),z.c_str(),d.c_str());
        else if(mode=="integrate")response=args.count("--integration-settings")?atlas_integrate_with_settings(id.c_str(),p.c_str(),z.c_str(),d.c_str(),get("--integration-settings").c_str()):atlas_integrate(id.c_str(),p.c_str(),z.c_str(),d.c_str());
        else if(mode=="linearize")response=args.count("--integration-settings")?atlas_linearize_with_settings(id.c_str(),p.c_str(),z.c_str(),d.c_str(),get("--integration-settings").c_str()):atlas_linearize(id.c_str(),p.c_str(),z.c_str(),d.c_str());
        else if(mode=="run"&&scope_aware)response=atlas_run_scope_with_settings(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),num("--target","0.01"),integer("--steps","100"),integer("--cycles","0"),get("--integration-settings").c_str());
        else if(mode=="run")response=args.count("--integration-settings")?atlas_run_with_settings(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),num("--target","0.01"),integer("--steps","100"),integer("--cycles","0"),get("--integration-settings").c_str()):atlas_run(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),num("--target","0.01"),integer("--steps","100"),integer("--cycles","0"));
        else throw std::runtime_error("unknown mode");
    }catch(const std::exception&e){response=failure(e.what());}
    std::cout<<response<<'\n';return output.find("\"ok\":true")!=std::string::npos?0:1;
}
#endif
