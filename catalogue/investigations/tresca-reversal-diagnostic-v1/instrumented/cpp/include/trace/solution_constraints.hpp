#pragma once
#include <vector>
namespace atlas_trace {
// Older generated catalogues intentionally have no solution_check member.
// The dependent requires expression preserves their source and behavior.
template<class Model> bool checked_solution_state(const Model& model,const std::vector<double>& z,const std::vector<double>& p) {
    if constexpr(requires { model.solution_check; })return !model.solution_check || model.solution_check(z,p);
    else return true;
}
} // namespace atlas_trace
