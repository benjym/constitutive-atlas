#include "atlas/solver.hpp"
#include <bit>
#include <iostream>
#include <thread>
#include <functional>
using namespace atlas;
bool same(double a,double b){return std::bit_cast<unsigned long long>(a)==std::bit_cast<unsigned long long>(b);}
bool same(const Jet&a,const Jet&b){if(!same(a.v,b.v))return false;for(int i=0;i<38;++i)if(!same(a.d[i],b.d[i]))return false;return true;}
int main(){int checks=0,failures=0;auto check=[&](bool ok){++checks;if(!ok)++failures;};
 check(derivative_work_columns()==38);
 for(int active:{1,2,8,16,32,37})for(double primal:{-2.,-1.,-0.,0.,1e-320,.5,2.,1e300})for(double tail:{0.,-0.,.25,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
  Jet a(primal),b(1.25);for(int j=0;j<38;++j){a.d[j]=j<active?(j%2?.125:-.25):tail;b.d[j]=j<active?.25:tail;}
  std::vector<std::function<Jet()>>ops{[&]{return a+b;},[&]{return a-b;},[&]{return -a;},[&]{return a*b;},[&]{return a/b;},[&]{return asqrt(a);},[&]{return aexp(a);},[&]{return alog(a);},[&]{return asin(a);},[&]{return acos(a);},[&]{return aabs(a);},[&]{return apow(a,b);},[&]{return unary(a,2.,std::numeric_limits<double>::infinity());}};
  for(auto&op:ops){Jet full=op(),shortened;{DerivativeTailScope scope(active+1);shortened=op();}check(same(full,shortened));check(finite_value(full)==finite_value(shortened));}
  Jet full(91),shortened(91);bool f=scalar_log1p_checked(a,full),s;{DerivativeTailScope scope(active+1);s=scalar_log1p_checked(a,shortened);}check(f==s&&same(full,shortened));
  Sym<Jet> tensor=make_sym(a,b,Jet(3.),Jet(.1),Jet(.2),Jet(.05));
  f=trace_accuracy::trace_checked(tensor,full);{DerivativeTailScope scope(active+1);s=trace_accuracy::trace_checked(tensor,shortened);}check(f==s&&same(full,shortened));
  for(auto op:{spectral_candidate::Operation::max,spectral_candidate::Operation::min,spectral_candidate::Operation::upper_sum,spectral_candidate::Operation::min_value}){
   full=Jet(91);shortened=Jet(91);spectral_candidate::Diagnostic df,ds;
   f=spectral_candidate::scalar_checked(tensor,op,full,df);{DerivativeTailScope scope(active+1);s=spectral_candidate::scalar_checked(tensor,op,shortened,ds);}check(f==s&&df.status==ds.status&&same(full,shortened));
  }
  Sym<Jet> pf,ps;for(auto&v:pf.v)v=Jet(91);ps=pf;spectral_candidate::Diagnostic df,ds;
  f=spectral_candidate::projector_checked(tensor,spectral_candidate::Operation::projector_min,pf,df);{DerivativeTailScope scope(active+1);s=spectral_candidate::projector_checked(tensor,spectral_candidate::Operation::projector_min,ps,ds);}check(f==s&&df.status==ds.status);for(int j=0;j<6;++j)check(same(pf.v[j],ps.v[j]));
 }
 // Independent full-storage finiteness oracle for certified uniform tails.
 for(int active:{1,8,16,32,37})for(double tail:{0.,-0.,.25,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})for(bool bad_active:{false,true}){
  Jet a(1);for(int j=active;j<38;++j)a.d[j]=tail;if(bad_active)a.d[0]=std::numeric_limits<double>::quiet_NaN();
  const bool oracle=std::isfinite(a.v)&&std::all_of(a.d.begin(),a.d.end(),[](double v){return std::isfinite(v);});
  {DerivativeTailScope scope(active+1);check(finite_value(a)==oracle);}
 }
 // Ordinary external arbitrary/nonuniform high lanes retain full-width rejection.
 for(int lane=0;lane<38;++lane)for(double bad:{std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
  Jet a(1);a.d[lane]=bad;check(derivative_work_columns()==38&&!finite_value(a));Sym<Jet>tensor=identity<Jet>();tensor.v[5]=a;check(!finite_value(tensor));
  Jet out(91);check(!trace_accuracy::trace_checked(tensor,out)&&same(out,Jet(91)));
  spectral_candidate::Diagnostic diagnostic;check(!spectral_candidate::scalar_checked(tensor,spectral_candidate::Operation::min,out,diagnostic)&&same(out,Jet(91)));
 }
 // Entire model residual/Jacobian, valid/tiny/non-SPD/history/plastic/invalid states.
 for(int m=0;m<int(models().size());++m){const auto p=default_parameters(m);const auto scales=model_scales(m,p);auto initial=initial_state(m);const int n=int(initial.size());check(n<=32);
  for(double scale:{0.,1e-200,1e-24,1.,2.,5.,1e100})for(double increment:{0.,1e-6,-.01}){
   State state=initial;for(int j=0;j<3;++j)state[j]=60000*scale;state[0]*=2;std::vector<Jet>x(n),xn(n),full,shortened;Sym<Jet>de;de.v[0]=Jet(increment);
   for(int j=0;j<n;++j){x[j]=Jet(state[j]);x[j].d[j]=scales[j];xn[j]=Jet(initial[j]);}
   bool f=evaluate_model(m,x,xn,de,p,full),s;{DerivativeTailScope scope(n+1);s=evaluate_model(m,x,xn,de,p,shortened);}check(f==s&&full.size()==shortened.size());if(full.size()==shortened.size())for(size_t j=0;j<full.size();++j)check(same(full[j],shortened[j]));
  }
 }
 // Finite ties explicitly exercise checked singular spectral transactions.
 for(auto diagonal:{State{1,1,1},State{2,1,1},State{2,2,1},State{3,2,1},State{0,0,0}}){
  Sym<Jet>a;for(int k=0;k<3;++k){a.v[k]=Jet(diagonal[k]);a.v[k].d[k]=1;}
  for(auto op:{spectral_candidate::Operation::max,spectral_candidate::Operation::min,spectral_candidate::Operation::upper_sum,spectral_candidate::Operation::lower_sum}){
   Jet full(91),shortened(91);spectral_candidate::Diagnostic df,ds;bool f=spectral_candidate::scalar_checked(a,op,full,df),r;
   {DerivativeTailScope scope(9);r=spectral_candidate::scalar_checked(a,op,shortened,ds);}check(f==r&&df.status==ds.status&&same(full,shortened));
  }
  for(auto op:{spectral_candidate::Operation::projector_max,spectral_candidate::Operation::projector_min}){
   Sym<Jet>full,shortened;for(auto&x:full.v)x=Jet(91);shortened=full;spectral_candidate::Diagnostic df,ds;bool f=spectral_candidate::projector_checked(a,op,full,df),r;
   {DerivativeTailScope scope(9);r=spectral_candidate::projector_checked(a,op,shortened,ds);}check(f==r&&df.status==ds.status);for(int k=0;k<6;++k)check(same(full.v[k],shortened.v[k]));
  }
 }
 // Rotated nonaxisymmetric full candidate residual/Jacobian: plastic/unload/tiny.
 auto rotate=[](State state){
  const double c=std::cos(.37),s=std::sin(.37),d=std::cos(.61),t=std::sin(.61),r=std::sqrt(2.);
  double Q[3][3]={{c,-s*d,s*t},{s,c*d,-c*t},{0,t,d}};
  double a[3][3]={{state[0],state[3]/r,state[5]/r},{state[3]/r,state[1],state[4]/r},{state[5]/r,state[4]/r,state[2]}},b[3][3]{};
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)for(int k=0;k<3;++k)for(int l=0;l<3;++l)b[i][j]+=Q[i][k]*a[k][l]*Q[j][l];
  state[0]=b[0][0];state[1]=b[1][1];state[2]=b[2][2];state[3]=r*b[0][1];state[4]=r*b[1][2];state[5]=r*b[0][2];return state;
 };
 for(int m=0;m<int(models().size());++m)if(models()[m].id=="lade-duncan-1975-midpoint-elastic-eq19-gap-v4"){
  auto p=default_parameters(m);auto scales=model_scales(m,p);
  for(double factor:{1.,1e-24})for(bool unload:{false,true}){
   State current{300000*factor,90000*factor,60000*factor,0,0,0,0,10*factor},previous{60000*factor,60000*factor,60000*factor,0,0,0,13,0};
   if(unload){previous=current;current[0]=120000*factor;current[6]=13;}
   current=rotate(current);previous=rotate(previous);State strain=rotate(State{unload?-.002:.002,-.0004,-.0004,.0001,.00002,-.0001});
   std::vector<Jet>x(8),xn(8),full,shortened;Sym<Jet>de;for(int j=0;j<8;++j){x[j]=Jet(current[j]);x[j].d[j]=scales[j];xn[j]=Jet(previous[j]);}for(int j=0;j<6;++j)de.v[j]=Jet(strain[j]);
   bool f=evaluate_model(m,x,xn,de,p,full),r;{DerivativeTailScope scope(9);r=evaluate_model(m,x,xn,de,p,shortened);}check(f==r&&full.size()==shortened.size());if(full.size()==shortened.size())for(size_t j=0;j<full.size();++j)check(same(full[j],shortened[j]));
  }
 }
 // Checked helpers retain output sentinels and reject nonfinite representative tails.
 for(double bad:{std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
  Sym<Jet>a=identity<Jet>();for(int j=8;j<38;++j)a.v[0].d[j]=bad;Jet full(91),shortened(91);bool f=trace_accuracy::trace_checked(a,full),s;{DerivativeTailScope scope(9);s=trace_accuracy::trace_checked(a,shortened);}check(!f&&!s&&same(full,shortened));
  spectral_candidate::Diagnostic df,ds;f=spectral_candidate::scalar_checked(a,spectral_candidate::Operation::min,full,df);{DerivativeTailScope scope(9);s=spectral_candidate::scalar_checked(a,spectral_candidate::Operation::min,shortened,ds);}check(!f&&!s&&df.status==ds.status&&same(full,shortened));
 }
 {DerivativeTailScope outer(9);check(derivative_work_columns()==9);{DerivativeTailScope inner(4);check(derivative_work_columns()==4);}check(derivative_work_columns()==9);
  try{DerivativeTailScope inner(2);throw 1;}catch(int){}check(derivative_work_columns()==9);
  try{DerivativeTailScope bad(0);check(false);}catch(const std::invalid_argument&){}check(derivative_work_columns()==9);
  bool isolated=false;std::thread thread([&]{isolated=derivative_work_columns()==38;DerivativeTailScope s(3);isolated=isolated&&derivative_work_columns()==3;});thread.join();check(isolated&&derivative_work_columns()==9);
  auto early=[](){DerivativeTailScope inner(2);return derivative_work_columns();};check(early()==2&&derivative_work_columns()==9);
 }
 check(derivative_work_columns()==38);
 std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"passed\":"<<(failures?"false":"true")<<"}\n";return failures?1:0;
}
