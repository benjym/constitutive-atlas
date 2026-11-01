"""Reuse unchanged own-state driver and literal frozen GIS requests."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'docs/reviews/gis2024-v03-backends-v1'
s=importlib.util.spec_from_file_location('qualified_gis_driver',OLD/'driver.py');driver=importlib.util.module_from_spec(s);s.loader.exec_module(driver)
if __name__=='__main__':
 backend,executable,destination=sys.argv[1:];command=[executable]if backend=='native'else['node',str(OLD/'wasm_line.mjs'),executable];raise SystemExit(driver.execute(command,Path(destination),backend))
