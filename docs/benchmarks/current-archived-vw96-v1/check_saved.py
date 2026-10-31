"""Reconstruct the study from public pinned inputs and saved observations only."""
import importlib.util
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('vw96_engine_study',HERE/'study.py')
STUDY=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(STUDY)
# Only offline source/input lookup changes. The frozen study code remains exact.
STUDY.ROOT=HERE/'inputs'
if __name__=='__main__':
    result=STUDY.audit(HERE/'observations')
    STUDY.require(result==STUDY.read(HERE/'observations/results.json'),'saved scalar result differs')
    print(json.dumps({'saved_reconstruction':'pass','native_processes_reconstructed':result['native_processes'],
                      'overall_compatibility_pass':result['overall_compatibility_pass'],'new_native_calls':0},indent=2))
