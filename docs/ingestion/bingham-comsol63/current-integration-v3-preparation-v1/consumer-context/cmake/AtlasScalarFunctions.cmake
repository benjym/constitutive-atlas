# Common scalar source/rounding contract for supported live CMake consumers.
include_guard(DIRECTORY)
get_filename_component(ATLAS_SCALAR_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
if(NOT CMAKE_C_COMPILER_LOADED)
  message(FATAL_ERROR "Atlas scalar functions require project(... LANGUAGES C CXX)")
endif()
if(NOT CMAKE_C_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$" OR NOT CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
  message(FATAL_ERROR "Atlas scalar rounding contract currently supports GCC/Clang/Emscripten only")
endif()
if(NOT TARGET atlas_scalar_functions)
  add_library(atlas_scalar_functions STATIC
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/pow.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/pow_data.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/exp_data.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__math_xflow.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__math_uflow.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__math_oflow.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__math_invalid.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/sin.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__sin.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__cos.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__rem_pio2.c"
    "${ATLAS_SCALAR_ROOT}/cpp/scalar-functions/__rem_pio2_large.c")
  set_target_properties(atlas_scalar_functions PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED ON POSITION_INDEPENDENT_CODE ON)
  target_compile_options(atlas_scalar_functions PUBLIC -ffp-contract=off)
endif()
# Apply to subsequent targets in this consumer directory; actual commands audited.
link_libraries(atlas_scalar_functions)
