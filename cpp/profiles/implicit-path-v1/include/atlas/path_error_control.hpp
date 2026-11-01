#pragma once
#include "atlas/checked_spectral.hpp"

namespace atlas {
// Opt-in estimator for differential-law realizations expressed as residuals.
// This estimates path error; it is not an event certificate for arbitrary laws.
inline bool path_metric_layout(int model,const IntegrationSettings& settings){
    if(!settings.positive_stress_metric)return true;
    const auto& m=models().at(model);const auto& fields=m.fields;
    return !fields.empty()&&fields.front().name=="sigma"&&fields.front().offset==0&&fields.front().size==6
        &&!fields.front().transient&&(m.stress_scope==StressScope::total||m.stress_scope==StressScope::effective);
}
inline bool implicit_path_error(int model,const State& parent,const State& full,
    const State& half,const State& two,const State& p,const IntegrationSettings& settings,double& error){
    const auto scales=model_scales(model,p);error=0.;
    if(full.size()!=parent.size()||half.size()!=parent.size()||two.size()!=parent.size())return false;
    if(settings.positive_stress_metric){
        const auto& fields=models().at(model).fields;
        if(fields.empty()||fields.front().offset!=0||fields.front().size!=6||parent.size()<6)return false;
        double pressure=std::numeric_limits<double>::infinity();
        for(const State* state:{&parent,&full,&half,&two}){
            Sym<double> stress;for(int i=0;i<6;++i)stress.v[i]=(*state)[i];
            bool ok=true;const double least=spectral_scalar_or_mark(stress,spectral_candidate::Operation::min_value,ok);
            if(!ok||!std::isfinite(least)||!(least>0.))return false;
            pressure=std::min(pressure,least);
        }
        double defect=0.;for(int i=0;i<6;++i)defect=std::hypot(defect,full[i]-two[i]);
        error=defect/pressure; // Mandel Frobenius norm: invariant under rotation.
        for(size_t i=6;i<parent.size();++i)error=std::max(error,std::abs(full[i]-two[i])/scales[i]);
    }else{
        for(size_t i=0;i<parent.size();++i)error=std::max(error,std::abs(full[i]-two[i])/scales[i]);
    }
    return std::isfinite(error);
}
} // namespace atlas
