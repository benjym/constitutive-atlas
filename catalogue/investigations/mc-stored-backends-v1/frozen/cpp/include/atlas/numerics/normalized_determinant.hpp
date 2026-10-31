#pragma once
// Exact homogeneous determinant ratio on original stored Mandel components.
// Reuses the immutable determinant core's exact dyadic/radical arithmetic.
#include "atlas/numerics/determinant.hpp"
namespace atlas::normalized_determinant_accuracy {
namespace det=atlas::determinant_accuracy;
using det::Dyadic;using det::Radical;
inline constexpr const char* version="mandel-normalized-determinant-exact-quotient-rne-v1-candidate";
struct Quotient {Radical numerator;Dyadic denominator;}; // denominator strictly positive
inline Quotient quotient(Radical n,Dyadic d){
 if(d.sign<0){n.a=-n.a;n.b=-n.b;d=-d;}return {n,d};
}
inline int compare_to(const Quotient&x,const Dyadic&boundary){
 return det::radical_sign({x.numerator.a-boundary*x.denominator,x.numerator.b});
}
inline bool contains_nearest(const Quotient&x,std::uint64_t candidate){
 if(candidate>det::max_finite_bits)return false;
 const bool even=(candidate&1)==0;
 if(candidate){const int lower=compare_to(x,det::midpoint(candidate-1,candidate));if(lower<0||(lower==0&&!even))return false;}
 const int upper=compare_to(x,det::midpoint(candidate,candidate+1));return upper<0||(upper==0&&even);
}
inline bool rounded(const Quotient&input,double&out){
 if(input.denominator.sign<=0)return false;
 const int sign=det::radical_sign(input.numerator);if(!sign){out=0.;return true;}
 Quotient x=input;if(sign<0){x.numerator.a=-x.numerator.a;x.numerator.b=-x.numerator.b;}
 if(compare_to(x,det::midpoint(det::max_finite_bits,det::max_finite_bits+1))>=0)return false;
 const auto&n=x.numerator;
 const int ns=std::max(n.a.sign?det::bit_length(n.a.magnitude)+n.a.exponent:-10000,n.b.sign?det::bit_length(n.b.magnitude)+n.b.exponent:-10000);
 const int ds=det::bit_length(x.denominator.magnitude)+x.denominator.exponent;
 const double guide=std::ldexp((n.a.guide(ns)+std::sqrt(2.)*n.b.guide(ns))/x.denominator.guide(ds),ns-ds);
 const auto bits=std::bit_cast<std::uint64_t>(guide);
 if(guide>=0&&std::isfinite(guide)){
  for(int delta=-2;delta<=2;++delta){
   if(delta<0&&bits<std::uint64_t(-delta))continue;
   const auto candidate=delta<0?bits-std::uint64_t(-delta):bits+std::uint64_t(delta);
   if(contains_nearest(x,candidate)){out=candidate?det::binary(candidate|(sign<0?1ULL<<63:0)):0.;return true;}
  }
 }
 std::uint64_t lo=0,hi=det::max_finite_bits;
 while(lo<hi){const auto middle=lo+(hi-lo)/2+1;if(compare_to(x,Dyadic::from(det::binary(middle)))>=0)lo=middle;else hi=middle-1;}
 const int relation=compare_to(x,det::midpoint(lo,lo+1));const auto chosen=relation<0||(relation==0&&(lo&1)==0)?lo:lo+1;
 out=chosen?det::binary(chosen|(sign<0?1ULL<<63:0)):0.;return true;
}
inline Quotient primal(const std::array<Dyadic,6>&x,const Dyadic&trace){return quotient(det::polynomial(x),trace*trace*trace);}
// Strict structural interface and transactional assignment match determinant.
template<class Tensor,class Result>bool checked(const Tensor&tensor,Result&out){
 static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(tensor.v)>> ==6);
 static_assert(sizeof(double)==8&&std::numeric_limits<double>::is_iec559&&std::numeric_limits<double>::digits==53);
 Result candidate{};std::array<Dyadic,6>x;
 if constexpr(std::is_same_v<Result,double>){
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0])>,double>);
  for(unsigned i=0;i<6;++i){if(!std::isfinite(tensor.v[i]))return false;x[i]=Dyadic::from(tensor.v[i]);}
  const auto trace=x[0]+x[1]+x[2];if(!trace.sign)return false;
  if(!rounded(primal(x,trace),candidate))return false;
 }else{
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0].v)>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0].d[0])>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(candidate.v)>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(candidate.d[0])>,double>);
  static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(candidate.d)>> ==38);
  static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(tensor.v[0].d)>> ==38);
  for(unsigned i=0;i<6;++i){if(!std::isfinite(tensor.v[i].v))return false;for(double seed:tensor.v[i].d)if(!std::isfinite(seed))return false;x[i]=Dyadic::from(tensor.v[i].v);}
  const auto trace=x[0]+x[1]+x[2];if(!trace.sign)return false;
  const auto poly=det::polynomial(x);const auto cof=det::gradient(x);
  const auto t2=trace*trace,t4=t2*t2;
  if(!rounded(quotient(poly,t2*trace),candidate.v))return false;
  for(unsigned j=0;j<38;++j){
   Radical directional{};Dyadic dtrace;
   for(unsigned i=0;i<6;++i){const auto seed=Dyadic::from(tensor.v[i].d[j]);directional=directional+cof[i]*seed;if(i<3)dtrace=dtrace+seed;}
   const auto first=directional*trace,second=poly*(Dyadic::from(3.)*dtrace);
   const Radical numerator{first.a-second.a,first.b-second.b};
   if(!rounded(quotient(numerator,t4),candidate.d[j]))return false;
  }
 }
 out=candidate;return true;
}
} // namespace atlas::normalized_determinant_accuracy
