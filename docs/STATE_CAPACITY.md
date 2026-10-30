# State and derivative capacity

The common engine supports **32 scalar state components** in both schema versions. A symmetric Mandel tensor occupies six components. Physical-time mixed control reserves six further AD columns, giving **38 simultaneous unknowns**. This accommodates SANISAND's provisional 25-component persistent layout, or 26 including a residual multiplier, without removing reversal memory. It does not establish that model's equations or history semantics.

`atlas.model.MAX_STATE_COMPONENTS` bounds semantic validation; `max_state` and `max_derivatives` bound C++ storage. Generated catalogues contain a compile-time assertion against their actual largest layout, including all six controls. Timed-run JSON accepts at most 32 initial values; runtime ABI calls require the exact selected model's layout. Definitions exceeding 32 are rejected before code generation. The observable-count limit is separate and unchanged.

## Analytical verification fixture

`tests/fixtures/time/capacity-32.json` is an engine fixture, excluded from the public model catalogue. Its 32 components are stress `sigma[6]`, 25 scalar histories and a final scalar memory `m`. With `E=1000 Pa`, `P=10 Pa`, `tau=2 s`, and Mandel vector `a=(1,2,3,4,5,6)`, the equations are:

```
sigma_dot = E strain_rate + P m a / tau
history_i_dot = i / tau                  (i=1,...,25)
m_dot = (1-m) / tau
```

Under six stress holds and `m(0)=1`, the exact solution is constant stress, `history_i(t)=i t/tau` and `strain_j(t)=-P a_j t/(E tau)`. The native/Wasm schedule test supplies all 32 initial components explicitly, checks every final state and all six strains against these expressions, and compares the complete output trajectories. A second native/Wasm schedule starts with `m(0)=2` and checks exponential decay and its integrated creep against the exact continuum solution at declared absolute tolerances (`5e-6` in memory, `3e-8` in strain). Both ABIs must return a structured error for an overlong initial vector.

The native C++ test starts with `m(0)=2` and takes a backward-Euler step `h=0.5 s`. Independently solving the scalar balance gives `m_new=(2+h/tau)/(1+h/tau)=1.8`; stress holds then give `delta_strain_j=-h P m_new a_j/(E tau)`. This exercises the highest state column during a real 38-unknown Newton solve. Every entry of the 38-by-38 residual Jacobian is also checked against central finite differences; explicit assertions require nonzero highest-state coupling and all six control columns. Python boundary tests accept 32, reject 33 and admit a synthetic 26-component legacy residual/multiplier layout. Two negative compile tests deliberately reduce state or control derivative storage and require the generated capacity assertion to reject both.

## Reproduction

```sh
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
cmake --build build-wasm --parallel 2
node tools/test_schedule_wasm.mjs
```

The overflow test revealed an existing build defect: Wasm exception catching had only been enabled at link time. All three Wasm targets now compile and link with `-fexceptions`, as required by the [Emscripten exception documentation](https://emscripten.org/docs/porting/exceptions.html), so C++ ABI validation errors reach their existing JSON catch handlers.

Existing five-model analytical/reference checks and native/Wasm protocols remain regression gates. This is capacity verification, not SANISAND numerical validation or independent scientific review. Historical capability reports v1/v2 retain the earlier rejection evidence; v3 records the expanded boundary after its source commit.
