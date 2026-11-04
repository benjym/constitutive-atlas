#include "atlas/solver.hpp"
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
namespace atlas {
void number(double x){if(std::isfinite(x))std::cout<<x;else std::cout<<"null";}
void trace_advance(const char*kind,int it,double lateral,const Advance&a){
 std::cout<<"{\"kind\":\""<<kind<<"\",\"iteration\":"<<it<<",\"lateral\":";number(lateral);
 std::cout<<",\"ok\":"<<a.ok<<",\"finite_state\":"<<finite(a.state)<<",\"substeps\":"<<a.diagnostics.substeps<<",\"rejected\":"<<a.diagnostics.rejected<<",\"fractions\":"<<a.diagnostics.increment_fractions.size()<<",\"accepted_increments\":"<<a.diagnostics.accepted_increments.size()<<",\"partition_retries\":"<<a.diagnostics.partition_retries<<"}\n";
}
void trace_residual(int it,double residual){std::cout<<"{\"kind\":\"residual\",\"iteration\":"<<it<<",\"residual\":";number(residual);std::cout<<"}\n";}
void trace_derivative(int it,const ControlDerivative&d,const Advance&base){
 bool previous=false;double previous_slope=0;
 for(size_t k=0;k<d.probes.size();++k){const auto&p=d.probes[k];const bool valid=p.comparable&&p.finite_slope;
 const bool stable=valid&&previous&&std::abs(p.slope-previous_slope)<=1e-3*std::max(1.,std::max(std::abs(p.slope),std::abs(previous_slope)));
 std::cout<<"{\"kind\":\"probe\",\"iteration\":"<<it<<",\"probe\":"<<k<<",\"h\":";number(p.h);std::cout<<",\"slope\":";number(p.slope);
 std::cout<<",\"representable\":"<<p.representable<<",\"comparable\":"<<p.comparable<<",\"finite_slope\":"<<p.finite_slope<<",\"stable\":"<<stable<<",\"probe_ok\":"<<p.advance.ok<<",\"probe_finite_state\":"<<finite(p.advance.state)<<",\"base_substeps\":"<<base.diagnostics.substeps<<",\"probe_substeps\":"<<p.advance.diagnostics.substeps<<",\"base_fractions\":"<<base.diagnostics.increment_fractions.size()<<",\"probe_fractions\":"<<p.advance.diagnostics.increment_fractions.size()<<",\"base_accepted_increments\":"<<base.diagnostics.accepted_increments.size()<<",\"probe_accepted_increments\":"<<p.advance.diagnostics.accepted_increments.size()<<",\"base_partition_retries\":"<<base.diagnostics.partition_retries<<",\"probe_partition_retries\":"<<p.advance.diagnostics.partition_retries<<"}\n";
 previous=valid;if(valid)previous_slope=p.slope;
 }
 std::cout<<"{\"kind\":\"derivative\",\"iteration\":"<<it<<",\"ok\":"<<d.ok<<",\"h\":";number(d.h);std::cout<<",\"value\":";number(d.value);std::cout<<"}\n";
}
void trace_line_search(int it,double alpha,const Advance&a){trace_advance("line_search",it,alpha,a);}
#include "logged-controlled-step.inc"
}
int main(int argc,char**argv){
 try{
  if(argc!=2)throw std::runtime_error("case wire path required");std::ifstream in(argv[1]);if(!in)throw std::runtime_error("case wire missing");
  std::string version,id;in>>version>>id;if(version!="ATLAS-DERIVATIVE-TRACE-1"||id!="hypoplastic-sand-igs97")throw std::runtime_error("case identity");
  auto value=[&](){std::string s;in>>s;if(s.size()!=16||s.find_first_not_of("0123456789abcdef")!=std::string::npos)throw std::runtime_error("invalid binary64 wire");double v=std::bit_cast<double>(std::stoull(s,nullptr,16));if(!std::isfinite(v))throw std::runtime_error("nonfinite input");return v;};
  size_t n;in>>n;if(n!=13)throw std::runtime_error("state size");atlas::State state(n);for(auto&v:state)v=value();in>>n;if(n!=14)throw std::runtime_error("parameters size");atlas::State parameters(n);for(auto&v:parameters)v=value();
  double axial=value(),reference=value(),current_axial=value();atlas::IntegrationSettings settings;settings.residual_tolerance=value();settings.rate_tolerance=value();in>>settings.max_iterations>>settings.max_depth>>settings.max_substeps>>settings.max_backtracks;if(!in||!atlas::valid_settings(settings))throw std::runtime_error("invalid settings");std::string extra;if(in>>extra)throw std::runtime_error("trailing case input");
  int model=-1;for(size_t i=0;i<atlas::models().size();++i)if(atlas::models()[i].id==id)model=int(i);if(model<0||!atlas::models()[model].rate)throw std::runtime_error("exact rate model absent");
  std::cout<<std::boolalpha<<std::setprecision(17);atlas::Sym<double>de;atlas::Advance result;
  const bool ok=atlas::logged_controlled_step(model,state,parameters,1,axial,reference,current_axial,de,result,settings);
  std::cout<<"{\"kind\":\"completion\",\"controller_ok\":"<<ok<<",\"step\":93,\"parent_retained\":true}\n";
  return 0; // A completed diagnostic may report the genuine controller failure.
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
}
