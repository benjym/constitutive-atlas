"""Read saved responses only, retaining genuine eleven-model descriptors."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];F=ROOT/'docs/reviews/gis2024-v03-research-freeze-v1'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def gis(directory):
 a=mod('mixed_gis_assessor',HERE/'assess_gis.py');read=a.load
 return a.audit(read(directory/'result.json'),directory,read(HERE/'gis-model.json'),read(F/'trajectory-requests.json.gz'),read(F/'probes.json'),read(F/'policy.json'),read(ROOT/read(F/'policy.json')['reference']),read(HERE/'generated-eleven/models.json')['models'])
def existing(backend):
 a=mod('mixed_existing_assessor',HERE/'assess_existing.py');read=a.read
 old=a.compare_old(read(HERE/(backend+'-old-nine-responses.json')),backend)
 lab=mod('mixed_tresca_laboratory',HERE/'assess_laboratory.py').assess(read(HERE/(backend+'-laboratory-responses.json')),read(HERE/'laboratory-inputs.json'),read(HERE/'laboratory-references.json'),read(HERE/'laboratory-policy.json'),ROOT)
 history=mod('mixed_tresca_history',HERE/'assess_history.py').assess(read(HERE/(backend+'-history-responses.json')),read(HERE/'history-inputs.json'),ROOT)
 return {'old_nine':old,'tresca_laboratory':lab,'tresca_history':history,'qualification_pass':all(x['qualification_pass']for x in [old,lab,history])}
if __name__=='__main__':
 backend,directory=sys.argv[1:];out={'existing':existing(backend),'gis':gis(Path(directory))};out['compatibility_pass']=out['existing']['qualification_pass']and out['gis']['backend_qualification_pass'];print(json.dumps(out,indent=2));raise SystemExit(0 if out['compatibility_pass']else 1)
