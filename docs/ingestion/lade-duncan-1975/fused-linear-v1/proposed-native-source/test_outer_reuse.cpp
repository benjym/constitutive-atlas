#include "atlas/solver.hpp"
#include <iostream>
using namespace atlas;
bool same_diag(const Diagnostics&a,const Diagnostics&b){return a.hierarchical_seed_trials==b.hierarchical_seed_trials&&a.hierarchical_seed_acceptances==b.hierarchical_seed_acceptances&&a.path_seed_value_evaluations==b.path_seed_value_evaluations&&a.path_seed_acceptances==b.path_seed_acceptances&&a.reserved_path_trials==b.reserved_path_trials&&a.iterations==b.iterations&&a.substeps==b.substeps&&a.rejected==b.rejected&&outer_same_bits(a.error,b.error)&&outer_same_state(a.increment_fractions,b.increment_fractions);}
bool same_advance(const Advance&a,const Advance&b){return a.ok==b.ok&&outer_same_state(a.state,b.state)&&same_diag(a.diagnostics,b.diagnostics)&&a.message==b.message&&outer_same_settings(a.settings,b.settings);}
bool same_sym(const Sym<double>&a,const Sym<double>&b){for(int i=0;i<6;++i)if(!outer_same_bits(a.v[i],b.v[i]))return false;return true;}
int main(){int checks=0,failures=0,hits=0,saved=0;auto check=[&](bool v){++checks;if(!v)++failures;};int m=-1;for(int i=0;i<int(models().size());++i)if(models()[i].id=="lade-duncan-1975-midpoint-elastic-eq19-gap-v4")m=i;if(m<0)return 2;
 auto p=default_parameters(m);State parent{60000,60000,60000,0,0,0,13,0};IntegrationSettings s;s.increment_tolerance=1e-7;s.positive_stress_metric=true;s.max_depth=20;s.max_substeps=200000;Sym<double>de;de.v[0]=1e-5;
 Advance payload;payload.ok=true;payload.state=parent;payload.state[6]=-0.;payload.settings=s;payload.message="entire transaction";payload.diagnostics.iterations=17;payload.diagnostics.substeps=4;payload.diagnostics.rejected=1;payload.diagnostics.error=1e-9;payload.diagnostics.reserved_path_trials=9;payload.diagnostics.path_seed_acceptances=2;payload.diagnostics.path_seed_value_evaluations=6;payload.diagnostics.hierarchical_seed_trials=3;payload.diagnostics.hierarchical_seed_acceptances=1;payload.diagnostics.increment_fractions={.25,.25,.25,.25};
 OuterTransaction slot;Advance out;slot.retain(m,parent,de,p,s,payload);check(slot.take(m,parent,de,p,s,out)&&same_advance(out,payload));check(!slot.take(m,parent,de,p,s,out));
 // Every complete key field; bitwise zero/one-ulp, changed size/model/history/parameter.
 for(int k=0;k<20;++k){auto z=parent,q=p;auto d=de;auto t=s;int model=m;slot.retain(m,parent,de,p,s,payload);
  if(k==0)d.v[1]=-0.;if(k==1)d.v[0]=std::nextafter(d.v[0],1.);if(k==2)z[6]=-0.;if(k==3)z.push_back(0);if(k==4)q[0]=std::nextafter(q[0],1.);if(k==5)model=m+1;if(k==6)t.residual_tolerance=std::nextafter(t.residual_tolerance,1.);if(k==7)t.rate_tolerance=std::nextafter(t.rate_tolerance,1.);if(k==8)t.increment_tolerance=std::nextafter(t.increment_tolerance,1.);if(k==9)++t.max_iterations;if(k==10)++t.max_depth;if(k==11)++t.max_substeps;if(k==12)++t.max_backtracks;if(k==13)t.positive_stress_metric=false;if(k==14)q.pop_back();if(k>=15)d.v[k-15+1]=1e-30;
  Advance sentinel=payload;sentinel.message="sentinel";check(!slot.take(model,z,d,q,t,sentinel)&&sentinel.message=="sentinel");check(!slot.take(m,parent,de,p,s,sentinel));
 }
 auto bad=payload;bad.ok=false;slot.retain(m,parent,de,p,s,bad);check(!slot.occupied);slot.retain(m,parent,de,p,s,payload);payload.state[0]=999;check(slot.take(m,parent,de,p,s,out)&&out.state[0]==60000);payload.state[0]=60000;
 // Actual controller both protocols, source loading/unloading/hold/tiny, failure and recovery.
 for(int protocol:{1,3})for(double axial:(protocol==1?State{1e-5,5e-5,-1e-5,0.,1e-12}:State{100.,1000.,-100.,0.,1e-7})){
  Sym<double>a,b;Advance cold,warm;OuterReuseCounts c,w;auto z=parent,q=p;bool ca=controlled_step(m,z,q,protocol,axial,60000,0,a,cold,s,false,&c);bool wa=controlled_step(m,z,q,protocol,axial,60000,0,b,warm,s,true,&w);
  check(ca==wa);check(same_sym(a,b));check(same_advance(cold,warm));check(z==parent&&q==p);check(w.executed+w.hits==c.executed);check(w.misses==0);hits+=w.hits;saved+=c.executed-w.executed;
 }
 check(hits>0&&saved==hits);
 for(int protocol:{1,3})for(int kind=0;kind<3;++kind){auto t=s;if(kind==0){t.increment_tolerance=0;t.positive_stress_metric=false;}if(kind==1)t.max_depth=0;if(kind==2){t.max_iterations=1;t.max_depth=2;}
  Sym<double>a,b;Advance cold,warm;OuterReuseCounts c,w;double axial=protocol==1?.0001:1000.;bool ca=controlled_step(m,parent,p,protocol,axial,60000,0,a,cold,t,false,&c),wa=controlled_step(m,parent,p,protocol,axial,60000,0,b,warm,t,true,&w);check(ca==wa&&same_sym(a,b)&&same_advance(cold,warm));if(kind==0)check(w.hits==0&&w.executed==c.executed);
 }
 // Multi-step source plastic path compares every committed state/diagnostic/strain.
 for(int protocol:{1,3}){auto a=run_protocol_impl(m,parent,p,protocol,protocol==1?.002:1000.,16,0,s,nullptr,LaboratoryRange::Interactive,false);auto b=run_protocol_impl(m,parent,p,protocol,protocol==1?.002:1000.,16,0,s,nullptr,LaboratoryRange::Interactive,true);check(a.ok&&b.ok&&a.message==b.message&&a.points.size()==b.points.size());if(a.points.size()==b.points.size())for(size_t i=0;i<a.points.size();++i)check(outer_same_state(a.points[i].state,b.points[i].state)&&same_sym(a.points[i].strain,b.points[i].strain)&&same_diag(a.points[i].diagnostics,b.points[i].diagnostics)&&outer_same_bits(a.points[i].control,b.points[i].control)&&outer_same_bits(a.points[i].pore_pressure,b.points[i].pore_pressure));}
 for(int protocol:{0,2,4}){Sym<double>a,b;Advance x,y;OuterReuseCounts w;check(controlled_step(m,parent,p,protocol,1e-6,60000,0,a,x,s,false)==controlled_step(m,parent,p,protocol,1e-6,60000,0,b,y,s,true,&w));check(same_sym(a,b)&&same_advance(x,y)&&w.hits==0);}
 auto hold=integrate(m,parent,Sym<double>{},p,s);check(hold.ok&&outer_same_state(hold.state,parent));check(derivative_work_columns()==38);
 std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"actual_reuses\":"<<hits<<",\"avoided_integrations\":"<<saved<<",\"passed\":"<<(failures?"false":"true")<<"}\n";return failures?1:0;
}
