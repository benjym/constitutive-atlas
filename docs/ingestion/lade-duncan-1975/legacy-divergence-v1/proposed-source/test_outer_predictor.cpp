#include "atlas/solver.hpp"
#include <iostream>
using namespace atlas;
bool same_diag(const Diagnostics&a,const Diagnostics&b){return a.hierarchical_seed_trials==b.hierarchical_seed_trials&&a.hierarchical_seed_acceptances==b.hierarchical_seed_acceptances&&a.path_seed_value_evaluations==b.path_seed_value_evaluations&&a.path_seed_acceptances==b.path_seed_acceptances&&a.reserved_path_trials==b.reserved_path_trials&&a.iterations==b.iterations&&a.substeps==b.substeps&&a.rejected==b.rejected&&outer_same_bits(a.error,b.error)&&outer_same_state(a.increment_fractions,b.increment_fractions);}
bool same_advance(const Advance&a,const Advance&b){return a.ok==b.ok&&outer_same_state(a.state,b.state)&&same_diag(a.diagnostics,b.diagnostics)&&a.message==b.message&&outer_same_settings(a.settings,b.settings);}
bool same_sym(const Sym<double>&a,const Sym<double>&b){for(int i=0;i<6;++i)if(!outer_same_bits(a.v[i],b.v[i]))return false;return true;}
int main(){int checks=0,failures=0,seeded=0,coldwork=0,warmwork=0;auto check=[&](bool v){++checks;if(!v)++failures;};int m=-1;for(int i=0;i<int(models().size());++i)if(models()[i].id=="lade-duncan-1975-midpoint-elastic-eq19-gap-v4")m=i;if(m<0)return 2;
 auto p=default_parameters(m);State parent{60000,60000,60000,0,0,0,13,0};IntegrationSettings s;s.increment_tolerance=1e-7;s.positive_stress_metric=true;s.max_depth=20;s.max_substeps=200000;Sym<double>prior;prior.v[0]=1e-5;prior.v[1]=prior.v[2]=-2e-6;double lateral=42;
 check(previous_lateral_guess(2e-5,&prior,lateral)&&outer_same_bits(lateral,-4e-6));check(prior.v[0]==1e-5);check(!previous_lateral_guess(1e-5,nullptr,lateral));
 for(int kind=0;kind<14;++kind){auto q=prior;double axial=1e-5;double sentinel=42;
  if(kind==0)axial=0.;if(kind==1)axial=-1e-5;if(kind==2)q.v[0]=0.;if(kind==3)q.v[2]=std::nextafter(q.v[2],1.);if(kind==4)q.v[3]=1e-8;if(kind==5)q.v[0]=1e-320;if(kind==6){axial=1;q.v[1]=q.v[2]=1e308;}if(kind==7)axial=std::numeric_limits<double>::infinity();if(kind>=8)q.v[kind-8]=std::numeric_limits<double>::quiet_NaN();
  check(!previous_lateral_guess(axial,&q,sentinel)&&sentinel==42);
 }
 // Actual sequential commits; cold and warm solve identical current parent.
 State current=parent;bool have=false;Sym<double>previous;
 for(int i=0;i<16;++i){double axial=.002/16;Sym<double>a,b;Advance cold,warm;OuterReuseCounts c,w;const auto saved=current;
  bool ca=controlled_step(m,current,p,1,axial,60000,0,a,cold,s,true,&c,nullptr,false);bool wa=controlled_step(m,current,p,1,axial,60000,0,b,warm,s,true,&w,have?&previous:nullptr,true);check(ca&&wa);check(current==saved);check(w.executed<=390&&w.outer_iterations<=30);check(w.failed_seed_trials==0);
  if(ca&&wa){double error=0;for(int j=0;j<8;++j)error=std::max(error,std::abs(cold.state[j]-warm.state[j])/(j<6||j==7?p[0]:p[2]));check(error<=1e-8);for(int j=0;j<6;++j)check(std::abs(a.v[j]-b.v[j])<=1e-10);current=warm.state;previous=b;have=true;}seeded+=w.seeded_trials;coldwork+=c.executed;warmwork+=w.executed;
 }
 check(seeded==15&&warmwork<coldwork);
 // Initial failed proposal spends an outer iteration before cold recovery.
 auto t=s;t.max_depth=0;Sym<double>bad;bad.v[0]=1e-12;bad.v[1]=bad.v[2]=-1e8;Sym<double>a,b;Advance cold,warm;OuterReuseCounts c,w;
 bool ca=controlled_step(m,parent,p,1,1e-12,60000,0,a,cold,t,true,&c,nullptr,false);bool wa=controlled_step(m,parent,p,1,1e-12,60000,0,b,warm,t,true,&w,&bad,true);
 check(ca&&wa&&same_advance(cold,warm)&&same_sym(a,b));check(w.seeded_trials==1&&w.failed_seed_trials==1);check(w.outer_iterations==c.outer_iterations+1&&w.executed==c.executed+1);check(parent==State({60000,60000,60000,0,0,0,13,0}));
 // Disabled/rate protocol, hold/reversal do not admit the predictor.
 for(double axial:{0.,-1e-12}){OuterReuseCounts d;Advance r;Sym<double>de;controlled_step(m,parent,p,1,axial,60000,0,de,r,s,true,&d,&prior,true);check(d.seeded_trials==0);}
 auto disabled=s;disabled.increment_tolerance=0;disabled.positive_stress_metric=false;OuterReuseCounts d;Advance r;Sym<double>de;controlled_step(m,parent,p,1,1e-6,60000,0,de,r,disabled,true,&d,&prior,true);check(d.seeded_trials==0);
 for(int protocol:{0,2,3,4}){OuterReuseCounts d;Advance r;Sym<double>de;controlled_step(m,parent,p,protocol,protocol==3?100.:1e-6,60000,0,de,r,s,true,&d,&prior,true);check(d.seeded_trials==0);}
 // Cyclic/hold histories retain deterministic cache on/off full results under SAME predictor.
 State controls{0,.0001,.0002,.0002,.0001,0,-.0001};auto runA=run_protocol_impl(m,parent,p,1,0,6,0,s,&controls,LaboratoryRange::Interactive,false,true),runB=run_protocol_impl(m,parent,p,1,0,6,0,s,&controls,LaboratoryRange::Interactive,true,true);check(runA.ok==runB.ok&&runA.message==runB.message&&runA.points.size()==runB.points.size());if(runA.points.size()==runB.points.size())for(size_t i=0;i<runA.points.size();++i)check(outer_same_state(runA.points[i].state,runB.points[i].state)&&same_sym(runA.points[i].strain,runB.points[i].strain)&&same_diag(runA.points[i].diagnostics,runB.points[i].diagnostics));
 check(derivative_work_columns()==38);std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"seeded_trials\":"<<seeded<<",\"cold_integrations\":"<<coldwork<<",\"warm_integrations\":"<<warmwork<<",\"passed\":"<<(failures?"false":"true")<<"}\n";return failures?1:0;
}
