// Generated declarative path ODE evaluator; no model-specific runtime.
#pragma once
#include "atlas/expm.hpp"
#include "atlas/checked_trace.hpp"
#include "atlas/checked_expression.hpp"
namespace atlas { namespace path_generated {
inline bool evaluate(int model,const std::vector<double>& z,const std::vector<double>& params,const std::vector<double>& inputs,std::vector<double>& rates,std::vector<double>& observables,std::vector<double>& scales,bool initial=false) { using T=double; bool atlas_eval_ok=true; const auto I=identity<T>(); std::vector<double> rr,oo,ss; switch(model) {
case 0: {
if(z.size()!=4 || params.size()!=6 || inputs.size()!=5) return false;
for(double x:z) if(!std::isfinite(x)) return false;
for(double x:inputs) if(!std::isfinite(x)) return false;
const T M=params[0];
if(!std::isfinite(M) || M<0.8 || M>1.8) return false;
const T N=params[1];
if(!std::isfinite(N) || N<0.0 || N>0.39) return false;
const T h=params[2];
if(!std::isfinite(h) || h<10.0 || h>500.0) return false;
const T lam=params[3];
if(!std::isfinite(lam) || lam<0.005 || lam>0.04) return false;
const T Gamma=params[4];
if(!std::isfinite(Gamma) || Gamma<0.5 || Gamma>1.5) return false;
const T pref=params[5];
if(!std::isfinite(pref) || pref<1000.0 || pref>1000.0) return false;
const T path_coordinate=inputs[0];
const T C=inputs[1];
const T Cs=inputs[2];
const T K=inputs[3];
const T Ks=inputs[4];
const T eta=z[0];
const T e=z[1];
const T ev=z[2];
const T eq=z[3];
const auto B=atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark(K, atlas_eval_ok) * atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(B)) return false;
const auto p=atlas::expression_or_mark((atlas::expression_or_mark(C, atlas_eval_ok) / atlas::expression_or_mark(B, atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(p)) return false;
const auto q=atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) * atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(q)) return false;
const auto r=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok) ? atlas::expression_or_mark(apow(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) * atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) - atlas::expression_or_mark(T(1.0), atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) : atlas::expression_or_mark(aexp(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(eta, atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok) - atlas::expression_or_mark(T(1.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(r)) return false;
const auto pi=atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) * atlas::expression_or_mark(r, atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(pi)) return false;
const auto psi_i=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(e, atlas_eval_ok) - atlas::expression_or_mark(Gamma, atlas_eval_ok)), atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark(lam, atlas_eval_ok) * atlas::expression_or_mark(alog(atlas::expression_or_mark((atlas::expression_or_mark(pi, atlas_eval_ok) / atlas::expression_or_mark(pref, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(psi_i)) return false;
const auto rL=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok) ? atlas::expression_or_mark(apow(atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(3.5), atlas_eval_ok) * atlas::expression_or_mark(psi_i, atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) - atlas::expression_or_mark(T(1.0), atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) : atlas::expression_or_mark(aexp(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((-atlas::expression_or_mark(T(3.5), atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(psi_i, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(rL)) return false;
const auto D=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(M, atlas_eval_ok) - atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(D)) return false;
const auto Y=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok) ? atlas::expression_or_mark(apow(atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) / atlas::expression_or_mark(pi, atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) / atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) : atlas::expression_or_mark(T(1.0), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(Y)) return false;
const auto eta_rate=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(M, atlas_eval_ok) * atlas::expression_or_mark(Y, atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(B, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark((atlas::expression_or_mark(B, atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(K, atlas_eval_ok) * atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(Y, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(h, atlas_eval_ok) * atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(rL, atlas_eval_ok) / atlas::expression_or_mark(r, atlas_eval_ok)), atlas_eval_ok) - atlas::expression_or_mark(T(1.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark(Cs, atlas_eval_ok) / atlas::expression_or_mark(C, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(Ks, atlas_eval_ok) * atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(B, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
if(!atlas_eval_ok || !atlas::finite_value(eta_rate)) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(M, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(h, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(lam, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) >= atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) <= atlas::expression_or_mark(T(0.39), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(C, atlas_eval_ok) > atlas::expression_or_mark((atlas::expression_or_mark(T(0.0), atlas_eval_ok) * atlas::expression_or_mark(C, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(B, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) > atlas::expression_or_mark((atlas::expression_or_mark(T(0.0), atlas_eval_ok) * atlas::expression_or_mark(p, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(e, atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark(eta, atlas_eval_ok) >= atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(N, atlas_eval_ok) * atlas::expression_or_mark(eta, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(3.5), atlas_eval_ok) * atlas::expression_or_mark(psi_i, atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(N, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
if(!(atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(B, atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(K, atlas_eval_ok) * atlas::expression_or_mark(M, atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(Y, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) > atlas::expression_or_mark(T(0.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
rr.resize(4);
rr[0]=atlas::expression_or_mark(eta_rate, atlas_eval_ok);
rr[1]=atlas::expression_or_mark((atlas::expression_or_mark((-atlas::expression_or_mark((atlas::expression_or_mark(T(1.0), atlas_eval_ok) + atlas::expression_or_mark(e, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(D, atlas_eval_ok)), atlas_eval_ok);
rr[2]=atlas::expression_or_mark(D, atlas_eval_ok);
rr[3]=atlas::expression_or_mark(T(1.0), atlas_eval_ok);
oo.resize(13);
put_tensor(oo,0,atlas::expression_or_mark(make_sym(atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(T(2.0), atlas_eval_ok) * atlas::expression_or_mark(q, atlas_eval_ok)), atlas_eval_ok) / atlas::expression_or_mark(T(3.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark(q, atlas_eval_ok) / atlas::expression_or_mark(T(3.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(p, atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark(q, atlas_eval_ok) / atlas::expression_or_mark(T(3.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(T(0.0), atlas_eval_ok) * atlas::expression_or_mark(p, atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(T(0.0), atlas_eval_ok) * atlas::expression_or_mark(p, atlas_eval_ok)), atlas_eval_ok), atlas::expression_or_mark((atlas::expression_or_mark(T(0.0), atlas_eval_ok) * atlas::expression_or_mark(p, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok));
if(!axisymmetric_x(tensor_from(oo,0))) return false;
oo[6]=atlas::expression_or_mark(p, atlas_eval_ok);
oo[7]=atlas::expression_or_mark(q, atlas_eval_ok);
oo[8]=atlas::expression_or_mark(pi, atlas_eval_ok);
oo[9]=atlas::expression_or_mark(psi_i, atlas_eval_ok);
oo[10]=atlas::expression_or_mark(D, atlas_eval_ok);
oo[11]=atlas::expression_or_mark((atlas::expression_or_mark(eq, atlas_eval_ok) + atlas::expression_or_mark((atlas::expression_or_mark(ev, atlas_eval_ok) / atlas::expression_or_mark(T(3.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
oo[12]=atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(ev, atlas_eval_ok) / atlas::expression_or_mark(T(3.0), atlas_eval_ok)), atlas_eval_ok) - atlas::expression_or_mark((atlas::expression_or_mark(eq, atlas_eval_ok) / atlas::expression_or_mark(T(2.0), atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok);
ss={atlas::expression_or_mark(T(1.0), atlas_eval_ok),atlas::expression_or_mark(T(1.0), atlas_eval_ok),atlas::expression_or_mark(T(1.0), atlas_eval_ok),atlas::expression_or_mark(T(1.0), atlas_eval_ok)};
if(!atlas_eval_ok) return false;
for(double x:rr) if(!std::isfinite(x)) return false;
for(double x:oo) if(!std::isfinite(x)) return false;
for(double x:ss) if(!std::isfinite(x) || x<=0) return false;
rates=std::move(rr);observables=std::move(oo);scales=std::move(ss);return true;
}
case 1: {
if(z.size()!=7 || params.size()!=1 || inputs.size()!=4) return false;
for(double x:z) if(!std::isfinite(x)) return false;
for(double x:inputs) if(!std::isfinite(x)) return false;
const T pref=params[0];
if(!std::isfinite(pref) || pref<1.0 || pref>100000.0) return false;
const T path_coordinate=inputs[0];
const T u=inputs[1];
const T du=inputs[2];
const T unused=inputs[3];
const T vscalar=z[0];
const auto A=tensor_from(z,1);
if(!(atlas::expression_or_mark((atlas::expression_or_mark(vscalar, atlas_eval_ok) < atlas::expression_or_mark(T(100.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
rr.resize(7);
rr[0]=atlas::expression_or_mark(vscalar, atlas_eval_ok);
put_tensor(rr,1,atlas::expression_or_mark(A, atlas_eval_ok));
oo.resize(6);
put_tensor(oo,0,atlas::expression_or_mark(A, atlas_eval_ok));
ss={atlas::expression_or_mark(T(1.0), atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok)};
if(!atlas_eval_ok) return false;
for(double x:rr) if(!std::isfinite(x)) return false;
for(double x:oo) if(!std::isfinite(x)) return false;
for(double x:ss) if(!std::isfinite(x) || x<=0) return false;
rates=std::move(rr);observables=std::move(oo);scales=std::move(ss);return true;
}
case 2: {
if(z.size()!=7 || params.size()!=1 || inputs.size()!=4) return false;
for(double x:z) if(!std::isfinite(x)) return false;
for(double x:inputs) if(!std::isfinite(x)) return false;
const T pref=params[0];
if(!std::isfinite(pref) || pref<1.0 || pref>100000.0) return false;
const T path_coordinate=inputs[0];
const T u=inputs[1];
const T du=inputs[2];
const T unused=inputs[3];
const T vscalar=z[0];
const auto A=tensor_from(z,1);
if(!(atlas::expression_or_mark((atlas::expression_or_mark(vscalar, atlas_eval_ok) < atlas::expression_or_mark(T(100.0), atlas_eval_ok)), atlas_eval_ok)) || !atlas_eval_ok) return false;
rr.resize(7);
rr[0]=atlas::expression_or_mark((atlas::expression_or_mark(u, atlas_eval_ok) + atlas::expression_or_mark(du, atlas_eval_ok)), atlas_eval_ok);
put_tensor(rr,1,atlas::expression_or_mark((atlas::expression_or_mark((atlas::expression_or_mark(pref, atlas_eval_ok) * atlas::expression_or_mark((atlas::expression_or_mark(u, atlas_eval_ok) + atlas::expression_or_mark(du, atlas_eval_ok)), atlas_eval_ok)), atlas_eval_ok) * atlas::expression_or_mark(I, atlas_eval_ok)), atlas_eval_ok));
oo.resize(6);
put_tensor(oo,0,atlas::expression_or_mark(A, atlas_eval_ok));
ss={atlas::expression_or_mark(T(1.0), atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok),atlas::expression_or_mark(pref, atlas_eval_ok)};
if(!atlas_eval_ok) return false;
for(double x:rr) if(!std::isfinite(x)) return false;
for(double x:oo) if(!std::isfinite(x)) return false;
for(double x:ss) if(!std::isfinite(x) || x<=0) return false;
rates=std::move(rr);observables=std::move(oo);scales=std::move(ss);return true;
}
default:return false;
}}
}}
