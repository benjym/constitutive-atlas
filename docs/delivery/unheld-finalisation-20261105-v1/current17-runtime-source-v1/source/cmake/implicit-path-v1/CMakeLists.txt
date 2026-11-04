cmake_minimum_required(VERSION 3.20)
project(AtlasImplicitPathV1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(PROFILE "${ATLAS_ROOT}/cpp/profiles/implicit-path-v1")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB COMPILER_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py" "${ATLAS_ROOT}/schemas/*.json")
file(GLOB MODEL_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/models/research/implicit-path/*.json" "${ATLAS_ROOT}/tests/fixtures/implicit-path-v1/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -B "${ATLAS_ROOT}/tools/generate_implicit_path.py" "${CMAKE_BINARY_DIR}/generated"
  DEPENDS ${COMPILER_INPUTS} ${MODEL_INPUTS} "${ATLAS_ROOT}/tools/generate_implicit_path.py"
  WORKING_DIRECTORY "${ATLAS_ROOT}" VERBATIM)
add_custom_target(atlas_implicit_path_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_implicit_path_v1 EXCLUDE_FROM_ALL "${PROFILE}/main.cpp")
add_dependencies(atlas_implicit_path_v1 atlas_implicit_path_models)
target_include_directories(atlas_implicit_path_v1 PRIVATE "${PROFILE}/include" "${CMAKE_BINARY_DIR}/generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_implicit_path_v1 PRIVATE -fexceptions)
  set_target_properties(atlas_implicit_path_v1 PROPERTIES OUTPUT_NAME "lade-domain" SUFFIX ".mjs")
  target_link_options(atlas_implicit_path_v1 PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createLadeGap"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
