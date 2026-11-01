#include "atlas/solver.hpp"
#include <iostream>
using namespace atlas;
int main(){int checks=0,failures=0;auto check=[&](bool ok){++checks;if(!ok)++failures;};int m=-1;for(int i=0;i<int(models().size());++i)if(models()[i].id=="lade-duncan-1975-midpoint-elastic-eq19-gap-v4")m=i;if(m<0)return 2;
 auto p=default_parameters(m);State parent{60000,60000,60000,0,0,0,13,0},original=parent;IntegrationSettings settings;settings.residual_tolerance=2e-10;settings.increment_tolerance=1e-7;settings.positive_stress_metric=true;settings.max_iterations=45;settings.max_depth=20;settings.max_substeps=200000;settings.max_backtracks=11;
 Sym<double>de;for(int j=0;j<3;++j)de.v[j]=-.0001;
 auto result=integrate(m,parent,de,p,settings);check(result.ok);check(parent==original);check(result.diagnostics.hierarchical_seed_trials>0);check(result.diagnostics.hierarchical_seed_acceptances>0);check(result.diagnostics.hierarchical_seed_acceptances<=result.diagnostics.hierarchical_seed_trials);check(result.diagnostics.reserved_path_trials<=3*settings.max_substeps);
 const double expected=p[0]*std::pow(std::pow(60000/p[0],1-p[8])-(1-p[8])*p[7]*.0001,1/(1-p[8]));
 // Parameter order is independently frozen in model.json: pa,k1,ft,A,rf,M,l,Kur,n,nu.
 if(result.ok){for(int j=0;j<3;++j)check(std::abs(result.state[j]-expected)/expected<1e-4);check(result.state[6]==13&&result.state[7]==0);}
 Sym<double>small;small.v[0]=1e-10;State ordinary;Diagnostics plain;check(advance_recursive(m,parent,small,p,ordinary,plain,0,settings));
 for(int kind=0;kind<3;++kind){State seed=parent;if(kind==0)seed.pop_back();if(kind==1)seed[0]=std::numeric_limits<double>::quiet_NaN();if(kind==2)seed[7]=1e100;const State saved=seed;State actual;Diagnostics d;
  check(advance_recursive(m,parent,small,p,actual,d,0,settings,&seed));check(actual==ordinary);check(d.hierarchical_seed_trials==1&&d.hierarchical_seed_acceptances==0);check(parent==original);if(kind!=1)check(seed==saved);else check(std::isnan(seed[0])&&seed.size()==8&&seed[7]==saved[7]);
 }
 // Exact raw alias hold, no hierarchical trial necessary.
 State alias=parent;alias[6]=-1;auto hold=integrate(m,alias,Sym<double>{},p,settings);check(hold.ok&&hold.state==alias&&hold.diagnostics.hierarchical_seed_trials==0);
 auto disabled=settings;disabled.increment_tolerance=0.;auto old=integrate(m,parent,small,p,disabled);State direct;Diagnostics cold;check(implicit_step(m,parent,small,p,direct,cold,disabled));check(old.ok&&old.state==direct&&old.diagnostics.hierarchical_seed_trials==0);
 // Failed macro and exhausted resource requests do not commit guesses/history.
 auto exhausted=settings;exhausted.max_depth=0;auto failed=integrate(m,parent,de,p,exhausted);check(!failed.ok&&failed.state==parent&&failed.diagnostics.substeps==0);
 auto short_newton=settings;short_newton.max_iterations=1;short_newton.max_depth=2;auto partial=integrate(m,parent,de,p,short_newton);check(!partial.ok&&partial.state==parent&&partial.diagnostics.hierarchical_seed_trials==0);
 auto recovery=integrate(m,partial.state,small,p,settings),fresh=integrate(m,parent,small,p,settings);check(recovery.ok&&fresh.ok&&recovery.state==fresh.state);check(derivative_work_columns()==38);
 std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"hierarchical_trials\":"<<result.diagnostics.hierarchical_seed_trials<<",\"hierarchical_acceptances\":"<<result.diagnostics.hierarchical_seed_acceptances<<",\"passed\":"<<(failures?"false":"true")<<"}\n";return failures?1:0;
}
