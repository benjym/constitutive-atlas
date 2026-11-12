#pragma once
#include "advance.hpp"

namespace atlas {
inline Advance weighted_profile_advance(int model,const State& parent,const Sym<double>& load,
                                        const State& parameters,const IntegrationSettings& settings) {
    Advance unavailable;unavailable.state=parent;unavailable.settings=settings;
    unavailable.message="model lacks an explicit weighted-history profile binding";
    if(model<0||model>=int(models().size()))return unavailable;
    const auto& m=models()[model];
    // This partition is compiled from the one independently selected model.
    // Resolve the names explicitly; the numerical callback itself is generic.
    if(m.id!="clay2014-trace-calibrated-igs-fixed-plane-v1"||parameters.size()!=m.parameters.size())
        return unavailable;
    weighted_history_v1::Binding bind{13,13,13};
    for(const auto& f:m.fields){
        if(f.transient||f.multiplier)continue;
        if(f.name=="sigma"&&f.size==6)bind.stress=f.offset;
        if(f.name=="e"&&f.size==1)bind.void_ratio=f.offset;
        if(f.name=="H"&&f.size==6)bind.memory=f.offset;
    }
    bool margin=false;
    for(size_t i=0;i<m.parameters.size();++i){
        const auto& name=m.parameters[i].name;
        if(name=="R")bind.R=parameters[i];
        if(name=="beta_r")bind.beta=parameters[i];
        if(name=="stress_interior_margin"){bind.stress_margin=parameters[i];margin=true;}
    }
    return margin?weighted_history_v1::advance(model,parent,load,parameters,settings,bind):unavailable;
}
}
