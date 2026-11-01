
# Source-pinned Burgers continuous law: physical-time research catalogue.
# Dedicated timed APIs; no addition to the strain-path browser catalogue.
file(GLOB BURGERS_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/burgers/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/burgers-generated/models.hpp" "${CMAKE_BINARY_DIR}/burgers-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/burgers-generated" "${CMAKE_SOURCE_DIR}/models/research/burgers"
  DEPENDS ${BURGERS_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_burgers_models DEPENDS "${CMAKE_BINARY_DIR}/burgers-generated/models.hpp" "${CMAKE_BINARY_DIR}/burgers-generated/models.json")
add_executable(atlas_burgers_solver EXCLUDE_FROM_ALL cpp/main.cpp)
add_dependencies(atlas_burgers_solver atlas_burgers_models)
target_include_directories(atlas_burgers_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/burgers-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_burgers_solver PRIVATE -fexceptions)
  set_target_properties(atlas_burgers_solver PROPERTIES OUTPUT_NAME "burgers" SUFFIX ".mjs")
  get_target_property(BURGERS_WASM_OPTIONS atlas_solver LINK_OPTIONS)
  target_link_options(atlas_burgers_solver PRIVATE ${BURGERS_WASM_OPTIONS})
endif()
