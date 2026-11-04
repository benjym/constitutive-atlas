"""Pure versioned-route and unchanged-observer pin regression; no real child."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,tempfile
from types import SimpleNamespace
sys.dont_write_bytecode=True

def run(L,check):
 P=Path(__file__).resolve().parent;B=L.B;packet=B/'baseline-five-portable-export-executable-v1'
 check('accepted exporter proposal exact',L.sha(packet/'manifest.json')=='3099f52ed76e1788a27c2b9155f7b55fd22725e3862e91d74cddd7d07c4aa460')
 review=B/'baseline-five-portable-export-executable-review-v1';check('genuine exporter review exact',L.sha(review/'decision.json')=='5fcbb3f2d7f2db00992643e8132ed3b629f88931818ec30f1796f404c6111e4a')
 source=ast.parse((packet/'proposed/tools/baseline_ci_package_portable_host_v3.py').read_text())
 call=next(n for n in ast.walk(source)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='child'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='source-export')
 argv=eval(compile(ast.Expression(call.args[1]),'<actual frozen exporter argv>','eval'),{'sys':SimpleNamespace(executable='/manufactured/python'),'root':Path('/manufactured/source'),'EXPORT_PACKET':'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-portable-export-executable-v1','source':Path('/manufactured/export'),'observations':Path('/manufactured/observations'),'spec':{'revision':L.POLICY['revision']}})
 check('actual v3 wrapper selects absolute Git argument',argv[3:5]==['--git-executable','/usr/bin/git']and argv[2].endswith('baseline-five-portable-export-executable-v1/bootstrap_source.py'))
 observer=B/'baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py';check('real unchanged observer pin',L.sha(observer)==L.POLICY['observer_sha256'])
 spec=importlib.util.spec_from_file_location('plan_v2_unchanged_observer',observer);O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)
 with tempfile.TemporaryDirectory(prefix='plan-v2-export-pin-',dir=P)as tmp:
  r=Path(tmp).resolve();git=r/'absolute-qualified-git';git.write_bytes(b'manufactured executable');git.chmod(0o755);calls=[]
  def fake_popen(*a,**k):calls.append((a,k));raise OSError('manufactured launch sentinel')
  try:O.observe([str(git),'--manufactured'],r,r/'proof',_popen=fake_popen)
  except OSError as error:check('real observer reaches injected absolute launch',str(error)=='manufactured launch sentinel'and len(calls)==1)
  else:raise AssertionError('expected manufactured sentinel')
  check('real observer retains closed raw failure',all((r/'proof'/name).is_file()for name in['receipt.json','stdout.raw','stderr.raw']))
 check('new source size saved-only derivation',json.loads((P/'source-size-derivation.json').read_text())['source_logical_bytes']==L.POLICY['source_logical_bytes'])
