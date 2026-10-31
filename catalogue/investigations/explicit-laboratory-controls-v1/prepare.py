from pathlib import Path
import json,hashlib,shutil
root=Path('/Users/bmar5496/code/constitutive-atlas'); stage=Path(__file__).parent
for name in ['cpp/main.cpp','cpp/include/atlas/solver.hpp']:
 p=stage/'proposed'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((root/name).read_bytes())
p=stage/'proposed/cpp/include/atlas/solver.hpp';s=p.read_text()
old='inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){'
new='inline Run run_protocol_impl(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings,const State*controls){'
assert s.count(old)==1;s=s.replace(old,new)
old='double control=cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps;'
new='double control=controls?(*controls)[i]:(cycles?target*std::sin(2*3.141592653589793*cycles*i/steps):target*i/steps);'
assert s.count(old)==1;s=s.replace(old,new)
append='''
// Legacy producers retain their original arithmetic and endpoint semantics.
inline Run run_protocol(int model,const State&initial,const State&p,int protocol,double target,int steps,int cycles,const IntegrationSettings&settings={}){
    return run_protocol_impl(model,initial,p,protocol,target,steps,cycles,settings,nullptr);
}
// laboratory-controls-0.1: cumulative change relative to the initial point.
// Protocol 3 specifies deviator stress change (Pa); all others specify strain.
// The original controller consumes differences of consecutive caller values.
// No interpolation, resampling, waveform generation or endpoint snapping.
inline Run run_protocol_controls(int model,const State&initial,const State&p,int protocol,const State&controls,const IntegrationSettings&settings={}){
    Run invalid;invalid.settings=settings;
    if(controls.size()<2||controls.size()>5001||controls.front()!=0){
        invalid.message="explicit controls require 2..5001 points beginning at zero";return invalid;
    }
    double amplitude=0;
    for(double control:controls){
        if(!std::isfinite(control)){invalid.message="explicit controls must be finite";return invalid;}
        amplitude=std::max(amplitude,std::abs(control));
    }
    return run_protocol_impl(model,initial,p,protocol,amplitude,int(controls.size())-1,0,settings,&controls);
}
'''
pos=s.rfind('\n}');assert pos>0;s=s[:pos]+ '\n'+append+s[pos:];p.write_text(s)
p=stage/'proposed/cpp/main.cpp';s=p.read_text()
s=s.replace('int cycles,const char*settings_csv){\n    try{','int cycles,const char*settings_csv,const atlas::State*controls=nullptr){\n    try{',1)
s=s.replace('auto run=atlas::run_protocol(m,z,p,protocol,target,steps,cycles,settings);','auto run=controls?atlas::run_protocol_controls(m,z,p,protocol,*controls,settings):atlas::run_protocol(m,z,p,protocol,target,steps,cycles,settings);',1)
old='        o<<",\\\"protocol\\\":"<<protocol<<",\\\"target\\\":"<<target<<",\\\"steps\\\":"<<steps<<",\\\"cycles\\\":"<<cycles<<",\\\"points\\\":[";'
new='''        o<<",\\\"protocol\\\":"<<protocol;
        if(controls){o<<",\\\"api_version\\\":\\\"experimental-laboratory-controls-0.1\\\",\\\"loading\\\":{\\\"version\\\":\\\"laboratory-controls-0.1\\\",\\\"controls\\\":";array(o,*controls);o<<"},\\\"steps\\\":"<<(controls->empty()?0:controls->size()-1);}
        else o<<",\\\"target\\\":"<<target<<",\\\"steps\\\":"<<steps<<",\\\"cycles\\\":"<<cycles;
        o<<",\\\"points\\\":[";'''
assert old in s;s=s.replace(old,new,1)
needle='extern "C" ATLAS_EXPORT const char* atlas_evaluate('
pos=s.index(needle)
new='''extern "C" ATLAS_EXPORT const char* atlas_run_controls_with_settings(const char*id,const char*parameters,const char*initial,int protocol,const char*controls_csv,const char*settings){
    try{auto controls=parse_csv(controls_csv);return run_response(id,parameters,initial,protocol,0,0,0,settings?settings:"",&controls);}
    catch(const std::exception&e){return failure(e.what());}
}
'''
s=s[:pos]+new+s[pos:]
s=s.replace('"--recorded-restarts"};','"--recorded-restarts","--laboratory-controls-file"};',1)
s=s.replace('&&mode!="recorded")throw std::runtime_error("incremental settings require run, integrate or linearize mode")','&&mode!="recorded"&&mode!="run-controls")throw std::runtime_error("incremental settings require run, run-controls, integrate, linearize or recorded mode")',1)
needle='        if(mode=="linearize"){'
new='''        if(mode!="run-controls"&&args.count("--laboratory-controls-file"))throw std::runtime_error("laboratory controls file requires run-controls mode");
        if(mode=="run-controls"){
            const std::vector<std::string> allowed={"--mode","--model","--parameters","--initial","--protocol","--integration-settings","--laboratory-controls-file"};
            for(const auto& arg:args)if(std::find(allowed.begin(),allowed.end(),arg.first)==allowed.end())throw std::runtime_error("option unsupported by run-controls mode: "+arg.first);
        }
'''
assert needle in s;s=s.replace(needle,new+needle,1)
needle='        else if(mode=="schedule")response='
new='''        else if(mode=="run-controls"){
            std::ifstream in(get("--laboratory-controls-file"),std::ios::binary);
            if(!in)throw std::runtime_error("cannot read --laboratory-controls-file");
            std::string controls;char ch;
            while(in.get(ch)){if(controls.size()>=2000000)throw std::runtime_error("laboratory controls file exceeds 2 MB");controls+=ch;}
            if(!in.eof())throw std::runtime_error("laboratory controls read failed");
            response=atlas_run_controls_with_settings(id.c_str(),p.c_str(),z.c_str(),integer("--protocol","1"),controls.c_str(),get("--integration-settings").c_str());
        }
'''
assert needle in s;s=s.replace(needle,new+needle,1)
p.write_text(s)
print('Prepared additive API in',stage/'proposed')
