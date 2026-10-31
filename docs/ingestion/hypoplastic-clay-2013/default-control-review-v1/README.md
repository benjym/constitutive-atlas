# Clay2013 default drained control - independent spherical algebra review

Task REV-clay2013-default-control; owner clay2013_source_closure;2026-10-31. Read-only review of the frozen candidate, [preview result](../../../../catalogue/investigations/clay2013-preview-v1/RESULTS.md) and its separately identified default-diagnostics-v1 scripts/output. No build, compiled call, material-oracle replay, shared edit or change to the failed study's gates.

## Conclusion

The reported spherical radial-rate bound is correct for the **exact initial state and fixed illustrative parameters**. At100kPa/e=.8, no differentiable zero-spin axisymmetric drained path can start with positive axial rate and zero radial stress rate under this selected law. At10kPa the exclusion condition does not hold; a zero-radial-stress initial tangent exists. Neither statement proves finite-step endpoint solvability, general physical initial admissibility or experimental validity.

An explicit action loading the complete selected model example is a reasonable consumer response to the current universal100kPa stress mixed with model-specific remaining state examples. Keep the failed100kPa default as negative evidence. The action must identify examples as editable software inputs, not preparation or calibration validation. Loading a different example does not repair or invalidate that earlier failed request.

## Source and equation selection

Mašín2013, [DOI](https://doi.org/10.1007/s11440-012-0199-y), [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf), SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`. Source Appendix43-58 and p3Eq7, with T=-sigma,D=-E, supply the compression-positive zero-spin restriction. Existing [source closure](../README.md) records visual source review and bounded publisher Appendix agreement; this review does not claim a fresh PDF inspection or complete final-publication reconciliation.

Candidate file is `catalogue/investigations/clay2013-preview-v1/models/hypoplastic-clay-2013.json`, SHA256 `6811580cf9c0678605b9bb7d93a524743bbe5b5cb1f547bd232d090aeda950e4`. Inspected exact signs include:

```
Ad = fs*Ld - (sigma/lambda_star)*trace(d)
stress_rate = fs*(de+c*trace(de)*I) + (fd/fdA)*Ad*norm(de)
```

The plus nonlinear term follows the two compression-sign changes while retaining source d. Reversing d or the nonlinear sign would change this diagnosis and would not be a source-consistent solver correction.

## Independent derivation

At sigma=pI with p>0, normalized deviator a=0, j2=j3=Fm=0. For0<phi_c<pi/2, Eq56 becomes a strictly negative spherical tensor, so its normalized direction is d=-I/sqrt(3). The placeholder isotropic Lode value has no effect because Fm^(1/4)=0. With finite positive omega, fdA=4*(1-Fm)^(2/omega)=4. Density sets pe=pr*exp[(N-ln(1+e))/lambda*] and fd=(2p/pe)^2.

Write c=nu/(1-2nu), E=diag(x,y,y), x>0 and arbitrary real y. Then

```
L:E = E+c*(x+2y)I
L:d = -(1+3c)I/sqrt(3)
A:d = [-fs*(1+3c)+3p/lambda*]I/sqrt(3)
```

The radial stress rate is therefore

```
R(x,y)=A*x+B*y-C*sqrt(x*x+2*y*y)
A=fs*c
B=fs*(1+2c)
C=(fd/4)*[fs*(1+3c)-3p/lambda*]/sqrt(3)
```

Useful independent reductions are A=nu*B and

```
fs*(1+3c)-3p/lambda* = (3p/2)*(1/kappa*-1/lambda*)
C=(p/pe)^2*(sqrt(3)*p/2)*(1/kappa*-1/lambda*) >0
```

for lambda*>kappa*>0. These checks remove possible sign/factor-of-three mistakes without using any interpreted or compiled material rates.

For t=y/x, homogeneity gives R/x=g(t)=A+B*t-C*sqrt(1+2t²). Its derivatives are

```
g'(t)=B-2*C*t/sqrt(1+2t²)
g''(t)=-2*C/(1+2t²)^(3/2) <0.
```

If C>|B|/sqrt(2), both tails tend to minus infinity and the unique stationary point is the global maximum. Let Delta=C²-B²/2>0. Then

```
t*=B/(2*sqrt(Delta))
max_y R(x,y)/x = g(t*) = A-sqrt(Delta).
```

The strict condition matters: it cannot be applied when Delta<=0. In particular, failure of that condition alone does not establish a zero tangent; that requires a separate argument.

## Checked numbers and10kPa distinction

`check.py` imports only the Python standard library. It reconstructs actual candidate binary64 default parameters with Decimal.from_float and performs90-digit scalar algebra, never importing Atlas or a material/reference oracle. It validates the literal candidate signs, two equivalent C formulas, A=nuB, concavity/stationary identities and the saved coefficient agreement within1e-13 relative. Selected t probes test the algebra implementation; concavity and tail analysis, not finite sampling, establish the global maximum.

| Initial p | A (Pa) | B (Pa) | C (Pa) | Result |
| --- | --- | --- | --- | --- |
|10kPa|120833.3333333333|604166.6666666666|5377.856783314532|B>sqrt(2)C; no finite global maximum|
|100kPa|1208333.333333333|6041666.666666666|5377856.783314532|Maximum coefficient -2058236.048493199Pa|

At100kPa t*=.9247724386751602, and even that largest radial rate is strictly negative for every x>0. The retained binary64 diagnostic maximum -2058236.0484931972 differs only at floating rounding scale and agrees with this independent higher-precision calculation. The sign is not borderline.

At10kPa B>sqrt(2)C>0, hence g'(t)>B-sqrt(2)C>0 for all real t; g goes from minus to plus infinity. There is exactly one zero-radial initial tangent. Solving the quadratic with the required unsquared sign A+B*t>=0 gives

```
t0=[-A*B+C*sqrt(B²+2A²-2C²)]/(B²-2C²)
  = -0.1907804290773119948...
```

Its independent90-digit residual is1.5e-85Pa. The other squared-equation branch does not satisfy the original nonnegative square-root side. This initial tangent's existence does not by itself prove that an entire1% path or any given discretization will converge. Prior compiled successful10kPa histories are separate retained evidence and were not rerun here.

## Scope and attribution limits

The100kPa result rules out a differentiable **initial constant-radial-stress tangent with positive axial derivative** at the spherical state. It does not rule out every finite endpoint satisfying a constant radial stress, a disconnected large-increment solution, a different control path or a later nonspherical tangent. Numerical control uses finite endpoint solves; reducing the step cannot create the missing smooth local tangent, but this argument is not a theorem about every finite-step root or a proof of the exact algorithmic failure mechanism.

It does not show that100kPa itself is outside the material domain: the retained diagnostic has14successful explicit updates at10/100kPa. A rate can be well-defined and finite under prescribed strain while incompatible with a particular mixed-control tangent. It also does not turn outside-ASBS classification into a general rejection rule. The earlier source initialization review already documents outward ASBS rates; f>0 alone is not a source-defined yield barrier or universal initial inadmissibility condition.

The diagnostic's fourteen initial rate values are **Python interpretation**, not compiled-rate oracle observations. Its bound script contains an inaccurate comment saying “retained compiled initial rate,” while the accessed field is observations[].derived.stress_rate, populated by evaluation_environment. The study RESULTS.md correctly attributes those initial rates to Python. Preserve the script as history and use the correct attribution in future discussion. Matching fourteen values is a bounded algebra/representation comparison, not independent scientific admission or a new compiled acceptance gate.

## Consumer recommendation

Provide an explicit visible “Load model example” action. A complete model example should load the declared parameter defaults and **all persistent initial fields together**, including the full stress tensor, not only density/internal variables. For this candidate that means the unchanged10kPa spherical stress/e=.8 example with its illustrative parameters, explicitly named as software input rather than specimen preparation. If the UI deliberately offers a state-only action retaining edited parameters, label that behavior directly; it is a state example under current parameters, not necessarily a complete source model/calibration example.

Show chosen stress/void ratio and source/preparation limits; retain manual editing and exact import behavior. Do not automatically overwrite imported/user values or silently change all experiments to this example. Preserve support/axisymmetry checks: generic future examples may need unsupported stress components, so do not drop shears or average stresses to fit the lab without explicit rejection. Loading an example cannot guarantee every control, amplitude, reversal or parameter edit succeeds.

Any UI change and selected-example native/Wasm/browser study needs a **new** request identity/freeze. The failed100kPa1%/100step request remains required negative evidence in v1, with its original gates/receipts unchanged. This review recommends no constitutive equation change, pressure floor, clipping, ASBS projection, solver tolerance relaxation or automatic scientific promotion.

## Reproduction and handoff

```sh
python3 -B docs/ingestion/hypoplastic-clay-2013/default-control-review-v1/check.py --root /Users/bmar5496/code/constitutive-atlas
```

First execution passes; no failed check occurred in this review. `checks.json` records complete90-digit outputs; `manifest.json` pins script/report and exact inspected source/candidate/diagnostic/results files. It is a bounded scalar algebra review, not a runtime reproduction closure. Four-file packet staged at `/private/tmp/atlas-clay2013-default-control-review-v1/packet/`: README.md,check.py,checks.json,manifest.json. Coordinator reviews/integrates; no shared writes, builds, reference replay or promotion were performed.
