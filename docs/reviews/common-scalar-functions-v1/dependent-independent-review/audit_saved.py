"""Hash saved dependent build/source/artifact evidence; no compiled execution."""
from pathlib import Path
import json,hashlib,shlex,re,subprocess,sys
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;S=B/'dependent-results-v1';pins={};fail=[]
def sha(p):
    p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def load(p):sha(p);return json.loads(Path(p).read_text())
def check(ok,label):
    if not ok:fail.append(label)
freeze=load(B/'dependent-source-freeze-v1.json');src=Path(freeze['source'])
prior=load(O/'prospective-bindings-v1.json')
for p,h in prior['files'].items():check(sha(R/p)==h,'prospective binding '+p)
consumer=load(B/'consumer-source-freeze-v1.json');croot=Path(consumer['source'])
for p,h in consumer['files'].items():check(sha(p)==h and sha(src/Path(p).relative_to(croot))==h,'consumer/dependent equivalence '+p)
durable=load(S/'artifact-receipt.json')['artifacts'];consumerdurable=load(B/'consumer-results-v1/artifact-receipt.json')['artifacts'];maxdurable={p:h for p,h in consumerdurable.items() if '/maxwell/' in p}
check(len(maxdurable)==3,'three durable Maxwell artifacts')
for p,h in (durable|maxdurable).items():check(sha(R/p)==h,'durable '+p)
counts={}
for model in ['maxwell','norsand']:
 for backend in ['native','wasm']:
    folder=(B/'consumer-results-v1' if model=='maxwell' else S)/backend/model
    audit=load(folder/'build-audit.json');check(audit['status']=='passed','saved audit '+str(folder))
    check(len(audit['commands'])==len(audit['objects'])==13,'13 actual commands/objects '+str(folder))
    build=Path(audit['commands'][0]['directory']);check(load(build/'compile_commands.json')==audit['commands'],'actual commands '+str(folder))
    linkpath=build/'CMakeFiles'/('atlas_maxwell_solver.dir' if model=='maxwell' else 'atlas_path_capability.dir')/'link.txt';sha(linkpath);check(linkpath.read_text()==audit['link'],'actual link '+str(folder))
    for c in audit['commands']:
        args=shlex.split(c['command']);check('-O3' in args and '-DNDEBUG' in args and args.count('-ffp-contract=off')==1,'Release/contraction '+c['file'])
        check(not any(x in args for x in ['-ffast-math','-Ofast','-funsafe-math-optimizations','-ffp-contract=fast','-ffp-contract=on','-flto']),'unsafe flag '+c['file'])
        sha(c['file'])
        for x in args:
            if x.startswith('@'):
                p=build/x[1:];sha(p);check('-ffast-math' not in p.read_text() and '-ffp-contract=fast' not in p.read_text(),'compile response '+str(p))
    for p,contents in audit['response_files'].items():sha(p);check(Path(p).read_text()==contents,'link response '+p)
    check('libatlas_scalar_functions.a' in audit['link']+' '.join(audit['response_files'].values()),'common archive link '+str(folder));sha(build/'libatlas_scalar_functions.a')
    for obj in audit['objects']:
        check(sha(obj['path'])==obj['sha256'],'object '+obj['path'])
        if backend=='native':
            p=Path(obj['assembly']);check(sha(p)==obj['assembly_sha256'],'assembly '+str(p));check(not re.search(r'\b(?:v?fmadd\w*|v?fmsub\w*|v?fnmadd\w*|v?fnmsub\w*|fmla|fmls)\b',p.read_text()),'no saved native fused arithmetic '+str(p))
    for p,h in audit['artifacts'].items():check(sha(p)==h and h in (maxdurable if model=='maxwell' else durable).values(),'built/durable artifact '+p)
    if model=='norsand':
        raw=load(S/f'norsand-{backend}-results.json');check(raw['library_sha256']==next(iter(audit['artifacts'].values())) if backend=='native' else raw['module_sha256']==audit['artifacts'][str(build/'atlas_path_capability.mjs')] and raw['wasm_sha256']==audit['artifacts'][str(build/'atlas_path_capability.wasm')],'NorSand observed artifact '+backend)
        for p in (S/f'norsand-{backend}-generated').iterdir():check(sha(p)==sha(build/'generated'/p.name),'saved generated '+str(p))
    else:
        modeljson=load(build/'generated/models.json');expected=json.loads((src/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json').read_text());check(modeljson['models']==[expected],'exact Maxwell generated definition '+backend)
    counts[model+'_'+backend]=dict(commands=13,objects=13,artifacts=len(audit['artifacts']))
# Reproduce generated controlled-path source using only the frozen Python compiler.
selected=[src/p for p in ['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json']]
output=O/'norsand-generated-replay'
p=subprocess.run([sys.executable,'-B',str(src/'tools/generate_controlled_path.py'),'--output',str(output),*[str(x) for x in selected]],cwd=src,capture_output=True,text=True)
(O/'generation-replay.log').write_text(p.stdout+p.stderr);check(p.returncode==0,'pure Python generation')
for p in output.iterdir():
    for backend in ['native','wasm']:check(sha(p)==sha(S/f'norsand-{backend}-generated'/p.name),'regenerated source '+backend+' '+p.name)
obs=S/'maxwell-observations'
for p in obs.iterdir():check(sha(p)==sha(src/'docs/ingestion/maxwell-itasca900/integration-v1'/p.name),'durable Maxwell observation '+p.name)
for name in ['first.json','replay.json']:check(json.loads((src.parent/'cli'/name).read_text())==load(obs/'cli-creep-result.json'),'exact saved CLI import/replay '+name);sha(src.parent/'cli'/name)
report=load(obs/'native-transactions.json');check(report['CLI_replay_exact'] and report['recovery_pairs']==6 and report['actual_endpoint_restarts']==2 and json.loads(report['untimed_rejection_raw'])['ok'] is False,'CLI/transaction report')
for backend in ['native','wasm']:check(all(x['returncode']==0 for x in load(S/f'maxwell-{backend}-processes.json')),'all Maxwell process gates '+backend)
result=dict(identity='common-scalar-dependent-saved-independent-v1',pass_=not fail,failures=fail,source_files=518,unchanged_consumer_files=503,builds=counts,compiled_execution=False,checked_files=pins)
(O/'saved-audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checked_files'},indent=2));raise SystemExit(bool(fail))
