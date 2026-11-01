# CMake generated Testfile for 
# Source directory: /private/tmp/atlas-control-partition-v1/source
# Build directory: /private/tmp/atlas-control-partition-v1/native-md-v4
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test("atlas_numerical" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_numerical_tests")
set_tests_properties("atlas_numerical" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;56;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_recorded" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_recorded_tests")
set_tests_properties("atlas_recorded" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;60;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_tensor_square" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_tensor_square_tests")
set_tests_properties("atlas_tensor_square" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;63;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_python" "/opt/homebrew/Frameworks/Python.framework/Versions/3.14/bin/python3.14" "-m" "unittest" "discover" "-s" "tests" "-v")
set_tests_properties("atlas_python" PROPERTIES  ENVIRONMENT "ATLAS_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_solver;ATLAS_TIME_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_time_solver;ATLAS_RESEARCH_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_research_solver;ATLAS_HISTORY_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_history_solver;ATLAS_CLAY2013_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_clay2013_solver;ATLAS_GIS2024_SOLVER=/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_gis2024_solver" WORKING_DIRECTORY "/private/tmp/atlas-control-partition-v1/source" _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;64;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_time" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_time_tests")
set_tests_properties("atlas_time" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;89;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_capacity" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_capacity_tests")
set_tests_properties("atlas_capacity" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;93;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_recorded_fixture" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_recorded_fixture_tests")
set_tests_properties("atlas_recorded_fixture" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;97;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_expm_context" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_expm_probe" "0,0,0,0,0,0" "1")
set_tests_properties("atlas_expm_context" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;196;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_log1p_context" "/private/tmp/atlas-control-partition-v1/native-md-v4/atlas_log1p_probe" "0")
set_tests_properties("atlas_log1p_context" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;219;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
add_test("atlas_scalar_functions" "/opt/homebrew/Frameworks/Python.framework/Versions/3.14/bin/python3.14" "/private/tmp/atlas-control-partition-v1/source/tools/test_scalar_functions.py" "/private/tmp/atlas-control-partition-v1/native-md-v4/libatlas_scalar_probe.dylib")
set_tests_properties("atlas_scalar_functions" PROPERTIES  _BACKTRACE_TRIPLES "/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;351;add_test;/private/tmp/atlas-control-partition-v1/source/CMakeLists.txt;0;")
