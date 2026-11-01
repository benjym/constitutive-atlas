# J2 linear isotropic hardening examples

The model is a dry, small-strain, fixed-frame total-stress mathematical
backward-Euler specialization of OpenSees J2Plasticity. It uses the common Atlas
compiler and solver. The [source correction](../../docs/ingestion/j2-linear-hardening/CORRECTION-v2.md)
and [qualification](../../docs/ingestion/j2-linear-hardening/execution-v2/README.md)
explain its exact identity. Parameters in these examples are illustrative; they
are not calibrated experimental material constants.

Build one serial native target from the repository root:

```sh
cmake -S cmake/j2 -B build-j2 -DCMAKE_BUILD_TYPE=Release
cmake --build build-j2 --target atlas_j2_solver --parallel 1
python3 -B tools/run_j2.py build-j2/atlas_j2_solver examples/j2/reverse.json
python3 -B tools/run_j2.py build-j2/atlas_j2_solver examples/j2/nonproportional.json
```

`reverse.json` loads, unloads and reverses a deviatoric strain path;
`nonproportional.json` changes loading direction, includes shear and holds.
Every accepted endpoint becomes the next explicit input. State layout is six
Mandel stresses in Pa, equivalent plastic strain alpha, and the temporary
plastic multiplier gamma. Preserve sigma and alpha for physical restart; the
solver resets gamma at the next solve. A failed update returns the incoming
layout; the runner stops immediately. Strain components and stresses are
compression-positive, with shear entries multiplied by sqrt(2).

The examples explicitly choose `1e-11,1e-6,60,0,1,20` integration settings
(residual tolerance, rate tolerance, iteration limit, subdivision depth,
substep budget, backtracking limit). Subdivision is forbidden here to qualify
the stated single-step BE map. No physical duration, rate effect, relaxation,
pore pressure, finite rotation or stress-controlled protocol is implied.
For a curved continuous path, choose and refine the supplied strain increments;
a converged single BE solve does not establish path-discretization accuracy.

The optional Wasm build uses the same dedicated CMake project with `emcmake`
and the same serial explicit target. `tools/collect_j2_wasm.mjs` collects the
frozen study requests; `tools/collect_j2_paths.mjs` propagates actual history in
one module. Public browser catalogue packaging is a separate task.
