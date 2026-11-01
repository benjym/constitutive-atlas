#include "atlas/tensor.hpp"
#include <sstream>
#include <iomanip>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define SCALAR_PROBE_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define SCALAR_PROBE_EXPORT
#endif
static void scalar(std::ostream& out,double v){
 out<<"{\"classification\":\""<<(std::isnan(v)?"nan":std::isinf(v)?"infinity":"finite")<<"\",\"signbit\":"<<(std::signbit(v)?"true":"false");
 if(std::isfinite(v))out<<",\"value\":"<<std::setprecision(17)<<v;out<<'}';
}
extern "C" SCALAR_PROBE_EXPORT const char* atlas_scalar_functions_probe(int kind,double a,double b,int seeds){
 static std::string result;std::ostringstream out;out<<"{\"value\":";
 if(kind==0)scalar(out,atlas_scalar_power(a,b));
 else if(kind==1)scalar(out,atlas_cyclic_sine(a));
 else if(kind==2){atlas::Jet x(a),y(b);if(seeds&1)x.d[0]=1;if(seeds&2)y.d[1]=1;const auto z=atlas::apow(x,y);scalar(out,z.v);out<<",\"derivatives\":[";for(int i=0;i<atlas::max_derivatives;i++){if(i)out<<',';scalar(out,z.d[i]);}out<<']';}
 else return "{\"error\":\"unknown probe kind\"}";
 out<<'}';result=out.str();return result.c_str();
}
