# Standard Linear Solid examples

Build the isolated common-engine target serially:

```sh
cmake -S cmake/sls -B /private/tmp/atlas-sls -DCMAKE_BUILD_TYPE=Debug
cmake --build /private/tmp/atlas-sls --target atlas_sls_solver --parallel 1
python3 -m atlas.cli run examples/sls/creep-schedule.json --solver /private/tmp/atlas-sls/atlas_sls_solver --output /private/tmp/sls-creep.json
```

The examples use explicit twelve-component strain/branch-overstress state and illustrative SI parameters. Relaxation holds strain, creep holds stress, and load/hold/reversal demonstrates the ordered history. The long-term shear stiffness is nonzero. No specimen preparation, calibration or experimental prediction is implied. Scientific findings and exact qualification scope are recorded in the model dossier.
