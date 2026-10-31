#pragma once
#include "models.hpp"
#include "history.hpp"
#include "atlas/solver.hpp"
namespace context_study {
using namespace atlas;
template<class T> bool call(int slot,const Sym<T>& A,double threshold,bool initial,bool check_only,bool reset,bool scale,bool observe_scale,std::vector<T>&out){
bool atlas_eval_ok=true; const auto I=identity<T>(); switch(slot){
case 0: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::max_value, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 1: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::mid_value, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 2: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::min_value, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 3: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::max, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 4: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::mid, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 5: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::min, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 6: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::upper_sum, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 7: {
auto result=atlas::expression_or_mark(atlas::spectral_scalar_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::lower_sum, atlas_eval_ok), atlas_eval_ok);
out={result};
return atlas_eval_ok;
}
case 8: {
auto result=atlas::expression_or_mark(atlas::spectral_projector_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::projector_max, atlas_eval_ok), atlas_eval_ok);
out.assign(result.v.begin(),result.v.end());
return atlas_eval_ok;
}
case 9: {
auto result=atlas::expression_or_mark(atlas::spectral_projector_or_mark(atlas::expression_or_mark(A, atlas_eval_ok), atlas::spectral_candidate::Operation::projector_min, atlas_eval_ok), atlas_eval_ok);
out.assign(result.v.begin(),result.v.end());
return atlas_eval_ok;
}
case 10: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[10].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(10,z,z,Sym<T>{},p,tmp,false,0.,false,false);if(ok){
out={-tmp[7]};
}return ok;
}
case 11: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[9].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(9,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 12: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[12].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(12,z,z,Sym<T>{},p,tmp,false,0.,false,false);if(ok){
out={-tmp[7]};
}return ok;
}
case 13: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[11].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(11,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 14: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[14].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(14,z,z,Sym<T>{},p,tmp,false,0.,false,false);if(ok){
out={-tmp[7]};
}return ok;
}
case 15: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[13].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(13,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 16: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[22].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(22,z,z,Sym<T>{},p,tmp,false,0.,false,false);if(ok){
out={-tmp[7]};
}return ok;
}
case 17: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[21].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(21,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 18: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[8].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(8,z,z,Sym<T>{},p,tmp,false,0.,false,false);if(ok){
out={-tmp[7]};
}return ok;
}
case 19: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[7].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(7,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 20: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[15].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(15,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 21: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[16].parameters) p.push_back(param.value);
std::vector<T> tmp;bool ok=evaluate_model(16,z,z,Sym<T>{},p,tmp,false,0.,false,true);if(ok){
out=tmp;
}return ok;
}
case 22: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[6].parameters) p.push_back(param.value);
for(size_t j=0;j<p.size();++j)if(models()[6].parameters[j].name=="threshold"||models()[6].parameters[j].name=="shape")p[j]=threshold;
if(scale){const auto values=observe_scale?model_observable_scales(6,p):model_scales(6,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(6,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(6,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 23: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[20].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(20,p):model_scales(20,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(20,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(20,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 24: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[4].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(4,p):model_scales(4,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(4,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(4,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 25: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[3].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(3,p):model_scales(3,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(3,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(3,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 26: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[1].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(1,p):model_scales(1,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(1,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(1,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 27: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[2].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(2,p):model_scales(2,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(2,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(2,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 28: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[5].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(5,p):model_scales(5,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(5,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(5,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 29: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[0].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(0,p):model_scales(0,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(0,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(0,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 30: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[17].parameters) p.push_back(param.value);
for(size_t j=0;j<p.size();++j)if(models()[17].parameters[j].name=="threshold"||models()[17].parameters[j].name=="shape")p[j]=threshold;
if(scale){const auto values=observe_scale?model_observable_scales(17,p):model_scales(17,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(17,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(17,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 31: {
std::vector<T> z(7); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[18].parameters) p.push_back(param.value);
for(size_t j=0;j<p.size();++j)if(models()[18].parameters[j].name=="threshold"||models()[18].parameters[j].name=="shape")p[j]=threshold;
if(scale){const auto values=observe_scale?model_observable_scales(18,p):model_scales(18,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(18,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(18,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
case 32: {
std::vector<T> z(8); for(int k=0;k<6;++k) z[k]=A.v[k]; z[6]=T(.7);
std::vector<double> p; for(const auto&param:models()[19].parameters) p.push_back(param.value);
if(scale){const auto values=observe_scale?model_observable_scales(19,p):model_scales(19,p); out.clear(); bool ok=true;for(double v:values){ok=ok&&std::isfinite(v)&&v>0;out.push_back(T(v));}return ok;}
if(reset){std::vector<T> tmp;bool ok=prepare_model_increment(19,z,Sym<T>{},p,tmp);out.assign(tmp.begin(),tmp.begin()+6);return ok;}
std::vector<T> tmp;bool ok=evaluate_model(19,z,z,Sym<T>{},p,tmp,initial,0.,check_only,false); if(ok&&!check_only)out.assign(tmp.begin(),tmp.begin()+6);return ok;
}
default:return false;}}
}
