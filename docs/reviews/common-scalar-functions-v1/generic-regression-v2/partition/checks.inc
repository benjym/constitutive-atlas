namespace checks_study {
int run(){using namespace atlas;bool pass=true;State p{1.,3.,2.,3.},good(12),bad=good;bad[0]=12.;
 State out;Sym<double>zero;bool raw=evaluate_model(0,bad,good,zero,p,out);bool physical=solution_admissible(0,bad,p);pass=pass&&raw&&!physical&&solution_admissible(0,good,p);
 State malformed(11);pass=pass&&!solution_admissible(0,malformed,p)&&!solution_admissible(0,good,State(3));
 const double poison[]={std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};int rejected=0;
 for(int field=0;field<16;++field)for(double x:poison){State z=good,pars=p;if(field<12)z[field]=x;else pars[field-12]=x;pass=pass&&!solution_admissible(0,z,pars)&&solution_admissible(0,good,p);++rejected;}
 int seed_rejected=0;for(int field=0;field<12;++field)for(int column=0;column<38;++column)for(double x:poison){std::vector<Jet>z(12);z[field].d[column]=x;pass=pass&&!generated_solution_constraints(0,z,p);++seed_rejected;}
 std::vector<Jet>z(12);pass=pass&&generated_solution_constraints(0,z,p);
 State parent=bad;IntegrationSettings settings;settings.max_depth=0;auto a=integrate(0,parent,zero,p,settings);pass=pass&&!a.ok&&a.state==bad&&parent==bad;
 auto recovery=integrate(0,good,zero,p,settings);pass=pass&&recovery.ok&&recovery.state==good;
 struct Legacy {};pass=pass&&checked_solution_state(Legacy{},bad,p);
 std::cout<<"{\"pass\":"<<(pass?"true":"false")<<",\"raw_extension_ok\":"<<(raw?"true":"false")<<",\"invalid_physical_rejected\":"<<(!physical?"true":"false")<<",\"nonfinite_rejections\":"<<rejected<<",\"seed_rejections\":"<<seed_rejected<<"}\n";return pass?0:3;}
}
