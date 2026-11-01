#pragma once
#include <vector>
#include <type_traits>
namespace atlas_trace {
struct DerivedObservation {double branch=0,vmax=0,vmid=0,vmin=0,trace_trial=0,width=0;bool jets=false,check_initial=false;std::vector<double> trial,loading;};
inline bool trace_enabled=false;
inline std::vector<DerivedObservation> derived_observations;
}
