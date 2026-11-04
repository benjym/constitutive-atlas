#pragma once
// Exact dyadic/radical arithmetic for a 3D orthonormal Mandel determinant.
// The only floating operations guide a candidate; exact integer comparisons
// certify its rounding interval. No FMA, long double or libm accuracy assumed.
#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <limits>
#include <tuple>
#include <type_traits>
#include <vector>
#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__)
#error "Exact determinant requires finite-input checks without fast-math"
#endif
namespace atlas::determinant_accuracy {
inline constexpr const char* version="mandel-determinant-exact-radical-rne-v1-candidate";
using Big=std::vector<std::uint32_t>;
inline void trim(Big& a){while(!a.empty()&&a.back()==0)a.pop_back();}
inline int compare(const Big&a,const Big&b){
 if(a.size()!=b.size())return a.size()>b.size()?1:-1;
 for(size_t i=a.size();i-->0;)if(a[i]!=b[i])return a[i]>b[i]?1:-1;
 return 0;
}
inline Big add(const Big&a,const Big&b){
 Big c(std::max(a.size(),b.size())+1);std::uint64_t carry=0;
 for(size_t i=0;i+1<c.size();++i){const auto t=(i<a.size()?std::uint64_t(a[i]):0)+(i<b.size()?std::uint64_t(b[i]):0)+carry;c[i]=std::uint32_t(t);carry=t>>32;}
 c.back()=std::uint32_t(carry);trim(c);return c;
}
inline Big subtract(const Big&a,const Big&b){ // a>=b
 Big c(a.size());std::uint64_t borrow=0;
 for(size_t i=0;i<a.size();++i){const auto t=(i<b.size()?std::uint64_t(b[i]):0)+borrow;borrow=std::uint64_t(a[i])<t;c[i]=std::uint32_t(std::uint64_t(a[i])-t);}
 trim(c);return c;
}
inline Big shift(const Big&a,unsigned n){
 if(a.empty())return {};
 const unsigned whole=n/32,rest=n%32;Big c(a.size()+whole+(rest?1:0));
 for(size_t i=0;i<a.size();++i){c[i+whole]|=a[i]<<rest;if(rest)c[i+whole+1]|=a[i]>>(32-rest);}
 trim(c);return c;
}
inline Big multiply(const Big&a,const Big&b){
 if(a.empty()||b.empty())return {};
 Big c(a.size()+b.size());
 for(size_t i=0;i<a.size();++i){std::uint64_t carry=0;
  for(size_t j=0;j<b.size();++j){const auto t=std::uint64_t(a[i])*b[j]+c[i+j]+carry;c[i+j]=std::uint32_t(t);carry=t>>32;}
  c[i+b.size()]=std::uint32_t(carry);
 }
 trim(c);return c;
}
inline int bit_length(const Big&a){return a.empty()?0:int((a.size()-1)*32+32-std::countl_zero(a.back()));}
struct Dyadic {
 int sign=0,exponent=0;Big magnitude;
 void normalize(){
  trim(magnitude);if(magnitude.empty()){sign=0;exponent=0;return;}
  size_t words=0;while(magnitude[words]==0)++words;
  if(words){magnitude.erase(magnitude.begin(),magnitude.begin()+words);exponent+=int(words*32);}
  const unsigned n=std::countr_zero(magnitude[0]);
  if(n){for(size_t i=0;i<magnitude.size();++i)magnitude[i]=(magnitude[i]>>n)|(i+1<magnitude.size()?magnitude[i+1]<<(32-n):0);exponent+=int(n);trim(magnitude);}
 }
 static Dyadic power(int n){Dyadic a;a.sign=1;a.exponent=n;a.magnitude={1};return a;}
 static Dyadic from(double x){
  const auto bits=std::bit_cast<std::uint64_t>(x);const unsigned e=unsigned((bits>>52)&2047);
  const std::uint64_t sig=(bits&((std::uint64_t(1)<<52)-1))|(e?std::uint64_t(1)<<52:0);
  Dyadic a;a.sign=(bits>>63)?-1:1;a.exponent=e?int(e)-1075:-1074;a.magnitude={std::uint32_t(sig),std::uint32_t(sig>>32)};a.normalize();return a;
 }
 double guide(int scale)const{
  if(!sign)return 0.;const int length=bit_length(magnitude),keep=std::min(53,length);std::uint64_t high=0;
  for(int i=0;i<keep;++i){const unsigned bit=unsigned(length-1-i);high=(high<<1)|((magnitude[bit/32]>>(bit%32))&1);}
  return std::ldexp(sign*double(high),exponent+length-keep-scale);
 }
};
inline Dyadic operator-(Dyadic a){a.sign=-a.sign;return a;}
inline Dyadic operator+(const Dyadic&a,const Dyadic&b){
 if(!a.sign)return b;if(!b.sign)return a;
 Dyadic c;c.exponent=std::min(a.exponent,b.exponent);const auto x=shift(a.magnitude,unsigned(a.exponent-c.exponent)),y=shift(b.magnitude,unsigned(b.exponent-c.exponent));
 if(a.sign==b.sign){c.sign=a.sign;c.magnitude=add(x,y);}
 else {const int order=compare(x,y);c.sign=order>0?a.sign:b.sign;c.magnitude=order>=0?subtract(x,y):subtract(y,x);}
 c.normalize();return c;
}
inline Dyadic operator-(const Dyadic&a,const Dyadic&b){return a+(-b);}
inline Dyadic operator*(const Dyadic&a,const Dyadic&b){Dyadic c;c.sign=a.sign*b.sign;c.exponent=a.exponent+b.exponent;c.magnitude=multiply(a.magnitude,b.magnitude);c.normalize();return c;}
inline Dyadic half(Dyadic a){if(a.sign)--a.exponent;return a;}
inline int compare_positive(const Dyadic&a,const Dyadic&b){
 if(!a.sign||!b.sign)return a.sign?1:(b.sign?-1:0);
 const int x=bit_length(a.magnitude)+a.exponent,y=bit_length(b.magnitude)+b.exponent;
 if(x!=y)return x>y?1:-1;
 const int e=std::min(a.exponent,b.exponent);return compare(shift(a.magnitude,unsigned(a.exponent-e)),shift(b.magnitude,unsigned(b.exponent-e)));
}
struct Radical {Dyadic a,b;}; // a+b*sqrt(2), both exact dyadics
inline Radical operator+(const Radical&x,const Radical&y){return {x.a+y.a,x.b+y.b};}
inline Radical operator*(const Radical&x,const Dyadic&y){return {x.a*y,x.b*y};}
inline int radical_sign(const Radical&x){
 if(!x.a.sign)return x.b.sign;if(!x.b.sign)return x.a.sign;
 if(x.a.sign==x.b.sign)return x.a.sign;
 auto b2=x.b*x.b;++b2.exponent;return x.a.sign*compare_positive(x.a*x.a,b2);
}
inline int compare_to(const Radical&x,const Dyadic&y){return radical_sign({x.a-y,x.b});}
inline constexpr std::uint64_t max_finite_bits=0x7fefffffffffffffULL;
inline double binary(std::uint64_t bits){return std::bit_cast<double>(bits);}
inline Dyadic midpoint(std::uint64_t low,std::uint64_t high){return half(Dyadic::from(binary(low))+(high>max_finite_bits?Dyadic::power(1024):Dyadic::from(binary(high))));}
inline bool contains_nearest(const Radical&x,std::uint64_t candidate){
 if(candidate>max_finite_bits)return false;
 const bool even=(candidate&1)==0;
 if(candidate){const int lower=compare_to(x,midpoint(candidate-1,candidate));if(lower<0||(lower==0&&!even))return false;}
 const int upper=compare_to(x,midpoint(candidate,candidate+1));return upper<0||(upper==0&&even);
}
inline bool rounded(const Radical&input,double&out){
 const int sign=radical_sign(input);if(!sign){out=0.;return true;}
 Radical x=input;if(sign<0){x.a=-x.a;x.b=-x.b;}
 // Exact overflow threshold; its upper neighbour is the conceptual 2^1024.
 if(compare_to(x,midpoint(max_finite_bits,max_finite_bits+1))>=0)return false;
 const int scale=std::max(x.a.sign?bit_length(x.a.magnitude)+x.a.exponent:-10000,x.b.sign?bit_length(x.b.magnitude)+x.b.exponent:-10000);
 const double guide=std::ldexp(x.a.guide(scale)+std::sqrt(2.)*x.b.guide(scale),scale);
 const auto bits=std::bit_cast<std::uint64_t>(guide);
 if(guide>=0&&std::isfinite(guide)){
  for(int delta=-2;delta<=2;++delta){
   if(delta<0&&bits<std::uint64_t(-delta))continue;
   const auto candidate=delta<0?bits-std::uint64_t(-delta):bits+std::uint64_t(delta);
   if(contains_nearest(x,candidate)){out=candidate?binary(candidate|(sign<0?1ULL<<63:0)):0.;return true;}
  }
 }
 std::uint64_t lo=0,hi=max_finite_bits;
 while(lo<hi){const auto middle=lo+(hi-lo)/2+1;if(compare_to(x,Dyadic::from(binary(middle)))>=0)lo=middle;else hi=middle-1;}
 const int relation=compare_to(x,midpoint(lo,lo+1));const auto chosen=relation<0||(relation==0&&(lo&1)==0)?lo:lo+1;
 out=chosen?binary(chosen|(sign<0?1ULL<<63:0)):0.;return true;
}
inline Radical polynomial(const std::array<Dyadic,6>&x){
 return {x[0]*x[1]*x[2]-half(x[0]*x[4]*x[4]+x[1]*x[5]*x[5]+x[2]*x[3]*x[3]),half(x[3]*x[4]*x[5])};
}
inline std::array<Radical,6> gradient(const std::array<Dyadic,6>&x){
 return {{{x[1]*x[2]-half(x[4]*x[4]),{}},{x[0]*x[2]-half(x[5]*x[5]),{}},{x[0]*x[1]-half(x[3]*x[3]),{}},
          {-x[2]*x[3],half(x[4]*x[5])},{-x[0]*x[4],half(x[3]*x[5])},{-x[1]*x[5],half(x[3]*x[4])}}};
}
// Structural interface avoids circular dependencies. No output writes on failure.
template<class Tensor,class Result>bool checked(const Tensor&tensor,Result&out){
 static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(tensor.v)>> ==6);
 static_assert(sizeof(double)==8&&std::numeric_limits<double>::is_iec559&&std::numeric_limits<double>::digits==53);
 Result candidate{};std::array<Dyadic,6>x;
 if constexpr(std::is_same_v<Result,double>){
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0])>,double>);
  for(unsigned i=0;i<6;++i){if(!std::isfinite(tensor.v[i]))return false;x[i]=Dyadic::from(tensor.v[i]);}
  if(!rounded(polynomial(x),candidate))return false;
 }else{
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0].v)>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(tensor.v[0].d[0])>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(candidate.v)>,double>);
  static_assert(std::is_same_v<std::remove_cvref_t<decltype(candidate.d[0])>,double>);
  static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(candidate.d)>> ==38);
  static_assert(std::tuple_size_v<std::remove_cvref_t<decltype(tensor.v[0].d)>> ==38);
  for(unsigned i=0;i<6;++i){if(!std::isfinite(tensor.v[i].v))return false;for(double seed:tensor.v[i].d)if(!std::isfinite(seed))return false;x[i]=Dyadic::from(tensor.v[i].v);}
  if(!rounded(polynomial(x),candidate.v))return false;const auto cof=gradient(x);
  for(unsigned j=0;j<38;++j){Radical directional{};for(unsigned i=0;i<6;++i)if(tensor.v[i].d[j]!=0)directional=directional+cof[i]*Dyadic::from(tensor.v[i].d[j]);if(!rounded(directional,candidate.d[j]))return false;}
 }
 out=candidate;return true;
}
} // namespace atlas::determinant_accuracy
