#pragma once
#include <limits>
#include <algorithm>
#include <array>
#include <cmath>
#include <vector>

namespace atlas {
constexpr int max_state = 24;
constexpr int max_derivatives = max_state + 6; // state plus mixed-control increments
struct Jet {
    double v = 0;
    std::array<double,max_derivatives> d{};
    Jet()=default;
    Jet(double value):v(value) {}
};
inline double value(double x) { return x; }
inline double value(const Jet& x) { return x.v; }
inline Jet operator+(const Jet& a,const Jet& b) { Jet c(a.v+b.v); for(int i=0;i<max_derivatives;++i)c.d[i]=a.d[i]+b.d[i]; return c; }
inline Jet operator-(const Jet& a,const Jet& b) { Jet c(a.v-b.v); for(int i=0;i<max_derivatives;++i)c.d[i]=a.d[i]-b.d[i]; return c; }
inline Jet operator-(const Jet& a) { return Jet(0)-a; }
inline Jet operator+(const Jet& a) { return a; }
inline Jet operator*(const Jet& a,const Jet& b) { Jet c(a.v*b.v); for(int i=0;i<max_derivatives;++i)c.d[i]=a.d[i]*b.v+a.v*b.d[i]; return c; }
inline Jet operator/(const Jet& a,const Jet& b) { Jet c(a.v/b.v); for(int i=0;i<max_derivatives;++i)c.d[i]=(a.d[i]-c.v*b.d[i])/b.v; return c; }
inline bool operator>(const Jet&a,const Jet&b){return a.v>b.v;}
inline bool operator<(const Jet&a,const Jet&b){return a.v<b.v;}
inline bool operator>=(const Jet&a,const Jet&b){return a.v>=b.v;}
inline bool operator<=(const Jet&a,const Jet&b){return a.v<=b.v;}
inline Jet unary(const Jet& a,double v,double derivative) { Jet b(v);for(int i=0;i<max_derivatives;++i)b.d[i]=derivative*a.d[i];return b; }
inline double asqrt(double a){return std::sqrt(a);}
inline Jet asqrt(const Jet&a){const double v=std::sqrt(a.v);return unary(a,v,v>0?.5/v:0.);}
inline double aexp(double a){return std::exp(a);}
inline Jet aexp(const Jet&a){return unary(a,std::exp(a.v),std::exp(a.v));}
inline double alog(double a){return std::log(a);}
inline Jet alog(const Jet&a){return unary(a,std::log(a.v),1/a.v);}
inline double asin(double a){return std::sin(a);}
inline Jet asin(const Jet&a){return unary(a,std::sin(a.v),std::cos(a.v));}
inline double acos(double a){return std::cos(a);}
inline Jet acos(const Jet&a){return unary(a,std::cos(a.v),-std::sin(a.v));}
inline double aabs(double a){return std::abs(a);}
inline Jet aabs(const Jet&a){return unary(a,std::abs(a.v),a.v>=0?1:-1);}
inline double apow(double a,double b){return std::pow(a,b);}
inline Jet apow(const Jet&a,const Jet&b){
    const double v=std::pow(a.v,b.v);Jet c(v);
    for(int i=0;i<max_derivatives;++i) {
        const double da=a.d[i]==0?0:b.v*std::pow(a.v,b.v-1)*a.d[i];
        const double db=b.d[i]==0?0:v*std::log(a.v)*b.d[i];
        c.d[i]=da+db;
    }
    return c;
}
template<class T>T amin(const T&a,const T&b){return a<b?a:b;}
template<class T>T amax(const T&a,const T&b){return a>b?a:b;}
template<class T>struct Sym { std::array<T,6> v{}; };
template<class T>Sym<T> make_sym(T xx,T yy,T zz,T xy,T yz,T xz){return Sym<T>{{xx,yy,zz,xy,yz,xz}};}
template<class T>bool axisymmetric_x(const Sym<T>& a){
    double scale=0;for(const auto& v:a.v){if(!std::isfinite(value(v)))return false;scale=std::max(scale,std::abs(value(v)));}
    const double tol=64*std::numeric_limits<double>::epsilon()*scale;
    return std::abs(value(a.v[1])-value(a.v[2]))<=tol&&std::abs(value(a.v[3]))<=tol&&std::abs(value(a.v[4]))<=tol&&std::abs(value(a.v[5]))<=tol;
}
template<class T>Sym<T> identity(){Sym<T> s;s.v[0]=s.v[1]=s.v[2]=T(1);return s;}
template<class T>Sym<T> operator+(const Sym<T>&a,const Sym<T>&b){Sym<T> c;for(int i=0;i<6;++i)c.v[i]=a.v[i]+b.v[i];return c;}
template<class T>Sym<T> operator-(const Sym<T>&a,const Sym<T>&b){Sym<T> c;for(int i=0;i<6;++i)c.v[i]=a.v[i]-b.v[i];return c;}
template<class T>Sym<T> operator-(const Sym<T>&a){return T(-1)*a;}
template<class T>Sym<T> operator+(const Sym<T>&a){return a;}
template<class T>Sym<T> operator*(const T&a,const Sym<T>&b){Sym<T> c;for(int i=0;i<6;++i)c.v[i]=a*b.v[i];return c;}
template<class T>Sym<T> operator*(const Sym<T>&a,const T&b){return b*a;}
template<class T>Sym<T> operator/(const Sym<T>&a,const T&b){return (T(1)/b)*a;}
template<class T>T trace(const Sym<T>&a){return a.v[0]+a.v[1]+a.v[2];}
template<class T>Sym<T> dev(const Sym<T>&a){return a-(trace(a)/T(3))*identity<T>();}
template<class T>T dot(const Sym<T>&a,const Sym<T>&b){T c(0);for(int i=0;i<6;++i)c=c+a.v[i]*b.v[i];return c;}
template<class T>T norm(const Sym<T>&a){return asqrt(dot(a,a));}
template<class T>T cube_trace(const Sym<T>&a){
    const T x=a.v[0],y=a.v[1],z=a.v[2],xy=a.v[3]/T(std::sqrt(2.)),yz=a.v[4]/T(std::sqrt(2.)),xz=a.v[5]/T(std::sqrt(2.));
    return x*x*x+y*y*y+z*z*z+T(3)*((x+y)*xy*xy+(y+z)*yz*yz+(x+z)*xz*xz)+T(6)*xy*yz*xz;
}
template<class T>Sym<T> tensor_from(const std::vector<T>&v,int offset){Sym<T> a;for(int i=0;i<6;++i)a.v[i]=v.at(offset+i);return a;}
template<class T>void put_tensor(std::vector<T>&v,int offset,const Sym<T>&a){for(int i=0;i<6;++i)v.at(offset+i)=a.v[i];}
}
