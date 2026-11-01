#define main frozen_main
#include "../frozen/driver.cpp"
#undef main
int main(){std::cout<<std::setprecision(17)<<std::boolalpha;for(const auto&q:requests()){
 IntegrationSettings s;s.max_depth=0;s.max_iterations=q.iterations;State t;Diagnostics d;const bool ok=implicit_step(q.model,q.z,tensor_from(q.de,0),q.p,t,d,s);State r;bool rok=evaluate_model(q.model,t,q.z,tensor_from(q.de,0),q.p,r);bool spectralok=true;auto a=tensor_from(t,0);double hi=spectral_scalar_or_mark(a,spectral_candidate::Operation::max_value,spectralok),lo=spectral_scalar_or_mark(a,spectral_candidate::Operation::min_value,spectralok);
 std::cout<<"{\"id\":\""<<q.id<<"\",\"ok\":"<<ok<<",\"tentative\":";array(t);std::cout<<",\"residual_ok\":"<<rok<<",\"residual\":";array(r);std::cout<<",\"physical\":"<<solution_admissible(q.model,t,q.p)<<",\"h_minus_range\":"<<t[6]-(hi-lo)<<",\"error\":"<<d.error<<",\"iterations\":"<<d.iterations<<"}\n";
}return 0;}
