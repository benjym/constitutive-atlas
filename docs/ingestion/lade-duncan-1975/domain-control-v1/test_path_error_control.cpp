#include "atlas/solver.hpp"
#include <iostream>
int main(){
    int m=-1;for(size_t i=0;i<atlas::models().size();++i)if(atlas::models()[i].id=="lade-duncan-1975-left-elastic-eq19-gap-v3")m=int(i);
    if(m<0)return 2;
    atlas::IntegrationSettings settings;settings.increment_tolerance=1e-7;settings.positive_stress_metric=true;
    auto p=atlas::default_parameters(m);int checks=0,failures=0;
    auto check=[&](bool ok){++checks;if(!ok)++failures;};
    check(atlas::path_metric_layout(m,settings));
    for(double scale:{1.,1e-12,1e-24}){
        atlas::State parent{100*scale,100*scale,100*scale,0,0,0,13,0},full=parent,half=parent,two=parent;
        for(int i=0;i<3;++i){full[i]=99*scale;half[i]=99.5*scale;two[i]=99.1*scale;}
        double error=0;check(atlas::implicit_path_error(m,parent,full,half,two,p,settings,error));
        const double expected=std::sqrt(3.)*.1/99.;check(std::abs(error-expected)<1e-15);
        full[0]=-scale;check(!atlas::implicit_path_error(m,parent,full,half,two,p,settings,error));
        full[0]=0;check(!atlas::implicit_path_error(m,parent,full,half,two,p,settings,error));
    }
    atlas::State parent{120,100,80,0,0,0,13,0},full=parent,half=parent,two=parent;
    full[0]-=.3;full[1]-=.2;full[2]-=.1;two[0]-=.31;two[1]-=.21;two[2]-=.11;
    double e1=0,e2=0;check(atlas::implicit_path_error(m,parent,full,half,two,p,settings,e1));
    auto rotate=[](atlas::State a){double x=a[0],y=a[1],xy=a[3];a[0]=(x+y)/2-xy/std::sqrt(2.);a[1]=(x+y)/2+xy/std::sqrt(2.);a[3]=(x-y)/std::sqrt(2.);return a;};
    check(atlas::implicit_path_error(m,rotate(parent),rotate(full),rotate(half),rotate(two),p,settings,e2));
    check(std::abs(e1-e2)<1e-15);
    std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"passed\":"<<(failures?"false":"true")<<"}\n";
    return failures?1:0;
}
