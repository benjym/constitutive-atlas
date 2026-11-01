"""Project the exact independent reporting decision; never export private curves."""
import hashlib,html,json
from pathlib import Path
from tools.strict_observation_json import loads
PACKET=Path('docs/benchmarks/kfs-development-agent-v1')
CLAIMS={f'C{i}' for i in range(1,8)}
def _checked(root,manifest,path):
    raw=(root/path).read_bytes()
    expected=manifest.get('files',{}).get(str(path),manifest.get('public_audit_input_closure',{}).get(str(path)))
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Reporting review hash mismatch: '+str(path))
    return raw

def projection(root):
    root=Path(root);manifest=loads((root/PACKET/'manifest.json').read_bytes())
    raw=_checked(root,manifest,PACKET/'decision.json');decision=loads(raw)
    _checked(root,manifest,PACKET/'README.md')
    _checked(root,manifest,Path('docs/benchmarks/kfs-development-review-v1/manifest.json'))
    if (decision.get('kind')!='independent-agent-development-reporting-review' or
        decision.get('id')!='kfs-development-agent-v1' or decision.get('outcome')!='accept_qualified_reporting' or
        decision.get('reviewer',{}).get('agent')!='/root/kfs_development_review' or
        decision.get('blocking_corrections')!=[] or decision.get('redistribution_permission') is not False):
        raise ValueError('Unsupported reporting review decision')
    claims=decision.get('claim_decisions',[])
    if len(claims)!=7 or {c.get('id') for c in claims}!=CLAIMS or any(c.get('outcome')!='accept_qualified_reporting' for c in claims):
        raise ValueError('Incomplete reporting review claims')
    for key in ('mandatory_qualifications','excluded_claims'):
        if not decision.get(key) or not all(isinstance(v,str) and v.strip() for v in decision[key]):
            raise ValueError('Missing reporting review qualifications')
    return {'id':decision['id'],'outcome':decision['outcome'],'date':decision['date'],
            'reviewer':decision['reviewer']['agent'],'scope':decision['scope'],
            'claims':[{'id':c['id'],'title':c['title'],'reason':c['reason']} for c in claims],
            'qualifications':decision['mandatory_qualifications'],'excluded_claims':decision['excluded_claims'],
            'model_admission':False,'redistribution_permission':False,
            'decision_sha256':hashlib.sha256(raw).hexdigest(),
            'decision_url':'./reporting-review/decision.json','review_url':'./reporting-review/review.html'}

def bundle(destination,root):
    root=Path(root);projection(root) # Validate before writing.
    folder=Path(destination)/'reporting-review';folder.mkdir(parents=True,exist_ok=True)
    (folder/'decision.json').write_bytes((root/PACKET/'decision.json').read_bytes())
    text=(root/PACKET/'README.md').read_text()
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Independent KFS reporting review</title><style>body{max-width:85ch;margin:2rem auto;padding:0 1rem;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style><p><a href="../development.html">Development evidence</a> · <a href="./decision.json">Exact decision JSON</a></p><h1>Independent KFS reporting review</h1><pre>'+html.escape(text)+'</pre></html>'
    (folder/'review.html').write_text(page)
