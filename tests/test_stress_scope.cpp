// Synthetic metadata checks only: no material evaluation or integration.
#include "atlas/schedule.hpp"
#include "atlas/recorded.hpp"
#include <iostream>
#include <map>
int main() {
    using atlas::StressScope;
    const std::map<std::string,std::pair<StressScope,int>> expected={
        {"scope-legacy-incremental",{StressScope::effective,-1}},
        {"scope-explicit-incremental",{StressScope::effective,-1}},
        {"scope-legacy-timed",{StressScope::unspecified,0}},
        {"scope-effective-timed",{StressScope::effective,0}},
        {"scope-total-timed",{StressScope::total,0}},
        {"scope-clock",{StressScope::none,-1}},
        {"scope-legacy-clock",{StressScope::none,-1}}
    };
    if(atlas::models().size()!=expected.size())return 1;
    for(const auto& model:atlas::models()) {
        const auto found=expected.find(model.id);
        if(found==expected.end()||model.stress_scope!=found->second.first||model.stress_offset!=found->second.second)return 2;
        std::cout<<model.id<<" scope="<<int(model.stress_scope)<<" observable_stress_offset="<<model.stress_offset<<"\n";
    }
    std::cout<<"Seven metadata rows verified; material calls=0\n";
}
