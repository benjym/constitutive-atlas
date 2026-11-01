namespace corpus_study {
using namespace atlas;
double number(const std::string&s){char*end=nullptr;double v=std::strtod(s.c_str(),&end);if(end!=s.c_str()+s.size())throw std::runtime_error("invalid token");return v;}
bool same(double a,double b){return std::bit_cast<std::uint64_t>(a)==std::bit_cast<std::uint64_t>(b);}
bool same(const State&a,const State&b){if(a.size()!=b.size())return false;for(size_t i=0;i<a.size();++i)if(!same(a[i],b[i]))return false;return true;}
void array(const State&v){std::cout<<'[';for(size_t i=0;i<v.size();++i){if(i)std::cout<<',';if(!std::isfinite(v[i]))std::cout<<"null";else std::cout<<v[i];}std::cout<<']';}
Advance baseline(){State p{1,3,2,3},z{0,0,0,0,0,0,.125,-.25,.375,-.5,.625,-.75};Sym<double>d;IntegrationSettings s;s.max_depth=0;return integrate(0,z,d,p,s);}
int run(){std::cout<<std::setprecision(17);std::string line;while(std::getline(std::cin,line))try{
 std::istringstream in(line);std::string id,mode,token;int iterations,depth,np,nc,nn,nd;
 if(!(in>>id>>mode>>iterations>>depth>>np>>nc>>nn>>nd))throw std::runtime_error("invalid header");
 auto read=[&](){if(!(in>>token))throw std::runtime_error("missing token");return number(token);};
 State p(np),z(nc),zn(nn),de(nd);for(State*v:{&p,&z,&zn,&de})for(double&x:*v)x=read();
 std::array<State,max_derivatives>sz,sn,sd;
 for(int j=0;j<max_derivatives;++j){sz[j].resize(12);sn[j].resize(12);sd[j].resize(6);for(State*v:{&sz[j],&sn[j],&sd[j]})for(double&x:*v)x=read();}
 if(in>>token)throw std::runtime_error("extra token");
 const auto oldp=p,oldz=z,oldzn=zn,oldde=de;const auto before=baseline();if(!before.ok)throw std::runtime_error("baseline failed");
 study_branch=-1;bool ok=false,output_finite=true,returned_parent=false,tentative_ok=false,tentative_changed=false;State values;std::vector<State>derivatives;Diagnostics diag;
 bool shape=np==4&&nc==12&&nn==12&&nd==6;
 if(shape){Sym<double>d=tensor_from(de,0);IntegrationSettings settings;settings.max_iterations=iterations;settings.max_depth=depth;
  if(mode=="double")ok=valid_parameters(0,p)&&evaluate_model(0,z,zn,d,p,values);
  else if(mode=="jet"){
   std::vector<Jet>x(12),xn(12),out;Sym<Jet>dd;
   for(int i=0;i<12;++i){x[i]=Jet(z[i]);xn[i]=Jet(zn[i]);for(int j=0;j<max_derivatives;++j){x[i].d[j]=sz[j][i];xn[i].d[j]=sn[j][i];}}
   for(int i=0;i<6;++i){dd.v[i]=Jet(de[i]);for(int j=0;j<max_derivatives;++j)dd.v[i].d[j]=sd[j][i];}
   ok=valid_parameters(0,p)&&evaluate_model(0,x,xn,dd,p,out);
   for(const auto&v:out){values.push_back(v.v);derivatives.emplace_back(v.d.begin(),v.d.end());output_finite=output_finite&&finite_value(v);}
  }else if(mode=="solve"||mode=="transaction"){
   if(mode=="transaction"){State tentative;Diagnostics td;tentative_ok=implicit_step(0,zn,d,p,tentative,td,settings);tentative_changed=!same(tentative,zn);}
   auto a=integrate(0,zn,d,p,settings);ok=a.ok;values=a.state;diag=a.diagnostics;returned_parent=same(a.state,zn);
  }else throw std::runtime_error("unknown mode");
 }
 int branch=study_branch;output_finite=output_finite&&finite(values);if(!output_finite)ok=false;
 const auto after=baseline();bool recovery=after.ok&&same(before.state,after.state);
 bool unchanged=same(p,oldp)&&same(z,oldz)&&same(zn,oldzn)&&same(de,oldde);
 std::cout<<"{\"id\":\""<<id<<"\",\"mode\":\""<<mode<<"\",\"ok\":"<<(ok?"true":"false")<<",\"branch\":"<<branch<<",\"shape\":"<<(shape?"true":"false")<<",\"finite\":"<<(output_finite?"true":"false")<<",\"input_unchanged\":"<<(unchanged?"true":"false")<<",\"baseline_recovery\":"<<(recovery?"true":"false")<<",\"returned_parent\":"<<(returned_parent?"true":"false")<<",\"tentative_ok\":"<<(tentative_ok?"true":"false")<<",\"tentative_changed\":"<<(tentative_changed?"true":"false")<<",\"iterations\":"<<diag.iterations<<",\"substeps\":"<<diag.substeps<<",\"rejected\":"<<diag.rejected<<",\"values\":";array(values);
 std::cout<<",\"derivatives\":[";for(size_t i=0;i<derivatives.size();++i){if(i)std::cout<<',';array(derivatives[i]);}std::cout<<"]}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}return 0;}
}
