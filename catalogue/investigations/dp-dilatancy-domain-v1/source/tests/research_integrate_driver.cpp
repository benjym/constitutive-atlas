// Persistent research transport over the unchanged common material C API.
// No constitutive equations, model dispatch or integration policy lives here.
#define main atlas_common_cli_main
#include "../cpp/main.cpp"
#undef main

int main(int argc,char**argv){
    if(argc!=2||std::string(argv[1])!="--stream")return atlas_common_cli_main(argc,argv);
    try{
        std::string line;
        while(std::getline(std::cin,line)){
            if(line=="--describe"){
                std::cout<<atlas_describe()<<'\n'<<std::flush;
                continue;
            }
            std::vector<std::string>fields;
            std::size_t start=0;
            for(;;){
                const auto end=line.find('\t',start);
                fields.push_back(line.substr(start,end==std::string::npos?end:end-start));
                if(end==std::string::npos)break;
                start=end+1;
            }
            if(fields.size()!=5)throw std::runtime_error("stream requests require five tab-separated fields");
            std::cout<<atlas_integrate_with_settings(fields[0].c_str(),fields[1].c_str(),fields[2].c_str(),fields[3].c_str(),fields[4].c_str())<<'\n'<<std::flush;
        }
        if(std::cin.bad())throw std::runtime_error("stream input failed");
        return 0;
    }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
