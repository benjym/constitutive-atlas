#pragma once
namespace atlas {
// A seed changes only the Newton iterate. History/loading stay in the evaluator closure.
// Choosing a smaller residual does not certify a common root for multiroot laws.
template<class Reset,class Admissible,class Evaluate,class Override>
inline bool choose_implicit_seed(const State&cold,const State*seed,const State&scales,
    Reset reset,Admissible admissible,Evaluate evaluate,Override override_residual,
    State&chosen,int&value_evaluations){
    if(!seed||cold.empty()||seed->size()!=cold.size()||scales.size()!=cold.size())return false;
    for(double scale:scales)if(!std::isfinite(scale)||!(scale>0.))return false;
    State candidate=*seed;reset(candidate);
    if(!finite(candidate)||!admissible(candidate))return false;
    State reference_residual,candidate_residual;
    ++value_evaluations;
    if(!evaluate(cold,reference_residual)||reference_residual.size()!=cold.size()||!finite(reference_residual))return false;
    override_residual(cold,reference_residual);
    ++value_evaluations;
    if(!evaluate(candidate,candidate_residual)||candidate_residual.size()!=cold.size()||!finite(candidate_residual))return false;
    override_residual(candidate,candidate_residual);
    if(!finite(reference_residual)||!finite(candidate_residual))return false;
    if(!(scaled_norm(candidate_residual,scales)<scaled_norm(reference_residual,scales)))return false;
    chosen=std::move(candidate);return true;
}
} // namespace atlas
