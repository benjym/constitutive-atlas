// Generated checked controlled-time C ABI, all writes after success.
#include "controlled_time_models.hpp"
#include "atlas/controlled_time_runtime.hpp"
#include <array>
#include <cstdint>
using namespace atlas::controlled_time;
static const std::vector<Definition> definitions={{8,{0,0,0,0,0,0,2,1},{{-1,1,0},{0,6,1},{7,1,0},{7,1,1},{6,1,0},{6,1,1}},[](const auto&z,const auto&p,const auto&i,auto&r,auto&o,auto&s,bool initial){return atlas::controlled_time_generated::evaluate(0,z,p,i,r,o,s,initial);}}};
static const std::vector<std::array<int,6>> shapes={{8,30,8,13,6,4}};
static const char* model_hashes[]={"fdda17fced48f8f368a45ab620b1e4dcdd7666a8b2146ac983b03a298f9b302d"};
extern "C" const char* controlled_time_model_hash(int m){return m>=0&&size_t(m)<definitions.size()?model_hashes[m]:nullptr;}
extern "C" const char* controlled_time_catalogue_hash(){return "bacbeb656d0f44cc1e33520d0d293fe73f81cc72c04ee42a62b8cec1905f97a9";}
extern "C" const char* controlled_time_catalogue_file_hash(){return "ed97d25a2b9f96811f94f9d60f32018927ede7810078dc09e3429cf3a0ee6ad5";}
struct Range{std::uintptr_t lo,hi;};
static bool range(const double*p,int n,Range&r){if(n<0||(n>0&&!p))return false;const auto lo=reinterpret_cast<std::uintptr_t>(p);if(size_t(n)>std::numeric_limits<std::uintptr_t>::max()/sizeof(double))return false;const auto bytes=size_t(n)*sizeof(double);if(lo>std::numeric_limits<std::uintptr_t>::max()-bytes)return false;r={lo,lo+bytes};return true;}
static bool disjoint(Range a,Range b){return a.lo==a.hi||b.lo==b.hi||a.hi<=b.lo||b.hi<=a.lo;}
static bool buffers(const std::vector<std::pair<const double*,int>>&in,const std::vector<std::pair<double*,int>>&out){std::vector<Range>i,o;Range r;for(auto a:in){if(!range(a.first,a.second,r))return false;i.push_back(r);}for(auto a:out){if(!range(a.first,a.second,r))return false;o.push_back(r);}for(size_t k=0;k<o.size();++k){for(auto a:i)if(!disjoint(o[k],a))return false;for(size_t j=0;j<k;++j)if(!disjoint(o[k],o[j]))return false;}return true;}
static bool valid(int m){return m>=0&&size_t(m)<definitions.size();}
static std::vector<double>copy(const double*p,int n){return n?std::vector<double>(p,p+n):std::vector<double>();}
extern "C" int controlled_time_size(int m,int f){return valid(m)&&f>=0&&f<6?shapes[m][f]:-1;}
extern "C" int controlled_time_evaluate(int m,const double*z,int ns,const double*p,int np,double time,const double*v,int nc,const double*cr,int nr,int initial,double*rate,int nrate,double*obs,int no,double*scale,int nscale){try{
 if(!valid(m)||ns!=shapes[m][0]||np!=shapes[m][1]||nc!=shapes[m][2]||nr!=nc||no!=shapes[m][3]||nrate!=ns||nscale!=ns||(initial!=0&&initial!=1)||!buffers({{z,ns},{p,np},{v,nc},{cr,nr}},{{rate,nrate},{obs,no},{scale,nscale}}))return 0;
 Context parent{copy(z,ns),time,copy(v,nc),copy(cr,nr),copy(p,np)};std::vector<double>r,o,s;if(!evaluate(definitions[m],parent,initial,r,o,s)||o.size()!=size_t(no))return 0;
 std::copy(r.begin(),r.end(),rate);std::copy(o.begin(),o.end(),obs);std::copy(s.begin(),s.end(),scale);return 1;
 }catch(...){return 0;}}
extern "C" int controlled_time_advance(int m,const double*z,int ns,const double*p,int np,double time,double duration,const double*v,int nc,const double*cr,int nr,const double*start,int nstart,const double*end,int nend,const double*settings,int nsettings,double*out,int nout,double*outtime,int ntime,double*outv,int nv,double*outr,int nout_rates,double*obs,int no,double*diag,int nd){try{
 if(!valid(m)||ns!=shapes[m][0]||np!=shapes[m][1]||nc!=shapes[m][2]||nr!=nc||nstart!=nc||nend!=nc||nsettings!=6||nout!=ns||ntime!=1||nv!=nc||nout_rates!=nc||no!=shapes[m][3]||nd!=4||!buffers({{z,ns},{p,np},{v,nc},{cr,nr},{start,nstart},{end,nend},{settings,nsettings}},{{out,nout},{outtime,ntime},{outv,nv},{outr,nout_rates},{obs,no},{diag,nd}}))return 0;
 for(int i=0;i<6;++i)if(!std::isfinite(settings[i]))return 0;if(settings[4]!=std::floor(settings[4])||settings[4]<1||settings[4]>60||settings[5]!=std::floor(settings[5])||settings[5]<1||settings[5]>1000000)return 0;
 Settings s{settings[0],settings[1],settings[2],settings[3],int(settings[4]),int(settings[5])};Context parent{copy(z,ns),time,copy(v,nc),copy(cr,nr),copy(p,np)},result;std::vector<double>o;Diagnostics d;
 if(!advance(definitions[m],parent,duration,copy(start,nstart),copy(end,nend),s,result,o,d)||o.size()!=size_t(no))return 0;
 std::copy(result.state.begin(),result.state.end(),out);*outtime=result.time;std::copy(result.controls.begin(),result.controls.end(),outv);std::copy(result.rates.begin(),result.rates.end(),outr);std::copy(o.begin(),o.end(),obs);diag[0]=d.trials;diag[1]=d.accepted;diag[2]=d.rejected;diag[3]=d.error;return 1;
 }catch(...){return 0;}}
