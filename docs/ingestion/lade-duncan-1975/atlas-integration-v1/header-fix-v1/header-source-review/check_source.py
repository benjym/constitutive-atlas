from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[5];P=H.parent;sha=lambda b:hashlib.sha256(b).hexdigest()
before=(P/'app-before.js').read_bytes();after=(P/'app-proposed.js').read_bytes();proposal=json.loads((P/'PROPOSAL.json').read_bytes());s=proposal['source']
assert sha(before)==s['old_sha256'] and sha(after)==s['new_sha256'] and (R/'web/app.js').read_bytes()==before
text=after.decode();start=text.index("    if(active&&id==='lade-duncan-1975-midpoint-elastic-eq19-gap-v4'){");end=text.index("    $('import-run').hidden=active;",start)
assert (text[:start]+text[end:]).encode()==before
block=text[start:end];assert block.count("$('model-description').textContent=")==1 and block.count("$('model-family').textContent=")==1 and block.count("$('model-status').textContent=")==1
assert 'const active=timedView.select(id);\n    if(active)' in text
assert all(x in block for x in ['small strain','compression-positive total mechanical stress','fixed axes and zero pore pressure','Custom paths remain exploratory','https://doi.org/10.1061/AJGEB6.0000204','./engine-implicit-path/review.json','./engine-implicit-path/approval.json','./engine-implicit-path/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.json'])
assert all(x in (R/'tools/build_implicit_path_laboratory.py').read_text() for x in ["'approval.json':approval_bytes","'review.json':review_bytes","MODEL_ID+'.json':definition"])
model=json.loads((R/'models/research/implicit-path/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.json').read_bytes());assert model['sources'][0]['url']=='https://doi.org/10.1061/AJGEB6.0000204'
(H/'source-check-results.json').write_text(json.dumps(dict(passed=True,exact_added_header_lines=len(block.splitlines()),otherwise_byte_identical=True,production_app_unchanged=True,compiledCalls=0),indent=2)+'\n')
print('PASS exact isolated header block; live app unchanged; source/package link identities verified')
