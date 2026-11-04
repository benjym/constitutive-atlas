from pathlib import Path
import json,hashlib,sys
base=Path(__file__).resolve().parent
reference=base.parent/'public-qualification-v1/expected-results.json'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='3ce68543c2409c94b0f1d706ace0bb4d7b5795cee77f3da7bdce84e7513ed07c'
case=next(x for x in json.loads(reference.read_text())['cases'] if x['id']=='near_hold_1000')
path=Path(sys.argv[1]);actual=json.loads(path.read_text())
assert actual['model']=='vibe-2026' and actual['request']==case['request'] and actual['result']==case['result']
report={'case':case['id'],'request_exact':True,'complete_result_exact':True,'download_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'identity':actual['identity'],'model':actual['model']}
out=base/'live-default-comparison-v3.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: actual default request and complete result equal original frozen reference')
