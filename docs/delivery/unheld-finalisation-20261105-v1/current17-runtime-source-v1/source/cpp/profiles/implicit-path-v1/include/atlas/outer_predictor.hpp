#pragma once
namespace atlas {
// Numerical initial guess only. Caller retains exact increment only after commit.
inline bool previous_lateral_guess(double axial,const Sym<double>*previous,double&lateral){
 if(!previous||!std::isfinite(axial)||axial==0.)return false;
 for(double v:previous->v)if(!std::isfinite(v))return false;
 const double prior=previous->v[0];if(prior==0.||std::signbit(prior)!=std::signbit(axial)||!outer_same_bits(previous->v[1],previous->v[2]))return false;
 if(previous->v[3]!=0.||previous->v[4]!=0.||previous->v[5]!=0.)return false;
 const double ratio=axial/prior;if(!std::isfinite(ratio)||ratio==0.)return false;
 const double proposed=previous->v[1]*ratio;if(!std::isfinite(proposed))return false;
 lateral=proposed;return true;
}
#ifdef ATLAS_TEST_OUTER_BUDGET
inline constexpr int outer_control_budget=ATLAS_TEST_OUTER_BUDGET;
static_assert(outer_control_budget>=1&&outer_control_budget<=30,"test may only reduce the public outer budget");
#else
inline constexpr int outer_control_budget=30;
#endif
#ifdef ATLAS_DISABLE_OUTER_REUSE
inline constexpr bool default_outer_reuse=false;
#else
inline constexpr bool default_outer_reuse=true;
#endif
}
