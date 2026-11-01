// Independent analytical tests of the recorded-path driver. No production tangent
// or integrate() call is used to construct an expected state.
#include "atlas/recorded.hpp"
#include <algorithm>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>
using namespace atlas;
namespace {
int checks=0, cases=0;
bool explicit_fixtures=false;
void require(bool value,const std::string& label){++checks;if(!value)throw std::runtime_error(label);}
void close(double a,double b,double absolute,double relative,const std::string& label){
 require(std::isfinite(a)&&std::isfinite(b)&&std::abs(a-b)<=absolute+relative*std::max(std::abs(a),std::abs(b)),label);
}
double contract(const Sym<double>& a,const Sym<double>& b){double x=0;for(int i=0;i<6;++i)x+=a.v[i]*b.v[i];return x;}
Sym<double> stress_for(const State& parent,const Sym<double>& origin,const Sym<double>& strain,double E,double nu){
 const double G=E/(2*(1+nu)),lambda=E*nu/((1+nu)*(1-2*nu));
 double volume=0;for(int i=0;i<3;++i)volume+=strain.v[i]-origin.v[i];
 Sym<double> stress;for(int i=0;i<6;++i)stress.v[i]=parent[i]+2*G*(strain.v[i]-origin.v[i])+(i<3?lambda*volume:0);
 return stress;
}
void targets(RecordedPath& path,const std::vector<Sym<double>>& strains,const State& parent,double E,double nu){
 for(size_t k=0;k<strains.size();++k){auto stress=stress_for(parent,path.initial_strain,strains[k],E,nu);
  for(int j=0;j<6;++j)path.knots[k].targets[j]=contract(path.controls[j].coefficients,path.controls[j].stress?stress:strains[k]);}
}
void check_path(int model,const State& parent,const State& parameters,const RecordedPath& path,const std::vector<Sym<double>>& expected,const std::string& label){
 auto saved=parent;auto run=replay_recorded(model,parent,parameters,path);++cases;
 require(run.ok,label+": "+run.message);require(parent==saved,label+": input mutation");
 require(run.points.size()==expected.size(),label+": point count");
 const double E=30000000.,nu=.25;
 for(size_t k=0;k<expected.size();++k){const auto& point=run.points[k];
  require(point.coordinate==path.knots[k].coordinate,label+": coordinate/order");
  require(point.state.size()==parent.size(),label+": state size");
  auto sigma=stress_for(parent,path.initial_strain,expected[k],E,nu);
  double volume=0;for(int i=0;i<3;++i)volume+=expected[k].v[i]-path.initial_strain.v[i];
  for(int i=0;i<6;++i){close(point.strain.v[i],expected[k].v[i],2e-11,2e-9,label+": strain");close(point.state[i],sigma.v[i],2e-4,2e-9,label+": stress");}
  close(point.state[6],(1+parent[6])*std::exp(-volume)-1,2e-10,2e-10,label+": density closure");
  if(k&&expected[k].v==expected[k-1].v){require(point.state==run.points[k-1].state,label+": duplicate changed state");require(point.strain.v==run.points[k-1].strain.v,label+": duplicate changed strain");require(point.diagnostics.substeps==0,label+": duplicate integrated");}
 }
 require(run.state==run.points.back().state,label+": final state mismatch");require(run.strain.v==run.points.back().strain.v,label+": final strain mismatch");
}
}

void additional_recorded_cases(){
 int elastic=-1;for(size_t i=0;i<models().size();++i)if(models()[i].id=="linear-elastic")elastic=int(i);
 auto parameters=default_parameters(elastic),initial=initial_state(elastic);
 RecordedPath path;for(int j=0;j<6;++j)path.controls[j].coefficients.v[j]=1.;
 for(int k=0;k<4;++k){RecordedKnot knot;knot.coordinate=k;knot.targets[0]=k*.0001;path.knots.push_back(knot);}
 auto reject=[&](RecordedPath bad,RecordedSettings settings=RecordedSettings{}){
  auto result=replay_recorded(elastic,initial,parameters,bad,settings);++cases;
  require(!result.ok&&result.points.empty()&&result.state==initial,"invalid specification accepted or mutated state");
 };
 auto bad=path;bad.knots[1].coordinate=bad.knots[0].coordinate;reject(bad);
 bad=path;bad.knots[2].coordinate=-1.;reject(bad);
 bad=path;bad.knots[1].coordinate=std::numeric_limits<double>::infinity();reject(bad);
 bad=path;bad.knots[1].targets[0]=std::numeric_limits<double>::quiet_NaN();reject(bad);
 bad=path;bad.controls[0].coefficients.v[0]=std::numeric_limits<double>::infinity();reject(bad);
 bad=path;bad.controls[0].coefficients={};reject(bad);
 bad=path;bad.controls[1]=bad.controls[0];reject(bad);
 bad=path;bad.controls[1].coefficients.v={{1.,1e-16,0.,0.,0.,0.}};reject(bad);
 bad=path;bad.knots.resize(1);reject(bad);
 bad=path;bad.knots.resize(5002);reject(bad);
 bad=path;bad.knots[0].targets[0]=.1;reject(bad);
 bad=path;bad.initial_strain.v[0]=std::numeric_limits<double>::quiet_NaN();reject(bad);
 RecordedSettings settings;settings.control_tolerance=0;reject(path,settings);
 settings={};settings.material.rate_tolerance=0;reject(path,settings);
 settings={};settings.max_material_trials=0;reject(path,settings);
 settings={};settings.max_iterations=0;reject(path,settings);
 settings={};settings.max_backtracks=-1;reject(path,settings);
 settings={};settings.finite_difference_step=0;reject(path,settings);
 require(!replay_recorded(-1,initial,parameters,path).ok,"invalid model accepted");
 auto invalid_initial=initial;invalid_initial.pop_back();require(!replay_recorded(elastic,invalid_initial,parameters,path).ok,"wrong state size accepted");
 // A distinct, tiny imposed strain must still execute a material update.
 auto tiny=path;tiny.knots.resize(2);tiny.knots[1].targets[0]=1e-12;
 auto tiny_run=replay_recorded(elastic,initial,parameters,tiny);++cases;
 require(tiny_run.ok&&tiny_run.material_trials==1&&tiny_run.points.back().diagnostics.substeps>0,"distinct tiny strain treated as duplicate");
 require(tiny_run.strain.v[0]==1e-12,"tiny strain suppressed");
 // Trial budgets apply across the entire path, retaining exactly the accepted prefix.
 settings={};settings.max_material_trials=1;
 auto limited=replay_recorded(elastic,initial,parameters,path,settings);++cases;
 require(!limited.ok&&limited.failed_knot==2&&limited.points.size()==2&&limited.material_trials==1,"trial cap or failure prefix wrong");
 require(limited.state==limited.points.back().state&&limited.strain.v==limited.points.back().strain.v,"failed knot leaked state");
 auto prefix=path;prefix.knots.resize(2);auto expected=replay_recorded(elastic,initial,parameters,prefix);
 require(expected.ok&&expected.state==limited.state,"budget failure differs from committed prefix");
 // Extreme but finite row scales must not overflow the norm or its reciprocal.
 auto scaled=path;
 for(int j=0;j<6;++j){double factor=j%2?1e300:1e-300;scaled.controls[j].coefficients.v[j]*=factor;for(auto& knot:scaled.knots)knot.targets[j]*=factor;}
 auto scaled_run=replay_recorded(elastic,initial,parameters,scaled);auto ordinary=replay_recorded(elastic,initial,parameters,path);++cases;
 require(scaled_run.ok&&ordinary.ok,"extreme equation scales rejected");
 for(size_t i=0;i<initial.size();++i)close(scaled_run.state[i],ordinary.state[i],1e-9,1e-12,"row scale changed result");
 // The final permitted Newton correction and final allowed material trial
 // can themselves converge; they do not require a redundant confirmation trial.
 auto one_step=path;one_step.knots.resize(2);
 for(int j=0;j<6;++j){one_step.controls[j].stress=true;one_step.knots[0].targets[j]=initial[j];one_step.knots[1].targets[j]=initial[j]+(j==0?100.:0.);}
 settings={};settings.max_iterations=1;settings.max_material_trials=2;
 auto boundary=replay_recorded(elastic,initial,parameters,one_step,settings);++cases;
 require(boundary.ok&&boundary.material_trials==2,"converged final iteration/trial was discarded");
 // Redundant mixed constraints require a constitutive rank check when solving.
 auto singular=path;singular.controls[1].coefficients=singular.controls[0].coefficients;singular.controls[1].stress=true;
 for(size_t i=0;i<models()[elastic].parameters.size();++i)if(models()[elastic].parameters[i].name=="nu")parameters[i]=0;
 for(size_t k=0;k<singular.knots.size();++k)singular.knots[k].targets[1]=initial[0]+30000000.*singular.knots[k].targets[0]+(k?50.:0.);
 auto singular_run=replay_recorded(elastic,initial,parameters,singular);++cases;
 require(!singular_run.ok&&singular_run.points.size()==1&&singular_run.failed_knot==1,"singular mixed controls accepted");
 // A valid endpoint does not require a nonsingular tangent. This consistent
 // redundant mixed system has a root at the explicit strain particular solution;
 // the solver makes no uniqueness claim and must not reject the valid root.
 for(size_t k=0;k<singular.knots.size();++k)singular.knots[k].targets[1]=initial[0]+30000000.*singular.knots[k].targets[0];
 singular.knots.resize(2);settings={};settings.max_material_trials=1;
 auto valid_root=replay_recorded(elastic,initial,parameters,singular,settings);++cases;
 require(valid_root.ok&&valid_root.material_trials==1,"valid endpoint rejected for singular tangent");
 // Same-parent material replay across all public models: reversals and no-op
 // records must preserve transient/history fields as well as stress.
 for(size_t m=0;m<models().size();++m){
  auto p=default_parameters(int(m)),z=initial_state(int(m));auto cyclic=path;cyclic.knots.clear();
  double amplitude=models()[m].id=="drucker-prager"?.012:models()[m].id=="modified-cam-clay"?.02:.0002;
  const double factors[]={0.,1.,-.6,-.6,.2};
  for(int k=0;k<5;++k){RecordedKnot knot;knot.coordinate=k;knot.targets[0]=factors[k]*amplitude;knot.targets[1]=knot.targets[2]=-.2*knot.targets[0];knot.targets[3]=.15*knot.targets[0];cyclic.knots.push_back(knot);}
  RecordedSettings fixture_settings;
  if(explicit_fixtures&&models()[m].id=="research-hp-extracted-asbs-gis-2024-v03"){
   require(fixture_settings.material.max_depth==14,"original default depth changed; review fixture allocation");
   const auto original=replay_recorded(int(m),z,p,cyclic);++cases;
   require(!original.ok&&original.failed_knot==1&&original.points.size()==1&&original.state==z&&original.strain.v==Sym<double>{}.v&&original.attempted_substeps==0,"original GIS default failure/rollback changed");
   Sym<double> first;first.v=cyclic.knots[1].targets;const auto rejected=integrate(int(m),z,first,p);++cases;
   require(!rejected.ok&&rejected.state==z&&rejected.diagnostics.substeps==0,"original GIS direct rollback changed");
   fixture_settings.material.max_depth=20;
  }
  auto run=replay_recorded(int(m),z,p,cyclic,fixture_settings);++cases;require(run.ok,"nonlinear recorded replay failed: "+models()[m].id+" "+run.message);
  auto continuation=cyclic;continuation.initial_strain=run.points[2].strain;
  continuation.knots.erase(continuation.knots.begin(),continuation.knots.begin()+2);
  auto resumed=replay_recorded(int(m),run.points[2].state,p,continuation,fixture_settings);++cases;
  require(resumed.ok&&resumed.state==run.state&&resumed.strain.v==run.strain.v,"recorded restart differs from uninterrupted path");
  State parent=z;Sym<double> previous;
  for(size_t k=1;k<cyclic.knots.size();++k){
   Sym<double> de;for(int j=0;j<6;++j)de.v[j]=cyclic.knots[k].targets[j]-previous.v[j];
   if(k!=3){auto direct=integrate(int(m),parent,de,p,fixture_settings.material);require(direct.ok,"direct nonlinear replay failed");parent=direct.state;}
   else require(run.points[k].state==run.points[k-1].state&&run.points[k].diagnostics.substeps==0,"duplicate changed nonlinear history");
   const auto scales=model_scales(int(m),p);
   for(size_t j=0;j<parent.size();++j)close(run.points[k].state[j],parent[j],1e-10*scales[j],1e-10,"nonlinear parent replay mismatch");
   for(int j=0;j<6;++j)previous.v[j]=cyclic.knots[k].targets[j];
  }
  // Match existing drained control endpoints using a different outer solver.
  auto drained=path;drained.knots.clear();drained.controls[1].stress=drained.controls[2].stress=true;
  for(int k=0;k<5;++k){RecordedKnot knot;knot.coordinate=k;knot.targets[0]=factors[k]*1e-4;knot.targets[1]=z[1];knot.targets[2]=z[2];drained.knots.push_back(knot);}
  if(explicit_fixtures&&models()[m].id=="original-cam-clay-sw-electronic-log-recovery-v1"){
   const auto original=replay_recorded(int(m),z,p,drained,fixture_settings);++cases;
   require(!original.ok&&original.failed_knot==1&&original.points.size()==1&&original.state==z&&original.strain.v==Sym<double>{}.v&&original.material_trials==1&&original.message=="singular mixed-control system; last committed knot retained","original OCC mixed-control corner failure/rollback changed");
   // Opt in to existing generic feasible-nullspace globalization; source law,
   // targets, tolerance, trial budget and legacy endpoint gates are unchanged.
   fixture_settings.max_restarts=4;
  }
  auto controlled=replay_recorded(int(m),z,p,drained,fixture_settings);++cases;if(!controlled.ok)std::cerr<<std::setprecision(17)<<"failed knot "<<controlled.failed_knot<<" residual "<<controlled.last_control_error<<" trials "<<controlled.material_trials<<" de0 "<<controlled.last_trial_increment.v[0]<<" de1 "<<controlled.last_trial_increment.v[1]<<"\n";require(controlled.ok,"drained replay failed: "+models()[m].id+" "+controlled.message);
  parent=z;double axial=0;
  for(size_t k=1;k<drained.knots.size();++k){
   if(k!=3){Sym<double> de;Advance direct;double next=drained.knots[k].targets[0];
    require(controlled_step(int(m),parent,p,1,next-axial,z[1],axial,de,direct,fixture_settings.material),"legacy drained replay failed");parent=direct.state;axial=next;}
   const auto scales=model_scales(int(m),p);
   for(size_t j=0;j<parent.size();++j)close(controlled.points[k].state[j],parent[j],2e-7*scales[j],2e-7,"drained endpoint mismatch");
  }
 }
}
int main(){try{
 const char* profile=std::getenv("ATLAS_NATIVE_FIXTURES");
 require(!profile||(std::string(profile)=="explicit-gis20-v2"||std::string(profile)=="explicit-gis20-occ-v3"),"unknown native fixture profile");explicit_fixtures=profile!=nullptr;
 std::cout<<(explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")<<"; models="<<models().size()<<'\n';
 int model=-1;for(size_t i=0;i<models().size();++i)if(models()[i].id=="linear-elastic")model=int(i);
 require(model>=0,"linear-elastic absent");auto parameters=default_parameters(model);auto parent=initial_state(model);
 // Anisotropic prestress and a nonzero laboratory strain origin expose hidden
 // zero-origin/preparation assumptions; all shears are Mandel components.
 parent[0]=120000.;parent[1]=90000.;parent[2]=150000.;parent[3]=2000.;parent[4]=-3000.;parent[5]=5000.;
 RecordedPath base;base.initial_strain.v={{.003,-.002,.001,.0004,-.0002,.0003}};
 std::vector<Sym<double>> expected(5,base.initial_strain);
 const double amplitudes[5]={0.,1.,-.7,-.7,.35};
 const double direction[6]={.0008,-.00025,.00015,.0003,-.00017,.00023};
 const double coordinates[5]={3.,3.25,4.5,5.,6.5};
 for(int k=0;k<5;++k){for(int j=0;j<6;++j)expected[k].v[j]+=amplitudes[k]*direction[j];RecordedKnot knot;knot.coordinate=coordinates[k];base.knots.push_back(knot);}
 for(int mode=0;mode<4;++mode){auto path=base;
  for(int j=0;j<6;++j){path.controls[j].stress=mode==1||(mode>=2&&(j%2));path.controls[j].coefficients.v[j]=1.;
   if(mode==3){path.controls[j].coefficients.v[(j+1)%6]=.11;path.controls[j].coefficients.v[(j+3)%6]=-.07;}}
  targets(path,expected,parent,30000000.,.25);std::string label="elastic-mode-"+std::to_string(mode);
  check_path(model,parent,parameters,path,expected,label);
  // Multiplying a row and its targets by a nonzero factor preserves physics.
  auto scaled=path;const double factors[6]={-3.,.1,7.,-.25,2.,.5};
  for(int j=0;j<6;++j){for(auto& x:scaled.controls[j].coefficients.v)x*=factors[j];for(auto& knot:scaled.knots)knot.targets[j]*=factors[j];}
  check_path(model,parent,parameters,scaled,expected,label+"-row-scaled");
  auto permuted=path;const int permutation[6]={5,2,0,4,1,3};for(int j=0;j<6;++j){permuted.controls[j]=path.controls[permutation[j]];for(size_t k=0;k<path.knots.size();++k)permuted.knots[k].targets[j]=path.knots[k].targets[permutation[j]];}
  check_path(model,parent,parameters,permuted,expected,label+"-row-permuted");
  // The independent coordinate is an ordering device, not elapsed physical time.
  auto reparameterized=path;const double other[5]={-8.,-7.999,-2.,19.,1000.};for(int k=0;k<5;++k)reparameterized.knots[k].coordinate=other[k];
  check_path(model,parent,parameters,reparameterized,expected,label+"-reparameterized");
 }
 // Six controls in invariant and shear directions: prescribed volume strain,
 // two orthonormal deviatoric normal stresses, and three Mandel shear stresses.
 auto invariant=base;invariant.controls[0].coefficients.v={{1.,1.,1.,0.,0.,0.}};
 const double s6=std::sqrt(6.),s2=std::sqrt(2.);
 invariant.controls[1].stress=true;invariant.controls[1].coefficients.v={{2/s6,-1/s6,-1/s6,0.,0.,0.}};
 invariant.controls[2].stress=true;invariant.controls[2].coefficients.v={{0.,1/s2,-1/s2,0.,0.,0.}};
 for(int j=3;j<6;++j){invariant.controls[j].stress=true;invariant.controls[j].coefficients.v[j]=1.;}
 targets(invariant,expected,parent,30000000.,.25);check_path(model,parent,parameters,invariant,expected,"invariant-mixed-controls");
 additional_recorded_cases();
 std::cout<<"{\"ok\":true,\"cases\":"<<cases<<",\"checks\":"<<checks<<"}\n";return 0;
 }catch(const std::exception& error){std::cerr<<error.what()<<"\n";return 1;}}
