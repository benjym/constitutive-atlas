from pathlib import Path
import json,hashlib,shutil
p=Path(__file__).parent; root=Path('/private/tmp/atlas-duncan-portable-power-v1'); assert not root.exists();root.mkdir()
up=Path('/opt/homebrew/Cellar/emscripten/6.0.8/libexec/system/lib/libc/musl');(p/'upstream').mkdir()
files=['src/math/'+n for n in ['pow.c','pow_data.c','pow_data.h','exp_data.c','exp_data.h','__math_xflow.c','__math_uflow.c','__math_oflow.c','__math_invalid.c']]+['COPYRIGHT']
for f in files:shutil.copy2(up/f,p/'upstream'/Path(f).name)
source=root/'source';shutil.copytree(p.parent/'frozen/source',source)
d=source/'diagnostic_pow';d.mkdir()
for f in files:
 if f=='COPYRIGHT':continue
 s=(up/f).read_text()
 if f.endswith('pow.c'):s=s.replace('double pow(double x, double y)','double atlas_diagnostic_pow(double x, double y)')
 if f.endswith('.h'):s=s.replace('#include <features.h>','#include "libm.h"')
 elif Path(f).name in ['pow_data.c','exp_data.c']:s='#include "libm.h"\n'+s
 (d/Path(f).name).write_text(s)
(d/'libm.h').write_text('''/* Isolated diagnostic compatibility layer, not a production math API. */
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
#endif
''')
h=source/'cpp/include/atlas/tensor.hpp';s=h.read_text();assert s.count('std::pow(')==3;s=s.replace('std::pow(','::atlas_diagnostic_pow(');s='extern "C" double atlas_diagnostic_pow(double,double);\n'+s;h.write_text(s)
c=source/'CMakeLists.txt';s=c.read_text();s+='''
# Isolated generic arithmetic diagnostic; no production installation.
enable_language(C)
target_sources(atlas_solver PRIVATE diagnostic_pow/pow.c diagnostic_pow/pow_data.c diagnostic_pow/exp_data.c diagnostic_pow/__math_xflow.c diagnostic_pow/__math_uflow.c diagnostic_pow/__math_oflow.c diagnostic_pow/__math_invalid.c)
''';c.write_text(s)
shutil.copytree(d,p/'adapted');shutil.copy2(h,p/'adapted/tensor.hpp');shutil.copy2(c,p/'adapted/CMakeLists.txt')
paths=list((p/'upstream').glob('*'))+list((p/'adapted').glob('*'))+[p/'prepare.py',p.parent/'freeze.json',p.parent/'common-residual-v1/power-v3/precision-results.json']
(p/'source-freeze.json').write_text(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths},'mirror':str(source),'upstream_sdk':'Emscripten6.0.8 bundled musl; exact local paths/hashes and COPYRIGHT preserved','changed_baseline_files':['cpp/include/atlas/tensor.hpp','CMakeLists.txt'],'new_directory':'diagnostic_pow/','production_changes':False},indent=2)+'\n')
print('Isolated portable-power source prepared; not built')
