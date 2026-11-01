#include "atlas/solver.hpp"
#include <iostream>
#include <limits>
int main(){
 using namespace atlas; int checks=0,failures=0;
 auto check=[&](bool ok){++checks;if(!ok)++failures;};
 const State parent{4,8}, original=parent, cold{4,0}, scales{2,1};
 State seed{2,99},saved=seed,chosen{91}; int evaluations=0,calls=0;
 auto reset=[](State&x){x[1]=0;};
 auto admissible=[](const State&x){return x[0]>=0;};
 auto evaluate=[&](const State&x,State&r){++calls;check(parent==original);r={x[0]-1,x[1]};return true;};
 auto identity=[](const State&,State&){};
 check(choose_implicit_seed(cold,&seed,scales,reset,admissible,evaluate,identity,chosen,evaluations));
 check(chosen==State({2,0})&&seed==saved&&parent==original&&evaluations==2&&calls==2);
 // Null, malformed, nonfinite and inadmissible candidates never evaluate.
 for(int kind=0;kind<6;++kind){State bad=seed,scale=scales;const State*ptr=&bad;
  if(kind==0)ptr=nullptr; if(kind==1)bad.pop_back();if(kind==2)bad[0]=std::numeric_limits<double>::infinity();
  if(kind==3)bad[0]=-1;if(kind==4)scale[0]=0;if(kind==5)scale.pop_back();
  chosen={91};evaluations=0;calls=0;
  check(!choose_implicit_seed(cold,ptr,scale,reset,admissible,evaluate,identity,chosen,evaluations));
  check(chosen==State({91})&&evaluations==0&&calls==0);
 }
 // Equal/worse guesses are ignored; output untouched. Aliasing seed and cold is safe.
 for(double value:{4.,8.}){State bad{value,8};chosen={91};evaluations=0;
  check(!choose_implicit_seed(cold,&bad,scales,reset,admissible,evaluate,identity,chosen,evaluations));check(chosen==State({91})&&evaluations==2);}
 chosen={91};evaluations=0;check(!choose_implicit_seed(cold,&cold,scales,reset,admissible,evaluate,identity,chosen,evaluations));check(cold==State({4,0}));
 // Failed, malformed or nonfinite evaluations cannot select a seed.
 for(int route=0;route<6;++route){int count=0; chosen={91};evaluations=0;
  auto broken=[&](const State&x,State&r){++count;r={x[0]-1,0};if(count==(route<3?1:2)){if(route%3==0)return false;if(route%3==1)r.pop_back();if(route%3==2)r[0]=std::numeric_limits<double>::quiet_NaN();}return true;};
  check(!choose_implicit_seed(cold,&seed,scales,reset,admissible,broken,identity,chosen,evaluations));check(chosen==State({91})&&evaluations==(route<3?1:2));}
 // Predictor uses the same multiplier replacement for both candidates.
 // Raw residual favors candidate, but multiplier row reversal rejects it.
 State multiplier_seed{2,0};auto no_reset=[](State&){};
 auto predictor_eval=[](const State&x,State&r){r={x[0]-1,0.};return true;};
 chosen={91};evaluations=0;check(choose_implicit_seed(cold,&multiplier_seed,scales,no_reset,admissible,predictor_eval,identity,chosen,evaluations));check(chosen==multiplier_seed);
 auto override_row=[](const State&x,State&r){r[0]=x[0]==4?0.:20.;};
 chosen={91};evaluations=0;check(!choose_implicit_seed(cold,&multiplier_seed,scales,no_reset,admissible,predictor_eval,override_row,chosen,evaluations));check(chosen==State({91}));
 auto bad_override=[](const State&,State&r){r[0]=std::numeric_limits<double>::infinity();};
 check(!choose_implicit_seed(cold,&seed,scales,reset,admissible,evaluate,bad_override,chosen,evaluations));
 // Scaled comparison differs from raw max and must use declared scales.
 State c{10,0},s{0,2},sc{100,1};auto raw=[](const State&x,State&r){r=x;return true;};
 check(!choose_implicit_seed(c,&s,sc,no_reset,[](const State&){return true;},raw,identity,chosen,evaluations));
 check(parent==original&&seed==saved&&cold==State({4,0}));
 std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<",\"passed\":"<<(failures?"false":"true")<<"}\n";return failures?1:0;
}
