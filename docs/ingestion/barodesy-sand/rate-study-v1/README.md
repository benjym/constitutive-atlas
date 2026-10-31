# Sand barodesy2015 — instantaneous rate research draft

Task SRC-barodesy2015-rate; review_igs97,2026-10-31. This additive packet preserves the frozen [parent source packet](../README.md). It does not add a model to the research catalogue, website, normal generated catalogue or solver build.

## Selected equations and scope

[Kolymbas2015](https://doi.org/10.1680/geot.14.P.151), original pp53–56 Eqs9,20,23,26–31, supplies the sand law. Its publisher PDF receipt remains in [the parent source audit](../source-audit.json): SHA256 `4d4511bdbb6014c19460bf0c5d7e2072c2c606fa8a5b49db180fc99d0da149da`. No PDFs, renderings or author software are redistributed. Existing source choices are unchanged: standard trace despite the p53 repeated-D22 typographical expression; fixed/supplied-corotated frame W=0; no general zero-stress initialization; no large-spin equivalence claim. Source p59 leaves substantial-shear objective-rate choice unresolved.

[model-draft.json](model-draft.json) is schema0.1/rate, status draft, ID `research-barodesy-sand-2015-fixed-frame`, stress6+e state7, compression positive, orthonormal Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Physical parameters, in order: c1,c2,c3,c4,c5,ec0,emin. Defaults explicitly use the **separate2019 author-manuscript illustrative fixture**, with c4 converted465kPa to465000Pa; they are not an exact2015 calibration or experimental fit.

Let n=|E|, U=E/n, v=trU, s=|Sigma|, S=Sigma/s, a=c1 exp(-c2 v), P=expm(-aU)/|expm(-aU)|. Set B=(ec0-emin)/(ec0+1) exp[-(1+emin)/c5 log1p(c5 s/c4)], ec=(emin+B)/(1-B), K=(c4+c5 s)/(e-emin). The compression-positive rate is

`Sigma'=K*((v-c3*ec)*P+c3*e*S)*n`, `e'=-(1+e)*tr(E)`.

Here s is the **Frobenius stress norm**, not mean pressure. The draft computes s as c4*norm(Sigma/c4), algebraically identical on its numerical interior. c4's physical role is the stress term in the original stiffness and critical-state law. Using c4 as the schema stress normalization is a separate provisional solver convention; it does not establish a universal integration tolerance. No integration tolerances or state-advance evidence are established here.

## Checked exponential envelope and numerical interior

The current generic implementation is `symmetric-expm-taylor18-frobenius64-v1`: dimensionless symmetric argument, Mandel Frobenius norm<=64, degree18 Horner with scaling/squaring, finite intermediate checks. This packet only uses that existing primitive. It adds no model-specific compiled kernel or shared operator.

The declared parameter envelope c1 in[-2,-.1], c2 in[0,1.5] proves `norm(-aU)=abs(c1)*exp(-c2*v) <= 2*exp(1.5*sqrt(3)) < 26.88 < 64` for nonzero loading, since |v|<=sqrt3 and norm(U)=1. At exact zero loading U=0 and the argument is0. This is an analytic parameter-bound proof, not a sampled maximum claim. Twelve retained c1/c2-corner cases exercise compression, extension and oblique directions against the Decimal oracle. Approximate arithmetic still uses the operator's own computed norm guard.

Other deliberately restricted support: c3 in[-5,-.1], c4 in[1000,1e8]Pa, c5 in[.1,100], ec0 in[.1,2], emin in[0,1], ec0>emin; e>emin with e-emin>=1e-8 and e<=3; scaled stress norm in[1e-10,1e10]; strictly positive normalized diagonals, leading2minor and determinant greater than64binary64epsilon. This is a conservative numerical interior, **not certified SPD classification** or complete physical applicability. No stress/density eigenvalue clipping is applied. Normalized Sylvester minors use explicit Cartesian-equivalent Mandel expressions.

Nonzero loading norm must be in[1e-140,1000]. The absolute-component sum distinguishes an actual zero input from a nonzero input whose squared norm underflows; the latter is rejected. These are numerical support choices, not source material limits. Trial quantities are guarded or rejected; invalid support is never silently relabeled zero loading.

Exactly zero loading selects the continuous zero-rate research extension, all7rate components zero, at admissible nonzero stress/e. The literal normalized source D0 is undefined there; no unique full loading Fréchet derivative is claimed. Zero stress stays rejected: the parent's two-direction limit witness proves the general T0 limit is nonunique. This packet supplies neither initialization repair nor spin correction.

## Independent reference and separate gates

[reference.py](reference.py) imports no Atlas module. It converts the actual binary64 Mandel values exactly to Decimal, divides shear components by Decimal sqrt2, and works with source **tension-positive full3x3 Cartesian** T,D. It directly sums the matrix power series with a geometric absolute-tail stopping rule; no Horner18, Atlas matrix products, production expm or production integration is used. The calculation is independently repeated at80and120digits. All7decimal channels, term counts and absolute precision differences are retained in [reference.json](reference.json). The observed refinement is empirical, not a rigorous forward-error certificate.

The draft gate checks structural/schema typing and common C++ source generation, then evaluates only the existing Python DSL. The oracle gate replays every retained input at both precisions and requires complete fresh equality with the retained reference, including rejected diagnostics. A forged frozen output is not accepted just because it has plausible metadata. No native or Wasm binary was executed.

The frozen [protocol](protocol.json) sets componentwise stress-rate error/natural scale<=2e-12, where the scale is max((c4+c5s)*|E|/(e-emin),norm(reference stress rate)). This follows rate homogeneity and avoids an arbitrary1Pa floor masking tiny nonzero loading. Void rate is checked separately:4ULP of the correctly rounded120digit result, or exact zero if the reference is zero. Exactly zero loading requires all7outputs exactly zero. These are instantaneous numerical gates, not scientific or finite-path criteria.

The37valid fixtures include full oblique stress/shear, pure shears, hydrocompression/extension, deviatoric loading, positive homogeneity, reversal, rotations/reflection, physical stress-unit scaling, independent parameter corners and density support. Nineteen Python invalid requests cover stress/density/domain, loading limits, parameter limits and named-input/type failures. The next compiled **numeric** proposal contains only15invalid positional requests. Boolean loading, nonfinite text and extra/missing named parameters remain4Python input checks; no implicit CSV coercion or compiled coverage claim is made. A future malformed-parser protocol requires separate literal raw inputs and parser-response rules.

## Reproduction and retained result

From this directory, with the installed repo on PYTHONPATH:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/path/to/constitutive-atlas python3 -m unittest -v test_rate_study
PYTHONDONTWRITEBYTECODE=1 python3 reference.py --check reference.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/path/to/constitutive-atlas python3 check.py
```

The reference command needs only stdlib Python. The draft check requires the repo's existing Atlas interpreter/compiler and existing schema-validation dependencies. The manifest pins relevant repo dependency bytes as observations; a changed dependency must be reviewed/re-pinned before a future compiled study. Portable fixture inputs are retained rather than regenerated using platform trigonometry. Root-level utility scripts used to assemble inputs are deliberately not delivered or required.

Current result:13Python test groups pass,37valid rates pass and19invalid requests reject. Max stress scaled error is7.604e-16; max void error is retained per case in [python-report.json](python-report.json). Header generation is tested in a temporary directory; it is **not compilation**. Immutable-parent tests cover pure evaluation only, not rollback of an integrated constitutive update. Corruption tests cover forged/missing/duplicate reference rows, precision/failure diagnostics, model-dependency mismatch, inaccurate output and Boolean aliases.

## Smallest next compiled study proposal

After independent source/code review and a separate coordinator handoff, freeze an isolated generated catalogue containing only this exact draft. Use the existing generic instantaneous research probe, unchanged common DSL evaluator, one explicit serial native build and then one explicit serial Wasm build. Bind exact model, allsource/dependency files, generated catalogue, descriptor, request inputs and artifact hashes before observations. No handwritten barodesy kernel is justified.

Run the same37valid positional requests, then15numeric-invalid/recovery pairs in each persistent process/instance, plus descriptor:68rows/backend if one initial valid control is not duplicated. Recover after each rejection using the original oblique control, verify request echo, state layout7, parameter order7, status, full7rates and fresh independent accuracy. Persist raw request/response bytes before parsing; separate parser/arity failures from normal echoed domain failure. Require both raw logs, before/after artifact/source hashes and strict input types; compare native/Wasm only after both independently meet reference gates. This is a **proposal**, not an executed or implemented collector contract.

Do not add material AD, a finite-path solver or public website access in that step. A later source-backed study must separately establish nonzero-state domain continuity, caller partition/refinement, exact volume relation, accepted-substep replay, failed-update parent rollback and recovery. Zero-stress initialization, finite spin and calibrated experimental validation remain unresolved.
