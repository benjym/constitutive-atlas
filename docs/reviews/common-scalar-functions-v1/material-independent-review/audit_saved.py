"""Read/hash saved artifacts and replay evidence only; no compiled execution."""
from pathlib import Path
import json,hashlib,re,shlex
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;S=B/'material-results-v1'
fail=[];pins={};counts={}
def digest(p):
    p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def check(ok,label):
    if not ok:fail.append(label)
def load(p):digest(p);return json.loads(Path(p).read_text())
freeze=load(B/'material-source-freeze-v1.json')
for p,h in freeze['files'].items():check(digest(p)==h,'source '+p)
prior=load(O/'prospective-receipt.json')
for p,h in prior['files'].items():check(digest(R/p)==h,'prospective binding '+p)
durable=load(S/'artifact-receipt.json')['artifacts']
for p,h in durable.items():check(digest(R/p)==h,'durable '+p)
for backend in ['native','wasm']:
    audit=load(S/f'{backend}-build-audit-v2.json');check(audit['status']=='passed','saved audit status '+backend)
    check(len(audit['commands'])==len(audit['objects'])==14,'14 commands/objects '+backend)
    build=Path(audit['commands'][0]['directory'])
    check(load(build/'compile_commands.json')==audit['commands'],'actual compile commands '+backend)
    actual_link=build/'CMakeFiles/atlas_duncan_api.dir/link.txt';digest(actual_link)
    check(actual_link.read_text()==audit['link'],'actual link '+backend)
    expanded=[]
    for cmd in audit['commands']:
        args=shlex.split(cmd['command']);check(args.count('-ffp-contract=off')==1,'contraction '+cmd['file'])
        for token in args:
            check(not (token in ['-ffast-math','-Ofast','-funsafe-math-optimizations','-fassociative-math','-freciprocal-math','-flto'] or token.startswith('-ffp-contract=') and token!='-ffp-contract=off'),'unsafe flags '+token)
            if token.startswith('@'):
                p=build/token[1:];digest(p);expanded.append(p.read_text())
        check(cmd['file'] in freeze['files'],'compiled source belongs to freeze '+cmd['file'])
    check(not any('-ffast-math' in x or '-ffp-contract=fast' in x for x in expanded),'response flags '+backend)
    for p,text in audit['response_files'].items():
        digest(p);check(Path(p).read_text()==text,'link response '+p)
    check('libatlas_scalar_functions.a' in audit['link']+' '.join(audit['response_files'].values()),'common archive linkage '+backend)
    archive=build/'libatlas_scalar_functions.a';digest(archive)
    for obj in audit['objects']:
        check(digest(obj['path'])==obj['sha256'],'object '+obj['path'])
        if backend=='native':
            p=Path(obj['assembly']);check(digest(p)==obj['assembly_sha256'],'assembly '+str(p))
            check(not re.search(r'\b(?:v?fmadd\w*|v?fmsub\w*|v?fnmadd\w*|v?fnmsub\w*|fmla|fmls)\b',p.read_text()),'saved fused assembly '+str(p))
    for p,h in audit['artifacts'].items():
        check(digest(p)==h,'built artifact '+p)
        check(h in durable.values(),'durable artifact matches built '+p)
    raw=load(S/f'{backend}-results.json')
    check(raw['artifact_sha256']==next(iter(audit['artifacts'].values())),'collector main artifact '+backend)
    if backend=='wasm':check(raw['wasm_sha256']==audit['artifacts'][str(build/'duncan.wasm')],'collector Wasm artifact')
    assessment=load(O/f'{backend}-assessment-replay.json');original=load(S/f'{backend}-assessment.json')
    check(assessment==original and assessment['pass_'],'full source replay '+backend)
    partition=load(O/f'{backend}-partition-replay.json');check(partition['pass_'] and partition['calls']==6248 and partition['retry_calls']==4,'partition replay '+backend)
    counts[backend]=dict(commands=14,objects=14,partition=partition,endpoint_max_normalized_error=assessment['summary']['endpoint_max_normalized_error'])
parity=load(O/'parity-replay.json');check(parity==load(S/'parity-results.json') and parity['pass_'],'parity replay equality')
check(parity['state_components_compared']==49616 and parity['worst_normalized_state_difference']==0,'49616 numeric state parity')
result=dict(identity='common-scalar-duncan-saved-independent-v1',pass_=not fail,failures=fail,backends=counts,parity=parity,compiled_execution=False,checked_files=pins)
(O/'saved-audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checked_files'},indent=2));raise SystemExit(bool(fail))
