#include "atlas/tensor.hpp"
#include "atlas/numerics/normalized_determinant.hpp"
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define EXPORT
#endif
namespace {
std::string answer;
std::string bits(double x){std::ostringstream o;o<<std::hex<<std::setfill('0')<<std::setw(16)<<std::bit_cast<std::uint64_t>(x);return o.str();}
std::vector<double> csv(const std::string&s){std::vector<double>v;std::istringstream in(s);std::string x;while(std::getline(in,x,',')){char*end=nullptr;const double a=std::strtod(x.c_str(),&end);if(x.empty()||end!=x.c_str()+x.size())throw std::runtime_error("CSV");v.push_back(a);}return v;}
std::string quoted(const std::string&s){std::string out="\"";for(char c:s){if(c=='\\'||c=='"')out+='\\';out+=c;}return out+'"';}
}
extern "C" EXPORT const char* normalized_determinant_probe(const char*input){
 try{
  std::istringstream line(input?input:"");std::string id,values,seeds;std::getline(line,id,'\t');std::getline(line,values,'\t');std::getline(line,seeds,'\t');const auto v=csv(values),s=csv(seeds);if(v.size()!=6||s.size()!=6*38)throw std::runtime_error("shape");
  atlas::Sym<double>a;atlas::Sym<atlas::Jet>j;
  for(unsigned i=0;i<6;++i){a.v[i]=v[i];j.v[i].v=v[i];for(unsigned k=0;k<38;++k)j.v[i].d[k]=s[i*38+k];}
  double primal=-123.5;atlas::Jet jet(17.25);for(unsigned k=0;k<38;++k)jet.d[k]=-64.+double(k)/2.;const auto before=jet;
  const bool dok=atlas::normalized_determinant_accuracy::checked(a,primal),jok=atlas::normalized_determinant_accuracy::checked(j,jet);
  bool unchanged=bits(before.v)==bits(jet.v);for(unsigned k=0;k<38;++k)unchanged=unchanged&&bits(before.d[k])==bits(jet.d[k]);
  bool inputs_unchanged=true;for(unsigned i=0;i<6;++i){inputs_unchanged=inputs_unchanged&&bits(a.v[i])==bits(v[i])&&bits(j.v[i].v)==bits(v[i]);for(unsigned k=0;k<38;++k)inputs_unchanged=inputs_unchanged&&bits(j.v[i].d[k])==bits(s[i*38+k]);}
  std::ostringstream out;out<<"{\"id\":"<<quoted(id)<<",\"version\":"<<quoted(atlas::normalized_determinant_accuracy::version)<<",\"inputs_unchanged\":"<<(inputs_unchanged?"true":"false")<<",\"double_ok\":"<<(dok?"true":"false")<<",\"double_bits\":"<<quoted(bits(primal))<<",\"double_unchanged\":"<<(bits(primal)==bits(-123.5)?"true":"false")<<",\"jet_ok\":"<<(jok?"true":"false")<<",\"jet_unchanged\":"<<(unchanged?"true":"false")<<",\"jet_bits\":["<<quoted(bits(jet.v));for(double x:jet.d)out<<','<<quoted(bits(x));out<<"]}";answer=out.str();
 }catch(const std::exception&e){answer="{\"harness_error\":"+quoted(e.what())+"}";}
 return answer.c_str();
}
#ifndef __EMSCRIPTEN__
int main(){std::string line;while(std::getline(std::cin,line))std::cout<<normalized_determinant_probe(line.c_str())<<std::endl;}
#endif
