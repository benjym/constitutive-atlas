cmake_minimum_required(VERSION 3.20)
project(AtlasIsolatedResearchV3 LANGUAGES C CXX)

# One reviewed declarative file, the ordinary compiler, and an existing generic
# transport. This project neither packages nor promotes a public model.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
include("${ATLAS_ROOT}/cmake/AtlasScalarFunctions.cmake")
set(ATLAS_MODEL_FILE "" CACHE FILEPATH "One declarative research model JSON file")
set(ATLAS_RESEARCH_TRANSPORT rate CACHE STRING "Transport: rate or integrate")
set_property(CACHE ATLAS_RESEARCH_TRANSPORT PROPERTY STRINGS rate integrate)
if(NOT ATLAS_MODEL_FILE OR NOT EXISTS "${ATLAS_MODEL_FILE}" OR IS_DIRECTORY "${ATLAS_MODEL_FILE}")
  message(FATAL_ERROR "ATLAS_MODEL_FILE must name one existing JSON file")
endif()
get_filename_component(ATLAS_MODEL_FILE "${ATLAS_MODEL_FILE}" ABSOLUTE)
get_filename_component(ATLAS_MODEL_EXTENSION "${ATLAS_MODEL_FILE}" LAST_EXT)
if(NOT ATLAS_MODEL_EXTENSION STREQUAL ".json")
  message(FATAL_ERROR "ATLAS_MODEL_FILE must have .json extension")
endif()
if(ATLAS_RESEARCH_TRANSPORT STREQUAL "rate")
  set(ATLAS_DRIVER "${ATLAS_ROOT}/tests/research_rate_driver_v3.cpp")
elseif(ATLAS_RESEARCH_TRANSPORT STREQUAL "integrate")
  if(EMSCRIPTEN)
    set(ATLAS_DRIVER "${ATLAS_ROOT}/cpp/main.cpp")
  else()
    set(ATLAS_DRIVER "${ATLAS_ROOT}/tests/research_integrate_driver.cpp")
  endif()
else()
  message(FATAL_ERROR "ATLAS_RESEARCH_TRANSPORT must be rate or integrate")
endif()
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB ATLAS_COMPILER_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py" "${ATLAS_ROOT}/schemas/*.json")
set(ATLAS_GENERATED "${CMAKE_BINARY_DIR}/generated")
add_custom_command(
  OUTPUT "${ATLAS_GENERATED}/models.hpp" "${ATLAS_GENERATED}/models.json"
  COMMAND "${Python3_EXECUTABLE}" -B -c "from atlas.compiler import generate; from pathlib import Path; import sys; generate(Path(sys.argv[1]), [Path(sys.argv[2])])" "${ATLAS_GENERATED}" "${ATLAS_MODEL_FILE}"
  DEPENDS "${ATLAS_MODEL_FILE}" ${ATLAS_COMPILER_INPUTS}
  WORKING_DIRECTORY "${ATLAS_ROOT}"
  VERBATIM)
add_custom_target(atlas_isolated_model DEPENDS "${ATLAS_GENERATED}/models.hpp" "${ATLAS_GENERATED}/models.json")
add_executable(atlas_isolated EXCLUDE_FROM_ALL "${ATLAS_DRIVER}")
add_dependencies(atlas_isolated atlas_isolated_model)
target_include_directories(atlas_isolated PRIVATE "${ATLAS_ROOT}/cpp/include" "${ATLAS_GENERATED}")
target_compile_options(atlas_isolated PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_isolated PRIVATE -fexceptions)
  set_target_properties(atlas_isolated PROPERTIES OUTPUT_NAME atlas-isolated SUFFIX ".js")
  target_link_options(atlas_isolated PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
endif()
