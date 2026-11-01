int laboratory_run(){
 const auto id=atlas::models().at(0).id;std::string label,pars,initial,controls,settings;int protocol,legacy;
 const std::string baseline="64,64,64,0,0,0,0,0,0,0,0,0";
 while(std::cin>>label>>protocol>>legacy>>std::quoted(pars)>>std::quoted(initial)>>std::quoted(controls)>>std::quoted(settings)){
  auto before=std::vector<std::string>{pars,initial,controls,settings};
  std::string response=legacy?atlas_run_controls_with_settings(id.c_str(),pars.c_str(),initial.c_str(),protocol,controls.c_str(),settings.c_str()):atlas_run_controls_scope_with_settings(id.c_str(),pars.c_str(),initial.c_str(),protocol,controls.c_str(),settings.c_str());
  std::string recovery=atlas_run_controls_scope_with_settings(id.c_str(),"1024,3072,2048,8",baseline.c_str(),4,"0000000000000000,0000000000000000","2e-10,1e-6,45,0,20000,11");
  bool unchanged=before==std::vector<std::string>{pars,initial,controls,settings};
  std::cout<<"{\"label\":"<<quote(label)<<",\"inputs_unchanged\":"<<(unchanged?"true":"false")<<",\"response\":"<<response<<",\"recovery\":"<<recovery<<"}\n";
 }
 return std::cin.eof()?0:2;
}
