#pragma once
#include "atlas/tensor.hpp"

namespace atlas {
inline constexpr const char* symmetric_expm_version="symmetric-expm-taylor18-frobenius64-v1";
namespace expm_detail {
template<class T>using Matrix=std::array<std::array<T,3>,3>;
template<class T>bool multiply(const Matrix<T>& a,const Matrix<T>& b,Matrix<T>& out){
    Matrix<T> result{};
    for(int i=0;i<3;++i)for(int j=0;j<3;++j)for(int k=0;k<3;++k){
        const T product=a[i][k]*b[k][j];
        if(!finite_value(product))return false;
        result[i][j]=result[i][j]+product;
        if(!finite_value(result[i][j]))return false;
    }
    out=result;return true;
}
template<class T>bool symmetrize(Matrix<T>& a){
    for(int i=0;i<3;++i)for(int j=0;j<i;++j){
        const T v=T(.5)*a[i][j]+T(.5)*a[j][i];
        if(!finite_value(v))return false;
        a[i][j]=a[j][i]=v;
    }
    return true;
}
}
// Failure never changes out, including when input and output alias. All38Jet
// derivative slots are checked; primal cancellation cannot hide failure.
template<class T>bool tensor_expm_checked(const Sym<T>& a,Sym<T>& out){
    if(!finite_value(a))return false;
    double frobenius=0.;
    for(const auto& x:a.v)frobenius=std::hypot(frobenius,value(x));
    if(frobenius>64.)return false;
    using Matrix=expm_detail::Matrix<T>;const T root2(std::sqrt(2.));
    Matrix b{{{{a.v[0],a.v[3]/root2,a.v[5]/root2}},
              {{a.v[3]/root2,a.v[1],a.v[4]/root2}},
              {{a.v[5]/root2,a.v[4]/root2,a.v[2]}}}};
    double row_norm=0.;
    for(const auto& row:b){double n=0.;for(const auto& x:row)n+=std::abs(value(x));row_norm=std::max(row_norm,n);}
    int s=0;while(row_norm>.5){row_norm*=.5;++s;}
    const T factor(std::ldexp(1.,-s));
    for(auto& row:b)for(auto& x:row){x=x*factor;if(!finite_value(x))return false;}
    Matrix p{};for(int i=0;i<3;++i)p[i][i]=T(1.);
    for(int k=18;k>=1;--k){
        Matrix product;
        if(!expm_detail::multiply(b,p,product))return false;
        for(int i=0;i<3;++i)for(int j=0;j<3;++j){
            p[i][j]=T(i==j?1.:0.)+product[i][j]/T(k);
            if(!finite_value(p[i][j]))return false;
        }
        if(!expm_detail::symmetrize(p))return false;
    }
    for(int k=0;k<s;++k){
        Matrix product;
        if(!expm_detail::multiply(p,p,product)||!expm_detail::symmetrize(product))return false;
        p=product;
    }
    const auto result=make_sym(p[0][0],p[1][1],p[2][2],root2*p[0][1],root2*p[1][2],root2*p[0][2]);
    if(!finite_value(result))return false;
    out=result;return true;
}
// The temporary is unusable when the sticky flag is false. Generated callers
// check this flag before successful return; no exception crosses the model API.
template<class T>Sym<T> tensor_expm_or_mark(const Sym<T>& a,bool& ok){
    Sym<T> out;
    if(ok&&!tensor_expm_checked(a,out))ok=false;
    return out;
}
}
