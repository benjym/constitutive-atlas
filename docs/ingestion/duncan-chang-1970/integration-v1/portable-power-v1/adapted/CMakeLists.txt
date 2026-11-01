cmake_minimum_required(VERSION 3.20)
project(ConstitutiveAtlas VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Physical-time power-creep research law: opt-in, separate from public catalogue.
# Build explicitly with --target atlas_power_creep_solver --parallel 1.
file(GLOB POWER_CREEP_MODELS CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/power-creep/*.json")
file(GLOB POWER_CREEP_COMPILER CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/atlas/*.py")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/power-creep-generated/models.hpp" "${CMAKE_BINARY_DIR}/power-creep-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/power-creep-generated" "${CMAKE_SOURCE_DIR}/models/research/power-creep"
  DEPENDS ${POWER_CREEP_MODELS} ${POWER_CREEP_COMPILER} schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_power_creep_models DEPENDS "${CMAKE_BINARY_DIR}/power-creep-generated/models.hpp" "${CMAKE_BINARY_DIR}/power-creep-generated/models.json")
add_executable(atlas_power_creep_solver EXCLUDE_FROM_ALL cpp/main.cpp)
add_dependencies(atlas_power_creep_solver atlas_power_creep_models)
target_include_directories(atlas_power_creep_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/power-creep-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_power_creep_solver PRIVATE -fexceptions)
  set_target_properties(atlas_power_creep_solver PROPERTIES OUTPUT_NAME "power-creep" SUFFIX ".js")
  target_link_options(atlas_power_creep_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createPowerCreep"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
endif()
file(GLOB MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/generated"
  DEPENDS ${MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_solver cpp/main.cpp)
add_dependencies(atlas_solver atlas_models)
target_include_directories(atlas_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_solver PRIVATE -fexceptions)
  set_target_properties(atlas_solver PROPERTIES OUTPUT_NAME "atlas" SUFFIX ".js")
  target_link_options(atlas_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
else()
  enable_testing()
  add_executable(atlas_numerical_tests tests/test_solver.cpp)
  add_dependencies(atlas_numerical_tests atlas_models)
  target_include_directories(atlas_numerical_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
  add_test(NAME atlas_numerical COMMAND atlas_numerical_tests)
  add_executable(atlas_recorded_tests tests/test_recorded.cpp)
  add_dependencies(atlas_recorded_tests atlas_models)
  target_include_directories(atlas_recorded_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
  add_test(NAME atlas_recorded COMMAND atlas_recorded_tests)
  add_executable(atlas_tensor_square_tests tests/test_tensor_square.cpp)
  target_include_directories(atlas_tensor_square_tests PRIVATE cpp/include)
  add_test(NAME atlas_tensor_square COMMAND atlas_tensor_square_tests)
  add_test(NAME atlas_python COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s tests -v)
  set_tests_properties(atlas_python PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" ENVIRONMENT "ATLAS_SOLVER=$<TARGET_FILE:atlas_solver>;ATLAS_TIME_SOLVER=$<TARGET_FILE:atlas_time_solver>")
endif()

# Synthetic integration fixtures use the same compiler and engine, but a separate
# generated catalogue. They are never packaged as public atlas models.
file(GLOB TIME_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tests/fixtures/time/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/time-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/time-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/time"
  DEPENDS ${TIME_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_time_models DEPENDS "${CMAKE_BINARY_DIR}/time-generated/models.hpp")
add_executable(atlas_time_solver cpp/main.cpp)
add_dependencies(atlas_time_solver atlas_time_models)
target_include_directories(atlas_time_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_time_solver PRIVATE -fexceptions)
  set_target_properties(atlas_time_solver PROPERTIES OUTPUT_NAME "time-fixtures" SUFFIX ".js")
  get_target_property(ATLAS_WASM_OPTIONS atlas_solver LINK_OPTIONS)
  target_link_options(atlas_time_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  add_executable(atlas_time_tests tests/test_time.cpp)
  add_dependencies(atlas_time_tests atlas_time_models)
  target_include_directories(atlas_time_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
  add_test(NAME atlas_time COMMAND atlas_time_tests)
  add_executable(atlas_capacity_tests tests/test_capacity.cpp)
  add_dependencies(atlas_capacity_tests atlas_time_models)
  target_include_directories(atlas_capacity_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
  add_test(NAME atlas_capacity COMMAND atlas_capacity_tests)
  add_executable(atlas_recorded_fixture_tests tests/test_recorded_fixture.cpp)
  add_dependencies(atlas_recorded_fixture_tests atlas_time_models)
  target_include_directories(atlas_recorded_fixture_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
  add_test(NAME atlas_recorded_fixture COMMAND atlas_recorded_fixture_tests)
endif()

# Source-pinned research drafts stay separate from both admitted browser models
# and synthetic verification fixtures. They use exactly the same compiler/engine.
file(GLOB RESEARCH_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/research-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/research-generated" "${CMAKE_SOURCE_DIR}/models/research"
  DEPENDS ${RESEARCH_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_research_models DEPENDS "${CMAKE_BINARY_DIR}/research-generated/models.hpp")
add_executable(atlas_research_solver cpp/main.cpp)
add_dependencies(atlas_research_solver atlas_research_models)
target_include_directories(atlas_research_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/research-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_research_solver PRIVATE -fexceptions)
  set_target_properties(atlas_research_solver PROPERTIES OUTPUT_NAME "research" SUFFIX ".js")
  target_link_options(atlas_research_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  set_property(TEST atlas_python APPEND PROPERTY ENVIRONMENT "ATLAS_RESEARCH_SOLVER=$<TARGET_FILE:atlas_research_solver>")
endif()

# Experimental phased history is separate from model integration and admission.
file(GLOB HISTORY_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/fixtures/history/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/history-generated/history_programs.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.history_compiler "${CMAKE_BINARY_DIR}/history-generated" "${CMAKE_SOURCE_DIR}/fixtures/history"
  DEPENDS ${HISTORY_FILES} atlas/history_compiler.py atlas/history.py atlas/dsl.py atlas/structure.py schemas/history-program.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_executable(atlas_history_solver cpp/history_main.cpp "${CMAKE_BINARY_DIR}/history-generated/history_programs.hpp")
target_include_directories(atlas_history_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/history-generated")
target_compile_options(atlas_history_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_history_solver PRIVATE -fexceptions)
  set_target_properties(atlas_history_solver PROPERTIES OUTPUT_NAME "history-fixtures" SUFFIX ".js")
  target_link_options(atlas_history_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  set_property(TEST atlas_python APPEND PROPERTY ENVIRONMENT "ATLAS_HISTORY_SOLVER=$<TARGET_FILE:atlas_history_solver>")
endif()

# Isolated clay research catalogue preserves prior research evidence hashes.
file(GLOB CLAY2013_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/clay2013/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/clay2013-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/clay2013-generated" "${CMAKE_SOURCE_DIR}/models/research/clay2013"
  DEPENDS ${CLAY2013_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_clay2013_models DEPENDS "${CMAKE_BINARY_DIR}/clay2013-generated/models.hpp")
add_executable(atlas_clay2013_solver cpp/main.cpp)
add_dependencies(atlas_clay2013_solver atlas_clay2013_models)
target_include_directories(atlas_clay2013_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/clay2013-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_clay2013_solver PRIVATE -fexceptions)
  set_target_properties(atlas_clay2013_solver PROPERTIES OUTPUT_NAME "clay2013" SUFFIX ".js")
  target_link_options(atlas_clay2013_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  set_property(TEST atlas_python APPEND PROPERTY ENVIRONMENT "ATLAS_CLAY2013_SOLVER=$<TARGET_FILE:atlas_clay2013_solver>")
endif()

# Selected HP/extracted-ASBS+GIS has its own research catalogue and source identity.
file(GLOB GIS2024_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/gis2024/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/gis2024-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/gis2024-generated" "${CMAKE_SOURCE_DIR}/models/research/gis2024"
  DEPENDS ${GIS2024_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_gis2024_models DEPENDS "${CMAKE_BINARY_DIR}/gis2024-generated/models.hpp")
add_executable(atlas_gis2024_solver cpp/main.cpp)
add_dependencies(atlas_gis2024_solver atlas_gis2024_models)
target_include_directories(atlas_gis2024_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/gis2024-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_gis2024_solver PRIVATE -fexceptions)
  set_target_properties(atlas_gis2024_solver PROPERTIES OUTPUT_NAME "gis2024" SUFFIX ".js")
  target_link_options(atlas_gis2024_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  set_property(TEST atlas_python APPEND PROPERTY ENVIRONMENT "ATLAS_GIS2024_SOLVER=$<TARGET_FILE:atlas_gis2024_solver>")
endif()

# Bounded checked matrix-function conformance has an isolated synthetic catalogue.
file(GLOB EXPM_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tests/fixtures/expm/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/expm-generated/models.hpp" "${CMAKE_BINARY_DIR}/expm-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/expm-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/expm"
  DEPENDS ${EXPM_MODEL_FILES} atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/expm-history-generated/history_programs.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.history_compiler "${CMAKE_BINARY_DIR}/expm-history-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/expm-history"
  DEPENDS tests/fixtures/expm-history/expm.json atlas/history.py atlas/history_compiler.py atlas/dsl.py atlas/symmetric_expm.py atlas/scalar_math.py atlas/structure.py
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_executable(atlas_expm_probe tests/expm_driver.cpp "${CMAKE_BINARY_DIR}/expm-generated/models.hpp" "${CMAKE_BINARY_DIR}/expm-history-generated/history_programs.hpp")
target_include_directories(atlas_expm_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/expm-generated" "${CMAKE_BINARY_DIR}/expm-history-generated")
target_compile_options(atlas_expm_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_expm_probe PRIVATE -fexceptions)
  set_target_properties(atlas_expm_probe PROPERTIES OUTPUT_NAME "expm-fixtures" SUFFIX ".js")
  target_link_options(atlas_expm_probe PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  add_test(NAME atlas_expm_context COMMAND atlas_expm_probe "0,0,0,0,0,0" "1")
endif()

# Stable scalar log1p is verified in an isolated expression/history catalogue.
file(GLOB LOG1P_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tests/fixtures/log1p/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/log1p-generated/models.hpp" "${CMAKE_BINARY_DIR}/log1p-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/log1p-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/log1p"
  DEPENDS ${LOG1P_MODEL_FILES} atlas/dsl.py atlas/scalar_math.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json schemas/model-v0.3.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/log1p-history-generated/history_programs.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.history_compiler "${CMAKE_BINARY_DIR}/log1p-history-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/log1p-history"
  DEPENDS tests/fixtures/log1p-history/log1p.json atlas/history.py atlas/history_compiler.py atlas/dsl.py atlas/scalar_math.py atlas/structure.py
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_executable(atlas_log1p_probe tests/log1p_driver.cpp "${CMAKE_BINARY_DIR}/log1p-generated/models.hpp" "${CMAKE_BINARY_DIR}/log1p-history-generated/history_programs.hpp")
target_include_directories(atlas_log1p_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/log1p-generated" "${CMAKE_BINARY_DIR}/log1p-history-generated")
target_compile_options(atlas_log1p_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_log1p_probe PRIVATE -fexceptions)
  set_target_properties(atlas_log1p_probe PROPERTIES OUTPUT_NAME "log1p-fixtures" SUFFIX ".js")
  target_link_options(atlas_log1p_probe PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  add_test(NAME atlas_log1p_context COMMAND atlas_log1p_probe "0")
endif()

# Suggested additive isolated target. Root reviews/inserts after existing targets.
# Does not alter normal public models/*.json generation or publish research assets.
file(GLOB BARODESY_RATE_MODELS CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/barodesy2017/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/barodesy-rate-generated/models.hpp" "${CMAKE_BINARY_DIR}/barodesy-rate-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/barodesy-rate-generated" "${CMAKE_SOURCE_DIR}/models/research/barodesy2017"
  DEPENDS ${BARODESY_RATE_MODELS} atlas/dsl.py atlas/scalar_math.py atlas/symmetric_expm.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_barodesy_models DEPENDS "${CMAKE_BINARY_DIR}/barodesy-rate-generated/models.hpp" "${CMAKE_BINARY_DIR}/barodesy-rate-generated/models.json")
add_executable(atlas_barodesy_rate_probe tests/barodesy_rate_driver.cpp)
add_dependencies(atlas_barodesy_rate_probe atlas_barodesy_models)
target_include_directories(atlas_barodesy_rate_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/barodesy-rate-generated")
target_compile_options(atlas_barodesy_rate_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_barodesy_rate_probe PRIVATE -fexceptions)
  set_target_properties(atlas_barodesy_rate_probe PROPERTIES OUTPUT_NAME "barodesy-rates" SUFFIX ".js")
  target_link_options(atlas_barodesy_rate_probe PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createBarodesyRates"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
# No automatic native execution is introduced by this suggestion.

# Add after the isolated rate target/custom generation from prior packet.
# Shares its generated models.hpp, not the production public catalogue.
add_executable(atlas_barodesy_material_ad_probe tests/barodesy_material_ad_driver.cpp)
add_dependencies(atlas_barodesy_material_ad_probe atlas_barodesy_models)
target_include_directories(atlas_barodesy_material_ad_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/barodesy-rate-generated")
target_compile_options(atlas_barodesy_material_ad_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_barodesy_material_ad_probe PRIVATE -fexceptions)
  set_target_properties(atlas_barodesy_material_ad_probe PROPERTIES OUTPUT_NAME "barodesy-material-ad" SUFFIX ".js")
  target_link_options(atlas_barodesy_material_ad_probe PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createBarodesyMaterialAD"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
# No automatic native execution or test registration.

# Integrate after the existing atlas_barodesy_models shared generation target.
# No second custom command and no automatic native execution.
add_executable(atlas_barodesy_solver cpp/main.cpp)
add_dependencies(atlas_barodesy_solver atlas_barodesy_models)
target_include_directories(atlas_barodesy_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/barodesy-rate-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_barodesy_solver PRIVATE -fexceptions)
  set_target_properties(atlas_barodesy_solver PROPERTIES OUTPUT_NAME "barodesy-isotropic" SUFFIX ".js")
  target_link_options(atlas_barodesy_solver PRIVATE ${ATLAS_WASM_OPTIONS})
endif()

# Add after shared isolated atlas_barodesy_models generation.
# No production model, regular driver, or normal catalogue changes.
add_executable(atlas_barodesy_hydro_ad_probe tests/barodesy_hydro_ad_driver.cpp)
add_dependencies(atlas_barodesy_hydro_ad_probe atlas_barodesy_models)
target_include_directories(atlas_barodesy_hydro_ad_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/barodesy-rate-generated")
target_compile_options(atlas_barodesy_hydro_ad_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_barodesy_hydro_ad_probe PRIVATE -fexceptions)
  set_target_properties(atlas_barodesy_hydro_ad_probe PROPERTIES OUTPUT_NAME "barodesy-hydro-ad" SUFFIX ".js")
  target_link_options(atlas_barodesy_hydro_ad_probe PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createBarodesyHydroAD"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()

# Isolated fixed-plane clay2014 research definition; excluded from public models.
file(GLOB CLAY2014_MODELS CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/clay2014/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/clay2014-generated/models.hpp" "${CMAKE_BINARY_DIR}/clay2014-generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/clay2014-generated" "${CMAKE_SOURCE_DIR}/models/research/clay2014"
  DEPENDS ${CLAY2014_MODELS} atlas/dsl.py atlas/scalar_math.py atlas/symmetric_expm.py atlas/model.py atlas/compiler.py atlas/stress.py atlas/structure.py schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_clay2014_models DEPENDS "${CMAKE_BINARY_DIR}/clay2014-generated/models.hpp" "${CMAKE_BINARY_DIR}/clay2014-generated/models.json")
add_executable(atlas_clay2014_rate_probe tests/research_rate_driver.cpp)
add_dependencies(atlas_clay2014_rate_probe atlas_clay2014_models)
target_include_directories(atlas_clay2014_rate_probe PRIVATE cpp/include "${CMAKE_BINARY_DIR}/clay2014-generated")
target_compile_options(atlas_clay2014_rate_probe PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_clay2014_rate_probe PRIVATE -fexceptions)
  set_target_properties(atlas_clay2014_rate_probe PROPERTIES OUTPUT_NAME "clay2014-rates" SUFFIX ".js")
  target_link_options(atlas_clay2014_rate_probe PRIVATE ${ATLAS_WASM_OPTIONS})
endif()

# Explicit finite-path study target; same research catalogue and common engine.
# Kept out of default builds and public browser packaging.
if(EMSCRIPTEN)
  add_executable(atlas_clay2014_solver EXCLUDE_FROM_ALL cpp/main.cpp)
else()
  add_executable(atlas_clay2014_solver EXCLUDE_FROM_ALL tests/research_integrate_driver.cpp)
endif()
add_dependencies(atlas_clay2014_solver atlas_clay2014_models)
target_include_directories(atlas_clay2014_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/clay2014-generated")
target_compile_options(atlas_clay2014_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_clay2014_solver PRIVATE -fexceptions)
  set_target_properties(atlas_clay2014_solver PROPERTIES OUTPUT_NAME "clay2014-paths" SUFFIX ".js")
  target_link_options(atlas_clay2014_solver PRIVATE ${ATLAS_WASM_OPTIONS})
endif()

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

# Isolated generic arithmetic diagnostic; no production installation.
enable_language(C)
target_sources(atlas_solver PRIVATE diagnostic_pow/pow.c diagnostic_pow/pow_data.c diagnostic_pow/exp_data.c diagnostic_pow/__math_xflow.c diagnostic_pow/__math_uflow.c diagnostic_pow/__math_oflow.c diagnostic_pow/__math_invalid.c)
