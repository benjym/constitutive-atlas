#pragma once
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
namespace atlas::cost_diagnostic {
enum Kind{jet_eval,value_eval,trace_jet,trace_value,spectral_jet,spectral_value,linear,admissible,path_error,integrate,seed,macro,count};
inline constexpr const char*names[]={"jet_eval","value_eval","trace_jet","trace_value","spectral_jet","spectral_value","linear","admissible","path_error","integrate","seed","macro"};
struct Measurement{std::uint64_t calls=0,nanoseconds=0;};
inline thread_local std::array<Measurement,count>measurements{};
using Clock=std::chrono::steady_clock;
inline thread_local auto started=Clock::now();
inline void start_request(){measurements={};started=Clock::now();}
struct Scope{Kind kind;Clock::time_point start;explicit Scope(Kind k):kind(k),start(Clock::now()){++measurements[k].calls;}~Scope(){measurements[kind].nanoseconds+=std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now()-start).count();}};
inline void bump(Kind k){++measurements[k].calls;}
inline void progress(int step,int iterations,int substeps,int rejected){
 std::cerr<<"{\"step\":"<<step<<",\"elapsed_ns\":"<<std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now()-started).count()<<",\"point_iterations\":"<<iterations<<",\"point_substeps\":"<<substeps<<",\"point_rejected\":"<<rejected<<",\"inclusive_costs\":{";
 for(int i=0;i<count;++i){if(i)std::cerr<<',';std::cerr<<'\"'<<names[i]<<"\":{\"calls\":"<<measurements[i].calls<<",\"ns\":"<<measurements[i].nanoseconds<<'}';}std::cerr<<"}}\n";
}
}
