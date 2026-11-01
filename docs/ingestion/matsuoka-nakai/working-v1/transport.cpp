// Generic persistent CLI transport around the existing public C ABI.
// No constitutive equations or model-specific branches are implemented here.
#define main atlas_original_cli_main
#include "atlas_cli_source.cpp"
#undef main
int main(){
    std::string line;
    while(std::getline(std::cin,line)){
        std::vector<std::string> fields;std::stringstream input(line);std::string field;
        while(std::getline(input,field,'\t'))fields.push_back(field);
        if(fields.size()!=5){std::cout<<"{\"ok\":false,\"message\":\"five fields required\"}"<<std::endl;continue;}
        std::cout<<atlas_integrate_with_settings(fields[0].c_str(),fields[1].c_str(),fields[2].c_str(),fields[3].c_str(),fields[4].c_str())<<std::endl;
    }
}
