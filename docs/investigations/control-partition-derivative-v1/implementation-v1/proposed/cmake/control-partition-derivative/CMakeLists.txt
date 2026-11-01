cmake_minimum_required(VERSION 3.20)
project(AtlasControlPartitionDerivative LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
include("${ATLAS_ROOT}/cmake/AtlasScalarFunctions.cmake")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB ATLAS_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py" "${ATLAS_ROOT}/schemas/*.json")
set(FIXTURE "${ATLAS_ROOT}/tests/fixtures/control-partition-derivative")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -B -m atlas.compiler "${CMAKE_BINARY_DIR}/generated" "${FIXTURE}"
  DEPENDS "${FIXTURE}/residual.json" "${FIXTURE}/rate.json" ${ATLAS_INPUTS}
  WORKING_DIRECTORY "${ATLAS_ROOT}" VERBATIM)
add_custom_target(atlas_control_partition_derivative_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_control_partition_derivative_fixture EXCLUDE_FROM_ALL "${FIXTURE}/main.cpp")
add_dependencies(atlas_control_partition_derivative_fixture atlas_control_partition_derivative_models)
target_include_directories(atlas_control_partition_derivative_fixture PRIVATE "${ATLAS_ROOT}/cpp/include" "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_control_partition_derivative_fixture PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_control_partition_derivative_fixture PRIVATE -fexceptions)
  set_target_properties(atlas_control_partition_derivative_fixture PROPERTIES OUTPUT_NAME control-partition-derivative SUFFIX ".mjs")
  target_link_options(atlas_control_partition_derivative_fixture PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sENVIRONMENT=node" "-sALLOW_MEMORY_GROWTH=1"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
