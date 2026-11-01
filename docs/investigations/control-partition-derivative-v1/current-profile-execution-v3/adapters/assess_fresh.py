"""Fresh-output dispatcher to unchanged dedicated profile assessment functions."""
import argparse,importlib.util,json,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve()
OUT=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve()
assert OUT.is_dir()and not OUT.is_relative_to(ROOT)
sys.path.insert(0,str(ROOT))
p=argparse.ArgumentParser();p.add_argument('profile',choices=['orthotropic','j2']);p.add_argument('--raw',type=Path);p.add_argument('--main',type=Path);p.add_argument('--defaults',type=Path);p.add_argument('--paths',type=Path);p.add_argument('--report-name',required=True);a=p.parse_args()
assert Path(a.report_name).name==a.report_name and not(OUT/a.report_name).exists()
def read(p):return json.loads(p.read_text())
if a.profile=='orthotropic':
 from tools.orthotropic_reference import assess
 report=assess(read(ROOT/'docs/ingestion/orthotropic-ogs/execution-v1/references.json')['cases'],read(a.raw))
else:
 from tools.study_j2 import assess_rows
 base=ROOT/'docs/ingestion/j2-linear-hardening/execution-v2'
 spec=importlib.util.spec_from_file_location('j2_history_assessor',base/'check_paths.py');history=importlib.util.module_from_spec(spec);spec.loader.exec_module(history)
 report={label:assess_rows(read(base/name)['cases'],read(path))for label,name,path in [('main','references.json',a.main),('defaults','default-references.json',a.defaults)]}
 specs=read(base/'paths.json')+[read(ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json')]
 report['paths_and_public_preset']=history.assess(specs,read(a.paths))
(OUT/a.report_name).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
