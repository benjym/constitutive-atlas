#!/usr/bin/env python3
"""Solver-only published-base extension of the unchanged bounded committed-blob audit."""
from pathlib import Path
import importlib.util,argparse
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/release-bindings-v1/audit.py'
spec=importlib.util.spec_from_file_location('published_binding_audit',SOURCE);audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).parent);a=p.parse_args()
 audit.TARGETS=['cpp/include/atlas/solver.hpp'];audit.run(a.output)
