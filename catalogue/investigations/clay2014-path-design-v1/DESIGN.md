# Clay2014 common-engine finite-path study design

Design only; no collector, model change, build, native/Wasm run or admission. Read baseline `1aa5ddcd533dceb5a1e994920d1708d2cf17184d`. The independent reference author is freezing a separate packet at `/private/tmp/atlas-clay2014-path-reference-20261031-v1`; the proposed collector must wait for the final generator, policy, inputs, reference and independent review hashes. Frozen instantaneous rate/source evidence stays unchanged.

## Selected law and complete target matrix

Use only `hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane-research`, exactly the existing seven-state model: compression-positive effective stress and void ratio, fixed actual material-plane axis, zero spin, printed Eq14 Am, proposed Eq49 alpha_f and source a=.3. No IGS, orientation transport, finite spin, public/experimental/AD admission or repair of either manuscript normalization discrepancy. [Source](https://doi.org/10.1680/geot.13.P.065), [pinned manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf), SHA256 `2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`.

| Path | Fixed orientation / stiffness | Supplied initial | Three original increments |
|---|---|---|---|
| vertical-nonproportional | n=(0,0,1), anisotropic ratios | Sigma=(120000,90000,80000,3000,-2000,1000)Pa; e=.65 | A,B,C below |
| oblique-reversal | n=(1/3,2/3,2/3), same ratios | Same actual input stress/e | Same A,B,C |
| rotated-oblique-reversal | Rotate actual axis, stress and each increment by Q below | Independently rounded rotated stress; e=.65 | Independently rounded Q*A*Q^T, etc. |
| isotropic-ratios-hydro-reversal | alpha_G=alpha_E=alpha_nu=1,nu_pp=0 | Sigma=100000I Pa; e=.65 | .003I, -.002I, .0015I |

Mandel order is xx,yy,zz,xy,yz,xz. A=(.006,-.002,.001,.002,-.001,.0015), B=(-.004,.001,-.0005,-.001,.0008,-.001), C=(.001,.003,-.001,-.001,.0015,.0007). Q has rows (1,2,2)/3,(2,1,-2)/3,(-2,2,-1)/3. Q is used on full Cartesian matrices, and on the axis vector. Actual supplied binary64 inputs, not ideal decimal or ideal eigenvalues, define the reference cases.

Other parameters are the existing illustrative rate fixtures: phi_c=30degrees converted once to radians,lambda_star=.12,kappa_star=.025,N=1.1,nu_pp=.1,alpha_G=2,alpha_E=2^1.25,alpha_nu=2, with the explicit isotropic case changes above. These are software fixtures, not source calibrations. p_ref stays1000Pa, source_a=.3 and fixed numerical policies stay64epsilon. Set the **numerical** p_scale to max(1Pa,hypot(*original supplied stress6)) independently for each case, and keep it fixed across tolerances, partitions, every generated state and failures. All17 parameter values/order must be explicit and echoed.

Every path runs tolerances1e-4,1e-6,1e-8 at caller partitions1 and7: 24 trajectories, 288 actual updates. There are12 trajectories of3 calls and12 of21. Every call uses the actual previous successful generated seven-state output as its next parent; neither reference targets nor analytical states may replace it. Every path/partition reference starts once from the original supplied state and carries its independent state through every actual caller piece. Preserve original order and all reversal knots; never sort by accumulated strain.

## Independent reference and exact loading

The reference uses the separately authored `tools/reference_clay2014_cartesian.py` literal four-index source law, Cartesian seven-state fixed-step RK4 and no DSL/common engine. Use28/56/112 steps per original caller piece at n=1 and4/8/16 per one-seventh piece at n=7. These are matched **nominal** meshes; binary64 residual pieces and actual RK steps are retained and need not be identical exact inputs. Three meshes establish observed refinement, not a rigorous error certificate. All RK stages and returned states must remain in the independent rate domain; never project stress, clip e, normalize state or restart from generated solver output.

Split each original Mandel component with first n−1 pieces equal to its actual binary64 division by n. The last piece is exact original rational minus exact sum of the earlier binary64 pieces, and must itself be exactly representable. Reject a nonrepresentable split. Retain exact rational cumulative six-component loading at every caller point and convert only for display. The independent reference API retains original inputs, parameter order, all actual caller pieces, all seven state targets at every mesh, coarse/middle and middle/fine differences, stage-domain checks, scalar closed-form comparison and rotated covariance.

For the isotropic-stiffness hydro case, derive a second non-RK target. Let V be signed actual volumetric strain, alpha=alpha_f>0, y=(pe/p)^alpha and k=alpha*(1/kappa_star−1/lambda_star)/2. During a fixed-sign segment with s=sign(V),

`y_new=s+(y_old−s)*exp(−kV)`;

`pe_new=pe_old*exp(V/lambda_star)`, `p_new=pe_new*y_new^(−1/alpha)`;

`e_new=(1+e_old)*exp(−V)−1`.

Use expm1 for the stable reciprocal update, explicit positive-y checks and long-precision/actual-loading comparison where practical. Carry y/pe through the real segment sequence, preserving reversal; unloading is not automatically a fixed kappa slope away from its special state. Sanisand independently confirmed this derivation. In all paths, check void closure separately from the original initial e and exact accumulated trace.

## Proposed precompiled numerical acceptance contract

The independent reference draft proposes stress-scaled limits[2e-3,1e-4,8e-6] and separate absolute void limits[5e-6,3e-7,2e-8], corresponding to loose/middle/tight. Stress error is the full six-component Frobenius difference divided by fixed original S=max(1Pa,hypot(initial stress6)); all seven state components are checked at **every** caller point. These budgets are now frozen in the independent source-only reference policy, before compiled observations.

Reference uncertainty U is explicitly the observed max of coarse/middle and middle/fine differences at the same caller point, separately in Pa and absolute void ratio. Require U<=10percent of the smallest corresponding production budget before using the reference, and require reference middle/fine<=.35*coarse/middle unless both are below the declared reference roundoff floor. The frozen reference policy uses5e-12*S Pa and5e-13 void as both reference and future production roundoff floors, superseding the earlier design proposal1e-7Pa/1e-14void. Every production caller point must meet its declared accuracy budget, with reference uncertainty and floors reported separately. Neither U nor observed fourth-order refinement is a certified bound.

Production refinement should hold for each path and both partitions: each endpoint-error successor<=.65*predecessor+2*(floor+maxU), and tight<=.35*loose+2*(floor+maxU). Compare production n=1 and n=7 states at each original physical segment endpoint. The frozen policy requires tight partition discrepancy<=.35*loose+2*productionfloor, with no reference uncertainty because that comparison does not use an RK4 target.

Rotated references must agree under Q at every corresponding caller point within their own empirical covariance budget. Production material covariance is checked at matching physical knots against a declared combined accuracy envelope, e.g.2*per-path production budget plus reference/floor/input-roundoff allowances. Do not demand identical adaptive substep partitions after rotating: the common scaled-component-max error norm is coordinate dependent. Each rotated path must independently meet its own reference and refinement gates. A strict observed monotonic covariance-error requirement can reject roundoff-limited coincidences and is not proposed here.

Proposed native/Wasm parity bound is5e-11 on fixed-scale stress Frobenius difference or absolute void ratio, at every caller state and actual generated parent. Both reports must first satisfy the whole numerical/transaction protocol. Bind exact native report bytes and audit **both** explicit raw transport companions. There is no equality requirement for cross-platform adaptive diagnostics, but each backend's counters/fractions must obey its solver contract.

## Transactions from an actual committed tensor prefix

Use oblique-reversal, n=1,tolerance1e-8. Its first two actual successful calls form the committed prefix list; the actual third matrix call is the recovery control from the committed second state. Do not use native states as Wasm parents: each backend prepares its own actual prefix and derives its probes from its own committed state.

From that same parent request: (1) the third increment with max_substeps=3, (2) (.9,.9,.9,0,0,0), and (3) exact zero. Each is followed by the identical third-increment recovery control. The budget call must fail after positive accepted internal progress and return the exact original caller parent. The domain call must fail and return that exact parent; its full-path void closure would be negative. The zero call must succeed and preserve all seven values. All recoveries must equal the original complete same-backend control response. Prefix and control themselves must bind the actual corresponding matrix entries.

For these inputs the exact first-two-increment trace is approximately.0015, so e_parent≈.6475268553 and the appended .9I full endpoint would give e≈−.8892771129. More generally the endpoint is negative for e_parent<exp(2.7)−1≈13.87973. This establishes an unsupported intended endpoint, not the unique internal reason the numerical solver will first reject. Keep the actual failure message/counters. Budget3 is a prospective regression requirement, not observed behavior; if it does not fail after progress, retain negative evidence and investigate rather than changing the budget after observing it.

Default call settings can reuse the existing predeclared common rate-study tuple[2e-10,rate_tolerance,45,20,20000,11], with only budget changed to3 for that probe. Validate exact settings fields/types/echoes. Rate accepted fractions must be equal dyadic pairs, each depth<=max_depth+1, substep count even and<=max_substeps, success coverage1, failure coverage<1 and partial budget coverage>0. No strain accumulator or independent history memory exists in this seven-state model; claims are material-state rollback only.

## Collection, untrusted evidence and proof boundary

One descriptor +288 matrix updates +three probe/recovery pairs gives295 transport rows per backend. Persist opaque stdout/stderr/status or CABI raw text **before** parsing/exit checks, then checkpoint each parsed response **before** acceptance. Retain partial/failed reports without overwriting their bytes. Require strict finite numeric inputs and outputs (Boolean aliases rejected), exact model ID/parameter/state/strain/settings echoes, actual request-chain identity, model descriptor/catalogue hash and explicit source/version/policy identities. Verify expected complete case×tolerance×partition set, duplicate/missing records, point indices and source reference hashes before checking accuracy.

Recompute the frozen independent reference freshly from pinned generator/constitutive code; do not trust stored reference rates or success metadata alone. Bind original source/typed/model bytes, schema/compiler/DSL/scalar/expm/runtime/settings/main, reference generator/protocol/frozen record, collectors/assessor/tests and executable/loader/Wasm bytes. Source/build manifests are distinct from numerical acceptance. Historical numerical replay can accept explicit archived artifact paths but must not pretend to rebuild or reopen unavailable artifacts. Add corruption tests for reference forging, misplaced caller/reversal records, true but wrong generated parent, altered descriptor/settings/axis, all seven channels, missing/duplicate trajectories, relaxed budgets, failure rollback/counters and both raw companions/parity bindings.

## Isolated target and archive prerequisite

Current CMake lines265–280 define `atlas_clay2014_models` and `atlas_clay2014_rate_probe`, not a common solver. Add a separate explicit `atlas_clay2014_solver` target using unchanged cpp/main.cpp, depending on the **existing** atlas_clay2014_models and including cpp/include plus the same clay2014-generated directory. No second generation command or catalogue merge. Recommend EXCLUDE_FROM_ALL and no automatic CTest registration. For Emscripten, reuse existing ATLAS_WASM_OPTIONS and exception flag, with distinct output clay2014-paths.js/.wasm. Bind descriptor to the single existing clay2014 model before execution; native and Wasm builds stay serial and narrowly targeted under root control.

Before any CMake edit, archive its exact current bytes at catalogue/source-snapshots/<sha>/CMakeLists.txt. Current SHA is `5292c493bf8e55183a453fbab5cf2928f886673e65cbd85f234c9ba4b215ac71`, directly pinned by clay2014-rates-v1/preobservation-native.json (`/files/CMakeLists.txt`, original document SHA `1fb3eba88173da5666102320ce5cc795828cc29d85a1b2263e2abe0441bb53bf`). No existing sidecar is present there. Add a new source-archive-map.json beside that receipt, bind the original receipt document and exact snapshot, and create a new clay2014-paths-v1/source-migration-inventory.json. Preserve all original receipts/manifests/maps/inventories and indirect references unchanged; do not update historical pins to the new CMake. Verify the overlay in a disposable root with changed live CMake, corrupt/missing snapshot and original-document corruption checks before mutation. Recheck the actual latest committed baseline at installation, since website work may move HEAD. `baseline-receipts.json` records this read-only discovery; it is not an installed overlay or build receipt.

## Required sequence

1. Freeze independent reference code, explicit policy/inputs, converged output and reviewer report.
2. Use the frozen reference-policy budgets/floors/partition offset, and finalize only transport/assessment details before compiled observations.
3. Prepare and verify the additive CMake source archive against the latest committed baseline.
4. Add only the isolated solver target and implement/review collectors and strict assessor around the frozen reference API; run synthetic corruption tests.
5. Freeze complete source receipts, then serially build native/Wasm targets and retain artifact/descriptor receipts before matrix observations.
6. Execute serial actual native/Wasm matrices, retain all raw failures before assessment, and freshly reassess both reports/raw companions/parity.
7. Retain a bounded finite-path result, with source choices and unresolved physical/calibration/publisher/IGS gates still explicit. No scientific/public admission follows automatically.
