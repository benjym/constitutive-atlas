"""Pure source audit replay on saved responses; forbid process/material calls."""
from pathlib import Path
import hashlib,json,runpy,subprocess,sys
P=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
original_write=Path.write_text;original_mkdir=Path.mkdir;original_run=subprocess.run
writes=[]
def write(path,text,*args,**kwargs):
    assert path==P/'wasm-source-results.json'
    assert text==path.read_text(),'Saved source audit report changed'
    writes.append(str(path))
    return original_write(OUT/'saved-wasm-source-replayed-report.json',text,*args,**kwargs)
def mkdir(path,*args,**kwargs):assert path.is_dir(),path
def forbid(*args,**kwargs):raise AssertionError('Reviewer must not invoke processes/materials')
Path.write_text=write;Path.mkdir=mkdir;subprocess.run=forbid
try:
    try:runpy.run_path(str(P/'check_wasm_source.py'),run_name='__main__')
    except SystemExit as result:assert result.code==0
finally:
    Path.write_text=original_write;Path.mkdir=original_mkdir;subprocess.run=original_run
assert len(writes)==1
report=json.loads((P/'wasm-source-results.json').read_bytes());assert report['passed'] and len(report['checks'])==6986 and all(c['passed'] for c in report['checks'])
groups={}
for row in report['checks']:
    key=row['name'].rsplit('_',1)[-1];groups[key]=groups.get(key,0)+1
result={'passed':True,'checks':len(report['checks']),'scope':'Saved-source audit report byte-identical; process calls forbidden; no material execution','report_sha256':hashlib.sha256((P/'wasm-source-results.json').read_bytes()).hexdigest(),'check_suffix_counts':groups}
(OUT/'saved-wasm-source-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
