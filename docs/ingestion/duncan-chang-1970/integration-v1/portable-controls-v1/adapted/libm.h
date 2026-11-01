/* Isolated diagnostic compatibility layer, not a production math API. */
#ifndef ATLAS_DIAGNOSTIC_LIBM_H
#define ATLAS_DIAGNOSTIC_LIBM_H
#include <stdint.h>
#include <float.h>
#include <math.h>
_Static_assert(sizeof(double)==8 && DBL_MANT_DIG==53 && DBL_MAX_EXP==1024 && FLT_RADIX==2 && FLT_EVAL_METHOD==0,"binary64 required");
#define hidden
#define WANT_ROUNDING 1
#define WANT_SNAN 0
#define TOINT_INTRINSICS 0
#undef __FP_FAST_FMA
#define __FP_FAST_FMA 0
#define issignaling_inline(x) 0
#define predict_false(x) __builtin_expect(x,0)
#define asuint64(f) ((union{double _f; uint64_t _i;}){f})._i
#define asdouble(i) ((union{uint64_t _i; double _f;}){i})._f
#define __pow_log_data atlas_diagnostic_pow_log_data
#define __exp_data atlas_diagnostic_exp_data
#define __math_xflow atlas_diagnostic_math_xflow
#define __math_uflow atlas_diagnostic_math_uflow
#define __math_oflow atlas_diagnostic_math_oflow
#define __math_invalid atlas_diagnostic_math_invalid
static inline double eval_as_double(double x){double y=x;return y;}
static inline double fp_barrier(double x){volatile double y=x;return y;}
static inline void fp_force_eval(double x){volatile double y;y=x;(void)y;}
double __math_xflow(uint32_t,double);
double __math_uflow(uint32_t);
double __math_oflow(uint32_t);
double __math_invalid(double);

#define __sin atlas_diagnostic_kernel_sin
#define __cos atlas_diagnostic_kernel_cos
#define __rem_pio2 atlas_diagnostic_rem_pio2
#define __rem_pio2_large atlas_diagnostic_rem_pio2_large
#define GET_HIGH_WORD(hi,d) do{(hi)=asuint64(d)>>32;}while(0)
#define FORCE_EVAL(x) fp_force_eval((double)(x))
double __sin(double,double,int);
double __cos(double,double);
int __rem_pio2(double,double*);
int __rem_pio2_large(double*,double*,int,int,int);
#endif
