#include "atlas/tensor.hpp"
#include <iostream>
#include <random>
#include <stdexcept>

using Matrix=std::array<std::array<double,3>,3>;
using Vector=std::array<double,6>;
Matrix matrix(const Vector&v){const double r=std::sqrt(2.);return {{{v[0],v[3]/r,v[5]/r},{v[3]/r,v[1],v[4]/r},{v[5]/r,v[4]/r,v[2]}}};}
Vector reference(const Vector&v){
    const auto a=matrix(v);Matrix b{};
    for(int i=0;i<3;++i)for(int j=0;j<3;++j)for(int k=0;k<3;++k)b[i][j]+=a[i][k]*a[k][j];
    return {b[0][0],b[1][1],b[2][2],std::sqrt(2.)*b[0][1],std::sqrt(2.)*b[1][2],std::sqrt(2.)*b[0][2]};
}
int main(){
    try{
        std::mt19937 rng(2004);std::uniform_real_distribution<double> sample(-3.,3.);
        for(int case_id=0;case_id<80;++case_id){
            Vector v{};for(double&x:v)x=sample(rng);
            atlas::Sym<atlas::Jet>a;
            for(int i=0;i<6;++i){a.v[i]=atlas::Jet(v[i]);a.v[i].d[i]=1.;}
            auto got=atlas::tensor_square(a);auto want=reference(v);
            for(int i=0;i<6;++i)if(std::abs(got.v[i].v-want[i])>1e-12*std::max(1.,std::abs(want[i])))throw std::runtime_error("Cartesian tensor-square value mismatch");
            for(int j=0;j<6;++j){
                const double h=1e-6;auto plus=v,minus=v;plus[j]+=h;minus[j]-=h;
                const auto fp=reference(plus),fm=reference(minus);
                for(int i=0;i<6;++i){
                    double fd=(fp[i]-fm[i])/(2*h);
                    if(std::abs(got.v[i].d[j]-fd)>1e-8*std::max(1.,std::abs(fd)))throw std::runtime_error("Cartesian finite-difference/AD tensor-square mismatch");
                }
            }
        }
        std::cout<<"Tensor square: 80 Cartesian values and 2880 AD/finite-difference entries passed\n";
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
