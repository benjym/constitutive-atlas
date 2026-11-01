// Diagnostic only: common generated residual with all current/previous/control
// AD columns. Contains no Duncan equations or handwritten material update.
#include "atlas/solver.hpp"
#include <sstream>
#include <iomanip>
#include <cstdlib>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define STUDY_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define STUDY_EXPORT
#endif
namespace {std::string jacobian_output;
std::vector<double> csv(const char*s){std::vector<double>v;std::istringstream in(s?s:"");std::string item;while(std::getline(in,item,',')){size_t n=0;double x=std::stod(item,&n);if(n!=item.size()||!std::isfinite(x))throw std::runtime_error("invalid diagnostic wire");v.push_back(x);}return v;}}
extern "C" STUDY_EXPORT const char* atlas_study_admissible(const char*state,const char*parameters){try{return atlas::solution_admissible(0,csv(state),csv(parameters))?"{\"ok\":true}":"{\"ok\":false}";}catch(...){return "{\"ok\":false}";}}
extern "C" STUDY_EXPORT const char* atlas_study_jacobian(const char*current,const char*previous,const char*strain,const char*parameters){
 try {using namespace atlas;auto z=csv(current),zn=csv(previous),de=csv(strain),p=csv(parameters);if(z.size()!=7||zn.size()!=7||de.size()!=6||p.size()!=10)throw std::runtime_error("diagnostic shape");std::vector<Jet>x(7),xn(7),r;Sym<Jet>d;
 for(int i=0;i<7;++i){x[i]=Jet(z[i]);xn[i]=Jet(zn[i]);x[i].d[i]=100000.;xn[i].d[i+7]=100000.;}
 for(int i=0;i<6;++i){d.v[i]=Jet(de[i]);d.v[i].d[i+14]=1.;}
 if(!evaluate_model(0,x,xn,d,p,r))throw std::runtime_error("diagnostic residual domain");std::ostringstream out;out<<std::setprecision(17)<<"{\"ok\":true,\"jacobian\":[";
 for(int i=0;i<7;++i){if(i)out<<',';out<<'[';for(int j=0;j<20;++j){if(j)out<<',';if(!std::isfinite(r[i].d[j]))throw std::runtime_error("nonfinite diagnostic derivative");out<<r[i].d[j]/100000.;}out<<']';}out<<"]}";jacobian_output=out.str();
 }catch(...){jacobian_output="{\"ok\":false}";}return jacobian_output.c_str();
}
