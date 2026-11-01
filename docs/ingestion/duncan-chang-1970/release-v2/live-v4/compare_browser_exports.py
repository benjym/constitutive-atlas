"""Compare actual Chrome exported full wire responses; only measured elapsed_ms is excluded."""
from pathlib import Path
import json,sys,hashlib
rows=[]
for label in ('default','dense','reset'):
    a=Path(sys.argv[1])/('upload-'+label+'-run.json');b=Path(sys.argv[1])/('live-'+label+'-run.json')
    x=json.loads(a.read_text());y=json.loads(b.read_text())
    for z in (x,y):
        assert z['result']['ok'] is True
        z['result'].pop('elapsed_ms')
    assert x==y, label+' complete specification/result mismatch'
    rows.append({'case':label,'upload_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'live_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'complete_export_equal_except_elapsed_ms':True,'points':len(x['result'].get('points',[]))})
out={'status':'PASS','source_commit':'0b1b15ac5f4c8038bce3b26a098d31116c28b537','workflow_run':41340720867,'cases':rows}
Path(__file__).with_name('browser-export-comparison-v1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
