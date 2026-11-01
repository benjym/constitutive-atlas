from pathlib import Path
import hashlib,json,shutil
p=Path(__file__).parent;out=Path('/private/tmp/atlas-duncan-portable-controls-v1');assert not out.exists();out.mkdir();source=out/'source';shutil.copytree('/private/tmp/atlas-duncan-portable-power-v1/source',source)
up=Path('/opt/homebrew/Cellar/emscripten/6.0.8/libexec/system/lib/libc/musl');(p/'upstream').mkdir();d=source/'diagnostic_pow'
for name in ['sin.c','__sin.c','__cos.c','__rem_pio2.c','__rem_pio2_large.c']:
 s=(up/'src/math'/name).read_text();(p/'upstream'/name).write_text(s)
 if name=='sin.c':s=s.replace('double sin(double x)','double atlas_diagnostic_sin(double x)')
 (d/name).write_text(s)
shutil.copy2(up/'COPYRIGHT',p/'upstream/COPYRIGHT')
h=d/'libm.h';s=h.read_text();suffix='''
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
''';assert s.endswith('#endif\n');h.write_text(s[:-7]+suffix+'#endif\n')
h=source/'cpp/include/atlas/solver.hpp';s=h.read_text();assert s.count('std::sin(')==1;s=s.replace('std::sin(','::atlas_diagnostic_sin(');h.write_text('extern "C" double atlas_diagnostic_sin(double);\n'+s)
c=source/'CMakeLists.txt';s=c.read_text();s+='\ntarget_sources(atlas_solver PRIVATE diagnostic_pow/sin.c diagnostic_pow/__sin.c diagnostic_pow/__cos.c diagnostic_pow/__rem_pio2.c diagnostic_pow/__rem_pio2_large.c)\n';c.write_text(s)
shutil.copytree(d,p/'adapted');shutil.copy2(h,p/'adapted/solver.hpp');shutil.copy2(c,p/'adapted/CMakeLists.txt')
ps=[p/'prepare.py',p.parent/'portable-power-v1/source-freeze.json',p.parent/'portable-power-v1/failure-analysis.json']+list((p/'upstream').glob('*'))+list((p/'adapted').glob('*'))
(p/'source-freeze.json').write_text(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in ps},'mirror':str(source),'production_changes':False,'incremental_changes':'From exact previouscandidate: solver.hpp single generic control sine call, diagnosticcompat header/prototypes,5newCfunctions andCMakeappend only; material sin/cos unchanged'},indent=2)+'\n')
print('New control-sine candidate prepared; no build')
