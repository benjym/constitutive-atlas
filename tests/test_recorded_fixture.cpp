// Synthetic committed-parent memory fixture, separate from public materials.
#include "atlas/recorded.hpp"
#include <iostream>
#include <stdexcept>
using namespace atlas;
int checks=0;
void require(bool value,const char* label){++checks;if(!value)throw std::runtime_error(label);}
int index(const std::string& name){for(size_t i=0;i<models().size();++i)if(models()[i].id==name)return int(i);throw std::runtime_error("missing fixture");}
RecordedPath path(bool stress){
 RecordedPath p;for(int j=0;j<6;++j){p.controls[j].stress=stress;p.controls[j].coefficients.v[j]=1.;}
 const double axial[]={0.,.01,-.02,-.02,.005};
 for(int k=0;k<5;++k){RecordedKnot knot;knot.coordinate=k;
  for(int j=0;j<6;++j)knot.targets[j]=stress?(j<3?100.:0.):0.;
  knot.targets[0]+=axial[k]*(stress?1000.:1.);p.knots.push_back(knot);}
 return p;
}
void restart_cases(){
 int m=index("test-recorded-plateau");const auto z=initial_state(m),p=default_parameters(m);
 RecordedPath path;for(int j=0;j<6;++j){path.controls[j].coefficients.v[j]=1.;path.controls[j].stress=j==1||j==2;}
 RecordedKnot a,b;a.targets={0,100,100,0,0,0};b.coordinate=1;b.targets={.001,101,101,0,0,0};path.knots={a,b};
 auto disabled=replay_recorded(m,z,p,path);
 require(!disabled.ok&&disabled.failed_knot==1&&disabled.material_trials==1,"plateau fixture not singular");
 require(disabled.restart_searches==0&&disabled.restart_trials==0,"disabled restart executed");
 RecordedSettings s;s.max_restarts=1;s.restart_step=.0015;s.restart_levels=1;
 auto run=replay_recorded(m,z,p,path,s);
 require(run.ok&&run.accepted_restarts==1&&run.restart_searches==1&&run.restart_trials==6,"bounded restart failed/accounting");
 require(std::abs(run.strain.v[1]-.002)<1e-12&&run.strain.v[1]==run.strain.v[2],"restart symmetry/root wrong");
 require(std::abs(run.state[6]-9e-6)<1e-12,"discarded restart trials leaked persistent memory");
 auto direct=integrate(m,z,run.strain,p);
 require(direct.ok&&direct.state==run.state,"restart result differs from immutable-parent replay");
 auto small=s;small.restart_step=.0001;
 auto failed=replay_recorded(m,z,p,path,small);
 require(!failed.ok&&failed.restart_trials==6&&failed.accepted_restarts==0&&failed.state==z,"failed bounded search changed state");
 auto budget=s;budget.max_material_trials=2;
 auto capped=replay_recorded(m,z,p,path,budget);
 require(!capped.ok&&capped.material_trials==2&&capped.restart_trials==1&&capped.state==z,"restart budget/rollback wrong");
 // A converged candidate on the last allowed trial/iteration must be accepted.
 auto exact=s;exact.restart_step=.002;exact.max_iterations=1;exact.max_material_trials=2;
 auto immediate=replay_recorded(m,z,p,path,exact);
 require(immediate.ok&&immediate.material_trials==2&&immediate.restart_trials==1,"converged restart unnecessarily re-evaluated");
 // Oblique prescribed strain: dx+2dy=.001. The normalized combined free
 // directions have different normalizations; an improving candidate must
 // still remain feasible before a subsequent Newton correction.
 auto oblique=path;oblique.controls[0].coefficients.v[1]=2.;auto oblique_settings=s;oblique_settings.restart_step=.0025;
 auto feasible=replay_recorded(m,z,p,oblique,oblique_settings);
 require(feasible.ok&&std::abs(feasible.strain.v[0]+2*feasible.strain.v[1]-.001)<1e-14,"restart left prescribed-strain nullspace");
 require(std::abs(feasible.state[6]-17e-6)<1e-12,"oblique candidate history incorrect");
 auto permuted=path;std::swap(permuted.controls[0],permuted.controls[2]);
 for(auto& knot:permuted.knots)std::swap(knot.targets[0],knot.targets[2]);
 for(auto& x:permuted.controls[2].coefficients.v)x*=-1e4;
 for(auto& knot:permuted.knots)knot.targets[2]*=-1e4;
 auto transformed=replay_recorded(m,z,p,permuted,s);
 require(transformed.ok&&transformed.state==run.state&&transformed.strain.v==run.strain.v,"row permutation/scaling changed restart solution");
 auto late=path;auto c=b;c.coordinate=2;c.targets={.002,100,100,0,0,0};late.knots.push_back(c);
 auto prefix=replay_recorded(m,z,p,late,s);
 require(!prefix.ok&&prefix.failed_knot==2&&prefix.points.size()==2&&prefix.state==run.state&&prefix.strain.v==run.strain.v,"late restart failure lost committed prefix");
 auto repeat=replay_recorded(m,z,p,path,s);
 require(repeat.ok&&repeat.state==run.state&&repeat.material_trials==run.material_trials,"restart not deterministic");
}
int main(){try{
 restart_cases();
 int model=index("test-parent-reset");auto p=default_parameters(model),z=initial_state(model);
 for(bool stress:{false,true}){
  const auto specification=path(stress);auto result=replay_recorded(model,z,p,specification);
  require(result.ok,"memory fixture replay failed");require(result.points.size()==5,"memory point count");
  auto parent=z;double strain=0;
  for(int k=1;k<5;++k){
   double target=stress?(specification.knots[k].targets[0]-100.)/1000.:specification.knots[k].targets[0];
   if(k!=3){Sym<double> increment;increment.v[0]=target-strain;
    auto direct=integrate(model,parent,increment,p);require(direct.ok,"direct memory update failed");parent=direct.state;}
   else require(result.points[k].state==result.points[k-1].state&&result.points[k].diagnostics.substeps==0,"duplicate memory mutated");
   for(size_t j=0;j<z.size();++j)require(std::abs(parent[j]-result.points[k].state[j])<=1e-11,"trial reset/history leak");
   // On reversal at k=2 the anchor must equal the old coordinate 1.01.
   if(k==2)require(std::abs(result.points[k].state[7]-1.01)<1e-14,"reset did not use immutable parent");
   strain=target;
  }
  auto again=replay_recorded(model,z,p,specification);require(again.ok&&again.state==result.state,"repeat path changed history");
 }
 // Failure after accepted internal substeps must restore the last complete knot.
 auto failure=path(false);failure.knots.resize(4);
 for(int k=0;k<4;++k)failure.knots[k].targets[0]=k==3?.1:k*.01;
 p[1]=1.025;
 auto result=replay_recorded(model,z,p,failure);
 require(!result.ok&&result.failed_knot==3&&result.points.size()==3,"domain failure prefix wrong");
 auto prefix=failure;prefix.knots.resize(3);auto expected=replay_recorded(model,z,p,prefix);
 require(expected.ok&&result.state==expected.state&&result.strain.v==expected.strain.v,"partial material work leaked");
 long long committed=0;for(const auto& point:result.points)committed+=point.diagnostics.substeps;
 require(result.attempted_substeps>committed,"failure did not exercise accepted internal work");
 require(result.state[7]==0.,"failure leaked pending reversal anchor");
 // A cubic multiplier residual is singular at its converged zero value.
 // The elastic predictor still gives an exact update. Stress inversion must
 // remain available through feasible numerical probes of that update.
 int norm_model=index("test-recorded-singular-multiplier");auto np=default_parameters(norm_model),nz=initial_state(norm_model);
 Sym<double> zero;auto linear=linearize_update(norm_model,nz,zero,np);
 require(linear.advance.ok&&!linear.tangent_ok,"multiplier fixture does not exercise unavailable tangent");
 auto norm_run=replay_recorded(norm_model,nz,np,path(true));
 require(norm_run.ok&&norm_run.finite_difference_probes>=6,"numerical derivative fallback failed");
 require(norm_run.state[6]==0.,"multiplier root changed");
 RecordedSettings budget;budget.max_material_trials=1;
 auto budget_run=replay_recorded(norm_model,nz,np,path(true),budget);
 require(!budget_run.ok&&budget_run.material_trials==1&&budget_run.finite_difference_probes==0,
         "unexecuted derivative probe counted");
 require(budget_run.points.size()==1&&budget_run.state==nz,"probe budget failure leaked state");
 // A physical-time model must not be reinterpreted with a unit path interval.
 int timed=index("test-maxwell");auto timed_initial=initial_state(timed);
 auto unsupported=replay_recorded(timed,timed_initial,default_parameters(timed),path(false));
 require(!unsupported.ok&&unsupported.points.empty()&&unsupported.state==timed_initial,"timed material accepted");
 std::cout<<"{\"ok\":true,\"checks\":"<<checks<<",\"failed_attempt_substeps\":"<<result.attempted_substeps-committed<<",\"fallback_probes\":"<<norm_run.finite_difference_probes<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
