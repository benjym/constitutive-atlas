#include "symmetric_spectral.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <cstdlib>
using namespace atlas;
using namespace atlas::spectral_candidate;
double number(const std::string&s){char* end=nullptr;const double v=std::strtod(s.c_str(),&end);if(end!=s.c_str()+s.size())throw std::runtime_error("invalid number");return v;}
Operation operation(const std::string&s){
    if(s=="max_value")return Operation::max_value;if(s=="mid_value")return Operation::mid_value;if(s=="min_value")return Operation::min_value;
    if(s=="max")return Operation::max;if(s=="mid")return Operation::mid;if(s=="min")return Operation::min;
    if(s=="upper_sum")return Operation::upper_sum;if(s=="lower_sum")return Operation::lower_sum;
    if(s=="projector_max")return Operation::projector_max;if(s=="projector_min")return Operation::projector_min;
    throw std::runtime_error("unknown operation");
}
template<class T>void fill(T&x){x=T(-777);if constexpr(std::is_same_v<T,Jet>)for(int j=0;j<max_derivatives;++j)x.d[j]=123+j;}
template<class T>bool unchanged(const T&a,const T&b){if constexpr(std::is_same_v<T,Jet>){return a.v==b.v&&a.d==b.d;}else return a==b;}
template<class T>void print(const T&a){std::cout<<"{\"value\":"<<value(a);if constexpr(std::is_same_v<T,Jet>){std::cout<<",\"derivatives\":[";for(int j=0;j<max_derivatives;++j){if(j)std::cout<<',';std::cout<<a.d[j];}std::cout<<']';}std::cout<<'}';}
template<class T>void call(const Sym<T>&a,Operation op){
    Diagnostic d;bool ok=false,preserved=true;
    if(op==Operation::projector_max||op==Operation::projector_min){
        Sym<T> out;for(auto&x:out.v)fill(x);const auto original=out;ok=projector_checked(a,op,out,d);
        for(int k=0;k<6;++k)preserved=preserved&&unchanged(out.v[k],original.v[k]);
        std::cout<<"\"output\":[";for(int k=0;k<6;++k){if(k)std::cout<<',';print(out.v[k]);}std::cout<<']';
    }else{T out;fill(out);const auto original=out;ok=scalar_checked(a,op,out,d);preserved=unchanged(out,original);std::cout<<"\"output\":[";print(out);std::cout<<']';}
    std::cout<<",\"ok\":"<<(ok?"true":"false")<<",\"failed_output_preserved\":"<<((!ok&&preserved)?"true":"false")<<",\"status\":\""<<d.status<<"\",\"diagnostic\":{\"scale_exponent\":"<<d.scale_exponent<<",\"norm\":"<<d.norm<<",\"residual\":"<<d.residual<<",\"orthogonality\":"<<d.orthogonality<<",\"minimum_gap\":"<<d.minimum_gap<<"}";
}
int main(){
    std::cout<<std::setprecision(17);std::string line;
    while(std::getline(std::cin,line)){
        try{
            std::istringstream in(line);std::string id,name,kind,token;in>>id>>name>>kind;if(!in)throw std::runtime_error("bad request");
            Sym<Jet> a;for(int k=0;k<6;++k){if(!(in>>token))throw std::runtime_error("missing value");a.v[k].v=number(token);}
            for(int j=0;j<max_derivatives;++j)for(int k=0;k<6;++k){if(!(in>>token))throw std::runtime_error("missing seed");a.v[k].d[j]=number(token);}
            if(in>>token)throw std::runtime_error("extra input");
            std::cout<<"{\"id\":\""<<id<<"\",\"operation\":\""<<name<<"\",\"kind\":\""<<kind<<"\",";
            if(kind=="jet")call(a,operation(name));else if(kind=="double"){Sym<double>b;for(int k=0;k<6;++k)b.v[k]=a.v[k].v;call(b,operation(name));}else throw std::runtime_error("bad kind");
            std::cout<<"}\n";
        }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
    }
    return 0;
}
