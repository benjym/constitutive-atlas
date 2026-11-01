#pragma once
// Bounded binary64 scalar functions; see docs/SCALAR_FUNCTIONS.md.
#ifdef __cplusplus
extern "C" {
#endif
double atlas_scalar_power(double base,double exponent);
double atlas_cyclic_sine(double argument);
#ifdef __cplusplus
}
#endif
