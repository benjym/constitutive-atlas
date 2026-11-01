#pragma once
// Prospective generic primitive candidate; not installed in the production DSL.
#include "atlas/tensor.hpp"
#include <numeric>
#include <type_traits>
#include <string>
namespace atlas::spectral_candidate {
inline constexpr const char* version="symmetric3-scaled-cyclic-jacobi24-v1-candidate";
using Matrix=std::array<std::array<double,3>,3>;
enum class Operation { max_value,mid_value,min_value,max,mid,min,upper_sum,lower_sum,projector_max,projector_min };
struct Diagnostic {
    std::string status="ok";
    int scale_exponent=0;
    double residual=0,orthogonality=0,norm=0,minimum_gap=0;
};
struct Spectrum {
    Matrix original{},vectors{};
    std::array<double,3> eigen{},diagonal_values{};
    int exponent=0;
    bool diagonal=false;
    Diagnostic diagnostic;
};
inline bool fail(Diagnostic& d,const char* message){d.status=message;return false;}
inline double matrix_norm(const Matrix&a){double n=0;for(const auto&r:a)for(double x:r)n=std::hypot(n,x);return n;}
inline bool cartesian_scaled(const std::array<double,6>&a,Matrix&out,int&exponent,Diagnostic&d){
    double largest=0;for(double x:a){if(!std::isfinite(x))return fail(d,"nonfinite_input");largest=std::max(largest,std::abs(x));}
    exponent=0;if(largest!=0)std::frexp(largest,&exponent);
    std::array<double,6> s{};
    for(int i=0;i<6;++i){s[i]=std::ldexp(a[i],-exponent);if(a[i]!=0&&s[i]==0)return fail(d,"scaling_underflow");}
    constexpr double root2=1.414213562373095048801688724209698;
    out={{{s[0],s[3]/root2,s[5]/root2},{s[3]/root2,s[1],s[4]/root2},{s[5]/root2,s[4]/root2,s[2]}}};
    for(int i=3;i<6;++i)if(s[i]!=0&&s[i]/root2==0)return fail(d,"shear_decode_underflow");
    return true;
}
inline bool decompose(const std::array<double,6>&input,Spectrum&out,Diagnostic&d){
    Spectrum s;for(int i=0;i<3;++i)s.vectors[i][i]=1;
    s.diagonal=input[3]==0&&input[4]==0&&input[5]==0;
    // Preserve tiny diagonal eigenvalues even when a common scale would erase them.
    if(s.diagonal){
        double largest=0;for(double x:input){if(!std::isfinite(x))return fail(d,"nonfinite_input");largest=std::max(largest,std::abs(x));}
        if(largest!=0)std::frexp(largest,&s.exponent);
        std::array<int,3> order{0,1,2};std::stable_sort(order.begin(),order.end(),[&](int i,int j){return input[i]>input[j];});
        s.vectors={};
        for(int k=0;k<3;++k){s.diagonal_values[k]=input[order[k]];s.eigen[k]=std::ldexp(input[order[k]],-s.exponent);s.vectors[order[k]][k]=1;}
        for(int i=0;i<3;++i)s.original[i][i]=std::ldexp(input[i],-s.exponent);
    }else{
        if(!cartesian_scaled(input,s.original,s.exponent,d))return false;
        Matrix a=s.original;
        constexpr std::array<std::array<int,2>,3> pairs{{{0,1},{0,2},{1,2}}};
        for(int sweep=0;sweep<24;++sweep)for(auto pair:pairs){
            const int p=pair[0],q=pair[1];const double off=a[p][q];if(off==0)continue;
            const double delta=.5*a[q][q]-.5*a[p][p];
            const double denom=delta+std::copysign(std::hypot(delta,off),delta);
            if(denom==0||!std::isfinite(denom))return fail(d,"rotation_range");
            const double t=off/denom,c=1/std::hypot(1.,t),sn=t*c;
            a[p][p]-=t*off;a[q][q]+=t*off;a[p][q]=a[q][p]=0;
            for(int k=0;k<3;++k){
                if(k!=p&&k!=q){const double kp=a[k][p],kq=a[k][q];a[k][p]=a[p][k]=c*kp-sn*kq;a[k][q]=a[q][k]=sn*kp+c*kq;}
                const double vp=s.vectors[k][p],vq=s.vectors[k][q];s.vectors[k][p]=c*vp-sn*vq;s.vectors[k][q]=sn*vp+c*vq;
            }
        }
        std::array<int,3> order{0,1,2};std::stable_sort(order.begin(),order.end(),[&](int i,int j){return a[i][i]>a[j][j];});
        const Matrix unsorted=s.vectors;
        for(int k=0;k<3;++k){s.eigen[k]=a[order[k]][order[k]];for(int i=0;i<3;++i)s.vectors[i][k]=unsorted[i][order[k]];}
    }
    d.scale_exponent=s.exponent;d.norm=matrix_norm(s.original);
    for(int i=0;i<3;++i)for(int j=0;j<3;++j){
        double av=0,vv=0;for(int k=0;k<3;++k){av+=s.original[i][k]*s.vectors[k][j];vv+=s.vectors[k][i]*s.vectors[k][j];}
        d.residual=std::hypot(d.residual,av-s.vectors[i][j]*s.eigen[j]);
        d.orthogonality=std::hypot(d.orthogonality,vv-double(i==j));
    }
    constexpr double eps=std::numeric_limits<double>::epsilon();
    if(!std::isfinite(d.residual)||!std::isfinite(d.orthogonality)||d.residual>128*eps*d.norm||d.orthogonality>128*eps)return fail(d,"decomposition_not_converged");
    d.minimum_gap=std::min(s.eigen[0]-s.eigen[1],s.eigen[1]-s.eigen[2]);
    s.diagnostic=d;out=s;return true;
}
inline bool is_value_only(Operation op){return op==Operation::max_value||op==Operation::mid_value||op==Operation::min_value;}
inline int selected(Operation op){return op==Operation::min_value||op==Operation::min||op==Operation::upper_sum||op==Operation::projector_min?2:op==Operation::mid_value||op==Operation::mid?1:0;}
inline bool isolated(const Spectrum&s,int i,Diagnostic&d){
    constexpr double eps=std::numeric_limits<double>::epsilon();
    for(int j=0;j<3;++j)if(i!=j&&!(std::abs(s.eigen[i]-s.eigen[j])>1024*eps*d.norm))return fail(d,"selected_eigenvalue_unresolved");
    return true;
}
inline Matrix projector(const Spectrum&s,int i){Matrix p{};for(int r=0;r<3;++r)for(int c=0;c<3;++c)p[r][c]=s.vectors[r][i]*s.vectors[c][i];return p;}
inline double bilinear(const Spectrum&s,const Matrix&h,int i,int j){double result=0;for(int r=0;r<3;++r)for(int c=0;c<3;++c)result+=s.vectors[r][i]*h[r][c]*s.vectors[c][j];return result;}
inline bool scalar_value(const Spectrum&s,Operation op,double&v,Diagnostic&d){
    if(op==Operation::projector_max||op==Operation::projector_min)return fail(d,"wrong_operation_shape");
    const int i=selected(op);if(!is_value_only(op)&&!isolated(s,i,d))return false;
    if(s.diagonal){if(op==Operation::upper_sum)v=s.diagonal_values[0]+s.diagonal_values[1];else if(op==Operation::lower_sum)v=s.diagonal_values[1]+s.diagonal_values[2];else v=s.diagonal_values[i];}
    else {double x=s.eigen[i];if(op==Operation::upper_sum)x=s.eigen[0]+s.eigen[1];else if(op==Operation::lower_sum)x=s.eigen[1]+s.eigen[2];v=std::ldexp(x,s.exponent);}
    return std::isfinite(v)||fail(d,"output_range");
}
inline std::array<double,6> mandel(const Matrix&a){constexpr double r=1.414213562373095048801688724209698;return {a[0][0],a[1][1],a[2][2],r*a[0][1],r*a[1][2],r*a[0][2]};}
template<class T>bool scalar_checked(const Sym<T>&a,Operation op,T&out,Diagnostic&d){
    d={};if(!finite_value(a))return fail(d,"nonfinite_input");
    std::array<double,6> values;for(int k=0;k<6;++k)values[k]=value(a.v[k]);
    Spectrum s;if(!decompose(values,s,d))return false;
    double primal=0;if(!scalar_value(s,op,primal,d))return false;
    T candidate(primal);
    if constexpr(std::is_same_v<T,Jet>){
        if(!is_value_only(op))for(int j=0;j<max_derivatives;++j){
            std::array<double,6> seeds;for(int k=0;k<6;++k)seeds[k]=a.v[k].d[j];
            Matrix h;int exponent=0;if(!cartesian_scaled(seeds,h,exponent,d))return false;
            const int i=selected(op);double result=0;
            if(op==Operation::upper_sum||op==Operation::lower_sum){for(int k=0;k<3;++k)if(k!=i)result+=bilinear(s,h,k,k);}
            else result=bilinear(s,h,i,i);
            candidate.d[j]=std::ldexp(result,exponent);
            if(!std::isfinite(candidate.d[j]))return fail(d,"derivative_range");
        }
    }
    out=candidate;return true;
}
template<class T>bool projector_checked(const Sym<T>&a,Operation op,Sym<T>&out,Diagnostic&d){
    d={};if(!finite_value(a))return fail(d,"nonfinite_input");
    if(op!=Operation::projector_max&&op!=Operation::projector_min)return fail(d,"wrong_operation_shape");
    std::array<double,6> values;for(int k=0;k<6;++k)values[k]=value(a.v[k]);
    Spectrum s;if(!decompose(values,s,d))return false;const int i=selected(op);if(!isolated(s,i,d))return false;
    Sym<T> candidate;const auto pv=mandel(projector(s,i));for(int k=0;k<6;++k)candidate.v[k]=T(pv[k]);
    if constexpr(std::is_same_v<T,Jet>){
        for(int column=0;column<max_derivatives;++column){
            std::array<double,6> seeds;for(int k=0;k<6;++k)seeds[k]=a.v[k].d[column];
            Matrix h;int exponent=0;if(!cartesian_scaled(seeds,h,exponent,d))return false;
            Matrix dp{};
            for(int j=0;j<3;++j)if(j!=i){
                const double coefficient=bilinear(s,h,j,i)/(s.eigen[i]-s.eigen[j]);
                for(int r=0;r<3;++r)for(int c=0;c<3;++c)dp[r][c]+=coefficient*(s.vectors[r][j]*s.vectors[c][i]+s.vectors[r][i]*s.vectors[c][j]);
            }
            const auto components=mandel(dp);
            for(int k=0;k<6;++k){candidate.v[k].d[column]=std::ldexp(components[k],exponent-s.exponent);if(!std::isfinite(candidate.v[k].d[column]))return fail(d,"derivative_range");}
        }
    }
    out=candidate;return true;
}
} // namespace atlas::spectral_candidate
