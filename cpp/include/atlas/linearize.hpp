#pragma once
#include "atlas/solver.hpp"

namespace atlas {
// Derivative of the converged discrete update, with its accepted partition and
// expression/reset branches fixed. Rows follow generated state field ordering;
// columns are the six total Mandel strain-increment components.
struct LinearizedAdvance {
    Advance advance;
    bool tangent_ok=false;
    bool reset_guard_at_zero=false;
    std::vector<State> state_tangent;
    std::string message;
};

inline LinearizedAdvance linearize_update(int model,const State& parent,const Sym<double>& increment,const State& parameters){
    LinearizedAdvance result;
    result.advance=integrate(model,parent,increment,parameters);
    if(!result.advance.ok){result.message="material update failed; no tangent";return result;}
    const auto scales=model_scales(model,parameters);const int n=int(parent.size());
    constexpr int controls=max_state;
    std::vector<Jet> previous(n);Sym<Jet> total;
    for(int i=0;i<n;++i)previous[i]=Jet(parent[i]);
    for(int j=0;j<6;++j){total.v[j]=Jet(increment.v[j]);total.v[j].d[controls+j]=1.;}
    std::vector<Jet> prepared;
    if(!prepare_model_increment(model,previous,total,parameters,prepared,&result.reset_guard_at_zero)){
        result.message="AD preparation failed";return result;
    }
    previous=prepared;double covered=0.;
    for(double fraction:result.advance.diagnostics.increment_fractions){
        if(!std::isfinite(fraction)||fraction<=0){result.message="invalid accepted partition";return result;}
        covered+=fraction;const auto de=Jet(fraction)*total;
        if(models().at(model).rate){
            std::vector<Jet> k1,k2,mid=previous;
            if(!evaluate_model(model,previous,previous,de,parameters,k1)){result.message="rate replay failed";return result;}
            for(int i=0;i<n;++i)mid[i]=previous[i]+Jet(.5)*k1[i];
            if(!evaluate_model(model,mid,previous,de,parameters,k2)){result.message="midpoint replay failed";return result;}
            for(int i=0;i<n;++i)previous[i]=previous[i]+k2[i];
        }else{
            State old(n),endpoint;for(int i=0;i<n;++i)old[i]=previous[i].v;
            Sym<double> step;for(int j=0;j<6;++j)step.v[j]=de.v[j].v;
            Diagnostics replay;
            if(!implicit_step(model,old,step,parameters,endpoint,replay)){
                result.message="accepted residual step could not be replayed";return result;
            }
            std::vector<Jet> unknown(n),residual;
            for(int i=0;i<n;++i){unknown[i]=Jet(endpoint[i]);unknown[i].d[i]=scales[i];}
            if(!evaluate_model(model,unknown,previous,de,parameters,residual)){
                result.message="AD residual evaluation failed";return result;
            }
            std::vector<State> jacobian(n,State(n));
            for(int i=0;i<n;++i)for(int k=0;k<n;++k)jacobian[i][k]=residual[i].d[k]/scales[i];
            std::vector<Jet> next(n);for(int i=0;i<n;++i)next[i]=Jet(endpoint[i]);
            for(int j=0;j<6;++j){
                State rhs(n),solution;
                for(int i=0;i<n;++i)rhs[i]=-residual[i].d[controls+j]/scales[i];
                if(!finite(rhs)||!solve_linear(jacobian,rhs,solution)){
                    result.message="singular or nonfinite residual linearization";return result;
                }
                for(int i=0;i<n;++i)next[i].d[controls+j]=solution[i]*scales[i];
            }
            previous=next;
        }
    }
    if(std::abs(covered-1.)>1e-12){result.message="accepted partition does not cover the increment";return result;}
    result.state_tangent.assign(n,State(6));
    for(int i=0;i<n;++i){
        if(!std::isfinite(previous[i].v)||std::abs(previous[i].v-result.advance.state[i])/scales[i]>1e-9){
            result.state_tangent.clear();result.message="AD replay endpoint differs from accepted update";return result;
        }
        for(int j=0;j<6;++j){
            double v=previous[i].d[controls+j];
            if(!std::isfinite(v)){result.state_tangent.clear();result.message="nonfinite update tangent";return result;}
            result.state_tangent[i][j]=v;
        }
    }
    result.tangent_ok=true;return result;
}
}
