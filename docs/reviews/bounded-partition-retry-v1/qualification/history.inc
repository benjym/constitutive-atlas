namespace history_study {
using namespace atlas;
double read(){std::string s;if(!(std::cin>>s))throw std::runtime_error("missing token");char*e;double x=std::strtod(s.c_str(),&e);if(e!=s.c_str()+s.size())throw std::runtime_error("bad number");return x;}
bool same(const State&a,const State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(std::bit_cast<std::uint64_t>(a[i])!=std::bit_cast<std::uint64_t>(b[i]))return false;return true;}
void bits(const State&s){std::cout<<'[';for(size_t i=0;i<s.size();++i){if(i)std::cout<<',';std::cout<<'"'<<std::bit_cast<std::uint64_t>(s[i])<<'"';}std::cout<<']';}
bool membership(const State&s,const State&p){bool result=false;if(!principal_range_accuracy::checked(tensor_from(s,0),2*p[3],result))throw std::runtime_error("membership diagnostic failed");return result;}
int run(){std::cout<<std::boolalpha;try{
 State p(4),initial(12);for(double&x:p)x=read();for(double&x:initial)x=read();int n;std::cin>>n;std::vector<State>loads(n,State(6));for(auto&d:loads)for(double&x:d)x=read();
 IntegrationSettings settings;settings.max_depth=0;State committed=initial;const auto baseline=integrate(0,initial,Sym<double>{},p,settings);if(!baseline.ok)throw std::runtime_error("baseline failed");
 bool stopped=false;int accepted=0;
 for(int i=0;i<n;++i){
  const State parent=committed,oldp=p,oldload=loads[i];
  if(stopped){std::cout<<"{\"step\":"<<i<<",\"attempted\":false,\"parent_bits\":";bits(parent);std::cout<<"}\n";continue;}
  const bool parent_in=membership(parent,p);const auto result=integrate(0,committed,tensor_from(loads[i],0),p,settings);
  const bool unchanged=same(parent,committed)&&same(p,oldp)&&same(loads[i],oldload);const bool rollback=same(result.state,parent);
  const bool output_in=membership(result.state,p);const auto recovery=integrate(0,initial,Sym<double>{},p,settings);const bool recovered=recovery.ok&&same(recovery.state,baseline.state);
  if(result.ok){committed=result.state;++accepted;}else stopped=true;
  std::cout<<"{\"step\":"<<i<<",\"attempted\":true,\"ok\":"<<result.ok<<",\"parent_in\":"<<parent_in<<",\"output_in\":"<<output_in<<",\"input_unchanged\":"<<unchanged<<",\"returned_parent\":"<<rollback<<",\"baseline_recovery\":"<<recovered<<",\"iterations\":"<<result.diagnostics.iterations<<",\"substeps\":"<<result.diagnostics.substeps<<",\"parent_bits\":";bits(parent);std::cout<<",\"output_bits\":";bits(result.state);std::cout<<",\"committed_bits\":";bits(committed);std::cout<<"}\n";
 }
 std::cout<<"{\"summary\":true,\"scheduled\":"<<n<<",\"accepted\":"<<accepted<<",\"stopped\":"<<stopped<<",\"final_bits\":";bits(committed);std::cout<<"}\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
}
