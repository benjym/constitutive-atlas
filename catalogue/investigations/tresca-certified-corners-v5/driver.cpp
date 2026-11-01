#define main atlas_original_cli_main
#include "frozen/cpp/main.cpp"
#undef main
#include "atlas/checked_principal_range.hpp"
#include <bit>
#include "corpus.inc"
#include "history.inc"
#include "checks.inc"
#include "laboratory.inc"
#include "reversal.inc"
int main(int argc,char**argv){if(argc!=2)return 2;std::string mode=argv[1];if(mode=="corpus")return corpus_study::run();if(mode=="history")return history_study::run();if(mode=="checks")return checks_study::run();if(mode=="reversal")return reversal_study::run();if(mode=="laboratory")return laboratory_run();return 2;}
