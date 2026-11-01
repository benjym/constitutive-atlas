"""Run the unchanged historical closure in a fresh exact-source temp tree.

No pin rewrite, current-root claim, solver execution or review promotion.
"""
import argparse,hashlib,json,runpy,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
DOC='docs/ingestion/barodesy-clay-2017/production-closure-v1/pins.json'
def reconstruct():
    pins=json.loads((ROOT/DOC).read_text());selected={}
    with tempfile.TemporaryDirectory(prefix='barodesy2017-review-closure-') as temp:
        base=Path(temp)
        for name,pin in pins['files'].items():
            source=checked_receipt(ROOT,DOC,name,pin);data=source.read_bytes()
            assert hashlib.sha256(data).hexdigest()==pin
            out=base/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            selected[name]=str(source.relative_to(ROOT))
        out=base/DOC;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/DOC).read_bytes())
        original=runpy.run_path(str(base/'docs/ingestion/barodesy-clay-2017/production-closure-v1/preflight.py'))['preflight']()
    return {'version':'barodesy2017-agent-original-closure-reconstruction-v1','pass':True,'exact_original_preflight_result':original,'restored_changed_paths':{k:v for k,v in selected.items() if k!=v},'current_root_preflight_passed':False,'new_scientific_review_inferred_from_old_preflight':False,'compiled_execution':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(reconstruct(),indent=2)+'\n')
