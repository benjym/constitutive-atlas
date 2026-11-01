First source-only mock run: 16 methods, 1 failure and 14 subtest errors.
The synthetic fixture wrote the macOS /var alias to CMakeCache while dispatcher
canonicalized to /private/var. All positive routes therefore stopped at context
validation, and the row-corruption test observed zero calls. Fixed comparison
to require exactly one CMAKE_HOME_DIRECTORY whose resolved path equals the
resolved source root; canonicalized synthetic fixture base too. This does not
weaken catalogue, helper, policy, model or artifact hash gates. No builds or
compiled calls occurred. The initial raw tool output is retained in session.
