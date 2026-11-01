"""Reuse the unchanged ten-model collection procedure in a fresh evidence directory."""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
s=importlib.util.spec_from_file_location('frozen_ten_collection',ROOT/'catalogue/investigations/tresca-mixed-catalogue-v1/study.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.P=HERE;m.STAGE=Path('/private/tmp/atlas-gis2024-mixed-catalogue-v1')
if __name__=='__main__':m.collect(sys.argv[1])
