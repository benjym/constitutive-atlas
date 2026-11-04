# Proposed native-only addition; coordinator integrates after independent review.
# Uses current reviewed generic runtime/compiler and immutable historical records.
if(NOT EMSCRIPTEN)
  file(GLOB RECORDED_LEGACY_COMPILER CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/atlas/*.py")
  add_custom_command(
    OUTPUT "${CMAKE_BINARY_DIR}/recorded-legacy-generated/models.hpp" "${CMAKE_BINARY_DIR}/recorded-legacy-generated/models.json"
    COMMAND "${Python3_EXECUTABLE}" -B tools/generate_recorded_legacy_models.py "${CMAKE_BINARY_DIR}/recorded-legacy-generated"
    DEPENDS tools/generate_recorded_legacy_models.py tests/recorded_native_fixtures.py
      ${RECORDED_LEGACY_COMPILER} schemas/model.schema.json
      "${CMAKE_SOURCE_DIR}/catalogue/investigations/clay2005-preview-v1/models/drucker-prager.json"
      "${CMAKE_SOURCE_DIR}/catalogue/investigations/clay2005-preview-v1/models/hypoplastic-sand-igs97.json"
      "${CMAKE_SOURCE_DIR}/catalogue/investigations/clay2005-preview-v1/models/hypoplastic-sand-vw96.json"
      "${CMAKE_SOURCE_DIR}/catalogue/investigations/clay2005-preview-v1/models/linear-elastic.json"
      "${CMAKE_SOURCE_DIR}/catalogue/investigations/clay2005-preview-v1/models/modified-cam-clay.json"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
  add_custom_target(atlas_recorded_legacy_models DEPENDS "${CMAKE_BINARY_DIR}/recorded-legacy-generated/models.hpp" "${CMAKE_BINARY_DIR}/recorded-legacy-generated/models.json")
  add_executable(atlas_recorded_legacy_solver EXCLUDE_FROM_ALL cpp/main.cpp)
  add_dependencies(atlas_recorded_legacy_solver atlas_recorded_legacy_models)
  target_include_directories(atlas_recorded_legacy_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/recorded-legacy-generated")
  target_compile_options(atlas_recorded_legacy_solver PRIVATE -Wall -Wextra -Wno-unused-variable -ffp-contract=off)
  target_link_libraries(atlas_recorded_legacy_solver PRIVATE atlas_scalar_functions)
endif()
