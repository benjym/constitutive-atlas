#include "advance.hpp"
#include <iostream>
#include <iomanip>
#include <string>

namespace wh=atlas::weighted_history_v1;
int main() {
    std::cout<<std::setprecision(17)<<std::showpoint;
    int kind=0,index=0;
    while(std::cin>>kind>>index){
        atlas::IntegrationSettings settings;
        wh::Binding b{0,6,7};
        atlas::State p(23),z(13);
        atlas::Sym<double> inc;
        if(!(std::cin>>settings.rate_tolerance>>settings.max_substeps))return 2;
        settings.max_depth=20;
        for(double& x:p)if(!(std::cin>>x))return 2;
        for(double& x:z)if(!(std::cin>>x))return 2;
        for(double& x:inc.v)if(!(std::cin>>x))return 2;
        b.R=p[20];b.beta=p[21];b.stress_margin=p[16];
        bool ok=false;int accepted=0,discarded=0;std::string message;
        if(kind==0){
            wh::History h;
            ok=wh::endpoint(z[6],wh::block(z,7),inc.v,b.R,b.beta,h);
            z[6]=h.e;
            std::copy(h.h.begin(),h.h.end(),z.begin()+7);
            accepted=h.powers;
        }else if(kind==1){
            auto q=wh::advance(0,z,inc,p,settings,b);
            z=q.state;ok=q.ok;accepted=q.diagnostics.substeps;discarded=q.diagnostics.discarded_substeps;
            message=q.message;
        }else return 2;
        std::cout<<"{\"index\":"<<index<<",\"ok\":"<<(ok?"true":"false")
                 <<",\"accepted\":"<<accepted<<",\"discarded\":"<<discarded
                 <<",\"message\":"<<std::quoted(message)<<",\"state\":[";
        for(size_t i=0;i<z.size();++i)std::cout<<(i?",":"")<<z[i];
        std::cout<<"]}\n";
    }
    return std::cin.eof()?0:2;
}
