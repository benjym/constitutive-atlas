#pragma once
#include <cmath>
namespace atlas_trace {
// Dimensionless scaled-residual/error criteria. Bounds limit per-call work;
// they are software limits, not constitutive admissibility conditions.
struct IntegrationSettings {
    double residual_tolerance=2e-10;
    double rate_tolerance=1e-6;
    int max_iterations=45;
    int max_depth=14;
    int max_substeps=20000;
    int max_backtracks=11;
};
inline bool valid_settings(const IntegrationSettings& s){
    return std::isfinite(s.residual_tolerance)&&s.residual_tolerance>0
        &&std::isfinite(s.rate_tolerance)&&s.rate_tolerance>0
        &&s.max_iterations>=1&&s.max_iterations<=1000
        &&s.max_depth>=0&&s.max_depth<=20
        &&s.max_substeps>=1&&s.max_substeps<=1000000
        &&s.max_backtracks>=0&&s.max_backtracks<=30;
}
}
