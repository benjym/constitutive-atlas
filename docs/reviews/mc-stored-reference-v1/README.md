# Independent stored-input Mohr–Coulomb H0 references

Task REF-mc-stored-tensor-directions-v1. This packet provides independent high-precision references for140 frozen named cases,38 current/parent/loading directions, and five separate material-parameter sensitivities. It uses only Python's standard library and the exact copied independent characteristic-cubic helper from the earlier spectral reference packet. It imports no Atlas/model/compiler/author implementation and executes no candidate or compiled artifact.

The canonical interface treats actual stored binary64 E,nu,c,phi,psi as exact real input values. It computes the elastic trial exactly with Fraction in stored Mandel coordinates, then converts shear to Cartesian by mathematical sqrt(2). Angles use high-precision Taylor sine/cosine. References describe the exact H0 source return expressions, not the rounded candidate classifier's unique selected tangent. Each mathematically defined branch has its own value and derivatives, including alternatives that are not source-admissible at that point.

## Results

- 140 canonical cases; strict-source selected counts: elastic24, face29, left26, right26, apex35.
- 571 defined branch expressions,21,698 full directional vectors (571×38), and2,855 separate parameter vectors (571×5). Repeated-spectrum undefined alternatives have explicit statuses.
- Base280/360 digits with frozen adaptive precision (actual280–780 and360–860) compare327,888 numeric fields. Maximum normalized difference3.84834e−172 and maximum internal normalized spectral/KKT residual1.05920e−186, both below the frozen1e−60 reference gate. No unresolved cases.
- Fixed-branch centered differences at400 digits and two relative steps1e−60/1e−70 pass15,264 component checks on12 representative cases. Worst normalized error3.61285e−70 against1e−60. Seven input columns include shear and column37; all five material parameters are checked separately.
- All38 directions pass260,376 basis/mixed linearity checks. Apex parameter identities pass4,200 checks. Six assertions preserve actual stored mixed-scale middle values and their returned values, including1 beside ±1e300 and1e−300 beside ±1e−100.

These are reference construction checks. They neither admit the model nor establish candidate/backend correctness, full floating-domain coverage, experimental validity, a unique boundary derivative, or parameter-Jet support in the production API.

## Reproduce

Use fresh output paths; preserve preceding outputs. Gzip metadata has mtime0; use the same output basenames for exact compressed-byte replay.

```sh
python3 -B generate.py corpus/inputs.json 280 /private/tmp/new-mc-ref/reference-p280.json.gz
python3 -B generate.py corpus/inputs.json 360 /private/tmp/new-mc-ref/reference-p360.json.gz
python3 -B check.py corpus/inputs.json /private/tmp/new-mc-ref/reference-p280.json.gz /private/tmp/new-mc-ref/reference-p360.json.gz reference-policy.json
python3 -B check_derivatives.py corpus/inputs.json /private/tmp/new-mc-ref/reference-p360.json.gz derivative-self-check-policy.json
```

Create `/private/tmp/new-mc-ref` first. `check.py` and `check_derivatives.py` exit nonzero on failed checks. Reference generation records arithmetic/domain failures in `unresolved`; consumers must check that list, not merely process exit status. Command stdout/stderr from the original runs is retained. Both reference gzip files are approximately3.4MB.

## Freeze and provenance

The parent corpus freeze SHA and all six source/input byte identities were verified before copying. `corpus/inputs.json` SHA256 is `c834a0800d60ac90d50b77da24308a2032343ba8e2b0620a3e3a4dc961ece28e`. The corpus has115 unique bitwise inputs among140 named cases and includes explicit prior failed-v1 hold regressions. It records eight **historical** candidate interpreter capture calls for those negative cases. This reference generator made zero candidate/Atlas calls. The capture script is copied for provenance and was not executed here.

`prospective-freeze.json` pins generator/helper, policy and copied sources before the first reference values. `derivative-self-check-prospective-freeze.json` pins the two-step derivative check before its values. The original strict-relative policy draft is preserved as `reference-policy-initial-relative.json`; it was superseded **before any generation** because pure relative comparisons cannot certify identically zero cancellation fields. The frozen replacement retains the1e−60 threshold with the explicit natural-scale floor described in `reference-policy.json`. There were no failed reference-generation or derivative-check runs in this task; no gate was changed after observing a failure.

The primary source is Sysala–Cermak arXiv1508.07435v3, pp7–13 Eqs3.1–3.6 and4.8–4.29; grouped tensor/tangent forms pp14–16. Exact source receipt and source-to-formula transcription are copied under `source/`. Raw copyrighted PDF bytes remain private. The independent helper is byte-identical to the prior `spectral-reference-v1/packet/generate.py`; [FORMAT.md](FORMAT.md) explains its use and the output contract.

## Scope and next gate

Source branch classification and all interval distances are high-precision evaluations, with stable cross-precision labels and KKT checks. They are not rigorous interval root/equality certification. Rounded binary64 model coefficients or roots may choose an adjacent branch near a boundary. The optional resolved-coefficient diagnostic reports separately frozen binary64 K,G,sf,sd,cf as exact coefficients; it provides values/branches only and does not replace the canonical physical reference.

A consumer must freeze its candidate value/derivative/branch-adjacency and rollback policy before candidate observations. Publishing all branch references does not authorize choosing whichever reference gives the smallest error. The caller must identify its actual selected branch and apply its prospective policy. These references evaluate the return operator on stored trials; host initialization/parent-state admissibility is a separate gate, particularly for captured rounded hold states. Failure/recovery and committed-state rollback still require actual generated solver tests.
