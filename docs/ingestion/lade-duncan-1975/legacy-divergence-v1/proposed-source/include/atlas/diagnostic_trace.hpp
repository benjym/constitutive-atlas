#pragma once
#include <iostream>
#include <iomanip>
namespace atlas {
// Observational, unconditionally enabled only in this diagnostic source copy.
inline void diagnostic_trace(const char*phase,int index,const State&parent,const Sym<double>&de,const State&candidate,const State&residual={},const std::vector<State>*jac=nullptr){
 static unsigned long sequence=0;
 auto array=[](const auto&values){std::cerr<<'[';bool first=true;for(double v:values){if(!first)std::cerr<<',';first=false;std::cerr<<'"'<<std::hexfloat<<v<<'"';}std::cerr<<']';};
 std::cerr<<"{\"seq\":"<<std::defaultfloat<<sequence++<<",\"phase\":\""<<phase<<"\",\"index\":"<<index<<",\"parent\":";array(parent);std::cerr<<",\"de\":";array(de.v);std::cerr<<",\"candidate\":";array(candidate);std::cerr<<",\"residual\":";array(residual);std::cerr<<",\"jac\":[";if(jac){bool first=true;for(const auto&row:*jac){if(!first)std::cerr<<',';first=false;array(row);}}std::cerr<<"]}\n";
}
}
