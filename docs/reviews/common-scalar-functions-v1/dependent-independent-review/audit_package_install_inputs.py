"""Audit saved software controls and prospective preservation; no bundle/build calls."""
from pathlib import Path
import hashlib,json,collections
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;pins={};errors=[]
def digest(p):
    p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def load(p):digest(p);return json.loads(Path(p).read_text())
def check(ok,label):
    if not ok:errors.append(label)
proposal=load(B/'package-proposal-freeze-v4.json')
for name,h in proposal['files'].items():check(digest(R/name)==h,'proposal '+name)
for script,freeze in [('run_package_controls_v5.py','package-controls-freeze-v5.json'),('run_package_controls_addendum_v1.py','package-controls-addendum-freeze-v1.json')]:
    d=load(B/freeze);check(digest(B/script)==d['script_sha256'],'frozen control script '+script)
check(load(B/'package-controls-freeze-v5.json')['policy_sha256']==digest(O/'NEGATIVE_CONTROLS_V1.md'),'main original policy pin')
check(load(B/'package-controls-addendum-freeze-v1.json')['policy_sha256']==digest(O/'CONTROLS_ADDENDUM_V2.md'),'supplement original policy pin')
control_summary={};positive=0;manifest_files=0
for directory,count in [('package-controls-v5',75),('package-controls-addendum-v1',35)]:
    summary=load(B/directory/'summary.json');check(summary['status']=='passed' and summary['count']==len(summary['controls'])==count,'control coverage '+directory)
    labels=set()
    for row in summary['controls']:
        label=(row['model'],row['control']);check(label not in labels,'unique control '+str(label));labels.add(label)
        check(row['passed'] is True and bool(row['error'])==row['expected_rejection'],'control result '+str(label))
        dest=B/directory/(row['model']+'-'+row['control'])
        if not row['expected_rejection']:
            positive+=1;engine=dest/('engine-maxwell' if row['model']=='maxwell' else 'engine-path');mf=load(engine/'package-manifest.json')
            for p,h in mf['files'].items():check(digest(dest/p)==h,'positive package manifest '+str(dest/p));manifest_files+=1
            q=load(engine/'qualification.json')
            if 'independent_review' in q:
                reviewer=q['independent_review'];check(digest(engine/reviewer['path'])==reviewer['sha256'],'locally resolvable accepted review '+str(engine))
                a=load(engine/reviewer['path']);check(a['status']=='accepted' and a['binding']==q['binding'] and a['gates']==q['gates'] and a['reviewer_run']!=q['implementation_run'],'accepted copied bindings '+str(engine))
    control_summary[directory]=dict(count=count,by_model=dict(collections.Counter(x['model'] for x in summary['controls'])),positive=sum(not x['expected_rejection'] for x in summary['controls']))
# Isolated current source and restored build records match exact accepted inputs.
v=Path('/private/tmp/atlas-common-scalar-functions-v1/package-controls-root-v5')
maxmanifest=load(O/'build-local-v2/maxwell/source-manifest.json')
for p,h in maxmanifest['files'].items():check(digest(v/p)==h,'restored isolated Maxwell source '+p)
norq=load(O/'build-local-v1/norsand/controlled-path-qualification.json')
for p,h in norq['binding']['sources'].items():check(digest(v/p)==h,'restored isolated NorSand source '+p)
for model,version in [('maxwell',2),('norsand',1)]:
    for p in (O/f'build-local-v{version}'/model).iterdir():check(digest(B/'package-controls-v5'/(model+'-build')/p.name)==digest(p),'restored receipt '+model+'/'+p.name)
plan=load(B/'package-preservation-v1/preservation-plan.json');before=load(B/'package-preservation-v1/frozen/bindings-before.json');base=load(B/'package-install-base-preflight-v1.json')['existing_destination_bases']
check(len(base)==3 and set(base)==set(proposal['bases']) and base==proposal['bases'],'three exact proposal bases')
check(len(plan['bindings'])==46 and len(plan['planned_sidecars'])==16 and len(plan['document_pins'])==27,'46 bindings/16 maps/27 documents')
check(plan['document_pin_rollforwards']==[] and plan['original_documents_unchanged'] is True,'no document rollforward')
for p,h in base.items():
    # Record the canonical preserved old byte identity, not another live pin.
    check(hashlib.sha256((R/p).read_bytes()).hexdigest()==h,'current unchanged base '+p)
    archive=R/'catalogue/source-snapshots'/h/p;check(digest(archive)==h,'canonical old base '+p)
for p,h in plan['document_pins'].items():check(digest(R/p)==h,'original document '+p)
maps={}
for target,row in plan['planned_sidecars'].items():
    check(target.endswith('/source-archive-map.json') and not Path(target).is_absolute() and '..' not in Path(target).parts,'safe sidecar '+target)
    old=R/target;check((hashlib.sha256(old.read_bytes()).hexdigest() if old.exists() else None)==row['original_sha256'],'sidecar current base '+target)
    proposed=R/row['proposed_path'];check(digest(proposed)==row['proposed_sha256'],'proposed sidecar '+target);m=load(proposed);maps[target]=m
    check(m['version']=='immutable-source-archive-map-0.1','map format '+target)
    if old.exists():
        oldm=json.loads(old.read_text());check(all(m['documents'].get(p)==h for p,h in oldm['documents'].items()),'old document pins retained '+target)
        check(all(e in m['entries'] for e in oldm['entries']),'old archive entries retained '+target)
        check(digest(R/'catalogue/source-snapshots'/row['original_sha256']/target)==row['original_sha256'],'old sidecar canonical archive '+target)
    for entry in m['entries']:check(digest(R/entry['archived_path'])==entry['sha256'],'all proposed map entries '+entry['archived_path'])
bindings={(x['document'],x['original_path'],x['sha256']) for x in plan['bindings']}
for row in plan['bindings']:
    check(digest(R/row['archived_path'])==row['sha256'],'binding archive '+row['archived_path'])
    m=maps[str(Path(row['document']).parent/'source-archive-map.json')]
    check(m['documents'][row['document']]==plan['document_pins'][row['document']],'exact mapped document '+row['document'])
    check({k:row[k] for k in ['original_path','sha256','archived_path']} in m['entries'],'exact mapping entry '+row['original_path'])
for row in before['primary_references']:
    if row['expected_equals_current_live']:check((row['document'],row['original_path'],row['sha256']) in bindings,'all live primary references preserved '+row['document'])
for row in before['secondary_source_map_references']:
    target=row['original_path']
    if target in plan['planned_sidecars'] and not row['document'].endswith('/source-archive-map.json') and row['sha256']==plan['planned_sidecars'][target]['original_sha256']:
        check((row['document'],target,row['sha256']) in bindings,'reverse map pin preserved '+row['document'])
digest(B/'apply_package_install_v1.py');digest(B/'prepare_package_preservation_v1.py')
result=dict(identity='common-scalar-package-controls-and-prospective-install-independent-v1',pass_=not errors,failures=errors,controls=control_summary,positive_packages=positive,positive_manifest_files_checked=manifest_files,preservation=dict(bindings=46,sidecars=16,documents=27,rollforwards=0),compiled_execution=False,checked_files=pins)
(O/'package-install-audit-results-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checked_files'},indent=2));raise SystemExit(bool(errors))
