"""Pure bounded continuation; only coordinator calls observe. No build route."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
PLAN=json.loads((HERE/'plan.json').read_text());ACTUAL=Path(PLAN['output']);SOURCE=Path(PLAN['source'])
OLD=HERE.parent/'rate-restoration-qualification-plan-v3'
spec=importlib.util.spec_from_file_location('_accepted_C_v3',OLD/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('_accepted_C_commands_v3',OLD/'commands.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def verify_plan(manifest_sha,review_pin):
 assert not m.sys.flags.optimize
 assert m.sha(HERE/'manifest.json')==manifest_sha
 for row in json.loads((HERE/'manifest.json').read_text())['files']:
  p=Path(row['path']);assert not p.is_absolute()and'..'not in p.parts
  q=HERE/p;assert q.resolve()==q and not q.is_symlink();assert m.sha(q)==row['sha256']and q.stat().st_size==row['size_bytes']
 for row in json.loads((HERE/'predecessor-pins.json').read_text()):m.verify(row)
 m.verify(review_pin);r=json.loads(Path(review_pin['path']).read_text());m.independent_identities(r)
 assert r['accepted']is True and r['proposal_manifest_sha256']==manifest_sha
 m.verify_plan('4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812');m.assert_source(SOURCE)
def guard(pre,manifest_sha,review_pin):
 verify_plan(manifest_sha,review_pin)
 for p in [*pre['inputs'],*pre['build_tools'].values(),pre['node'],pre['python']]:m.verify(p)
 assert [m.pin(p)for p in m.source_files(SOURCE)]==pre['source_inventory']
 m.validate_execution_freeze(json.loads((Path(PLAN['actual'])/'execution-freeze.json').read_text()))
def observe(pre,phase,manifest_sha,review_pin):
 assert phase in ('extra-native','extra-wasm','extra-pair')
 def bound():guard(pre,manifest_sha,review_pin)
 bound()
 backend=phase.removeprefix('extra-')
 if backend!='native':
  prior='native'if backend=='wasm'else'wasm'
  assert json.loads((ACTUAL/('extra-'+prior)/'report.json').read_text())['status']=='passed'
  prior_receipt=json.loads((ACTUAL/('outer-extra-'+prior)/'receipt.json').read_text());assert prior_receipt['status']=='passed'and prior_receipt['returncode']==0 and prior_receipt['mandatory_reap']is True and prior_receipt['reaped_returncode']==0
 assert not (ACTUAL/('outer-'+phase)).exists() and not (ACTUAL/phase).exists()
 assert m.sha(c.OBSERVER)==c.OBSERVER_SHA
 spec=importlib.util.spec_from_file_location('_original_observer',c.OBSERVER);o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
 argv=[pre['node']['path'],str(HERE/'extras.mjs'),backend,PLAN['actual'],manifest_sha,review_pin['path'],review_pin['sha256']]
 primary=None
 try:
  result=o.observe(argv,str(SOURCE),ACTUAL/('outer-'+phase),env=c.closed_environment(),timeout=1800)
  assert result.returncode==0,'failure retained; stop subsequent phases'
  return result
 except BaseException as error:primary=error;raise
 finally:
  try:bound()
  except BaseException as error:
   p=ACTUAL/('post-binding-error-'+phase+'.json');assert not p.exists()
   p.write_text(json.dumps({'error':repr(error),'primary':repr(primary)if primary else None})+'\n')
   if primary is None:raise
