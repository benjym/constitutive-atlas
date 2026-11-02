# VIBE Appendix A transcription initial study

Coordinator /root,3November2026. This is a draft, not scientific approval. Production equations are declarative JSON; build_candidate.py only emits expressions. Complete source source-v2 manifest90603c5756a0a1a8f2edd8cbdcb6d21ad639f51796d2dba78ceaca04047f442c and independent source/design reviewe977f5d0b734c740525cad7a3ef10022eb5483c10ece5a223010c03c43fa3b50 are retained in main workspace. Current candidate SHA256 2b9c882a6f272d793e28febaa570ba315449fd401348b69239d76edb083ed292.

Explicit identity: published complete AppendixA, zero-spin small-strain fixed-spatial 3D, compression-positive Mandel boundary, net Cauchy stress. Main-text Eq27 opposing-rate discrepancy and unique tensor identity completions are source-reviewed, not silent code corrections. No supplied author implementation runs.

## Map

The JSON follows A1–35 in algebraic dependency order. Fourth-order actions are expanded using isotropic identity/trace action. The stress RHS is first assembled in the source compression-negative signs and then negated at the output; e_dot is -(1+e)tr(D_Atlas). Saturation and micro/macrovoids use current stress/suction/T/e/scan. The rank-one inverse is applied as X-q/(1+3q)tr(X)I; stableFm is the source-equivalent trace-free invariant identity independently checked on30 exact matrices. At hydrostatic states cos3theta=0 is a lazy evaluation value for an otherwise undefined Lode quotient; its source multiplierFm^1/4 vanishes, so this is the continuous isotropic constitutive limit. No arbitrary deviatoric floor or state clipping is introduced.

The source leaves fscan unspecified at zero suction rate. The draft uses0 in that algebraic placeholder; all source stress terms depending on it multiply suction rate or its absolute value and a_scan_dot is zero, so no physical zero-rate response depends on that placeholder. This must be independently checked.

## Domain and parameters

Strict positive suction and positive thermal multiplier; positive micro/macrovoids, pM/pm, lambda/lambda_act, OCR and all required log/power arguments;0<=scan<=1;0<SM<1;0<=Sr<=1; all source denominators nonzero. Nonzero denominator guards use abs(den)>0 without assuming every denominator must be positive. No saturated endpoint, a_e=1 or numerical-clipping branch is claimed. Values at representational saturation/underflow are refused, not silently regularized.

Published BCV values are defaults; seven hidden parameters and the1K unit normalization are fixed. Candidate editable min/max are explicitly prospective Atlas study guards, not paper calibration confidence bounds or an assertion that every parameter/state combination runs. Numerical admission must identify actual qualified protocols/parameter cases and retain unsupported/refused cases. The parent has not observed compiled VIBE results.

## Prospective evidence

Independent source agent reference-v1 uses the paper directly and must not read/copy this DSL. Full8state reference paths and observables: nearSBS relaxation; six-component mixed mechanics/reversal; positive hydraulic/thermal paths including opposing internal contributions; scan branch reversals; selected nonzero ns/ls/lT collapse probes; source/domain rejection and recovery. Proposed comparison limits before compiled observation: point Pa/s1e-8abs+1e-7rel; dimensionless rates1e-12abs+1e-7rel; trajectory Pa1e-2abs+1e-7rel, e/scan1e-9abs+1e-7rel, scalar observables1e-8abs+1e-7rel. Reference convergence/precision and execution settings remain to be frozen separately before numerical qualification. Backend parity alone is insufficient.

Initial pure-Python inspection is limited to known source near-SBS context atT294K,s10MPa,e.725,scan0,pnet5.185790988798023MPa and zero controls/rates. It checks source-supported initialization and nonzero viscosity, not trajectory accuracy. Structural/dimensional transcription errors and their corrections are retained in transcription-errors.json. No C++/native/Wasm build or call has occurred.
