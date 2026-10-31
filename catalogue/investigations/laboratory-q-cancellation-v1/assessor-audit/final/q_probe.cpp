#include "atlas/stress_observables.hpp"
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <sstream>
#include <string>
#include <iostream>
#include <limits>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define EXPORT
#endif
static std::string output;
extern "C" EXPORT const char* atlas_q_probe(const char* wire) {
    static_assert(sizeof(double)==8 && std::numeric_limits<double>::is_iec559);
    if(!wire) return "{\"ok\":false}";
    const std::string text(wire);if(text.size()!=101) return "{\"ok\":false}";
    atlas::Sym<double> a;
    for(int i=0;i<6;++i) {
        std::uint64_t bits=0;
        for(int j=0;j<16;++j) {
            const char c=text[17*i+j];if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return "{\"ok\":false}";
            bits=(bits<<4)|std::uint64_t(c<='9'?c-'0':c-'a'+10);
        }
        if(i<5 && text[17*i+16]!=',')return "{\"ok\":false}";
        std::memcpy(&a.v[i],&bits,8);
        if(!std::isfinite(a.v[i])||std::abs(a.v[i])>1e300)return "{\"ok\":false}";
    }
    const double q=atlas::deviatoric_stress_magnitude(a);std::uint64_t qb;std::memcpy(&qb,&q,8);
    std::ostringstream o;o<<std::setprecision(17)<<"{\"ok\":true,\"q\":"<<q<<",\"q_bits\":\""<<std::hex<<std::setw(16)<<std::setfill('0')<<qb<<"\"}";
    output=o.str();return output.c_str();
}
#ifndef __EMSCRIPTEN__
int main(int argc,char**argv){if(argc!=2)return 2;std::cout<<atlas_q_probe(argv[1])<<'\n';}
#endif
