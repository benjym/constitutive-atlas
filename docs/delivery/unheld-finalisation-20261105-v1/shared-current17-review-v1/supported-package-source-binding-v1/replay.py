from pathlib import Path
import contextlib,io,json
O=Path(__file__).resolve().parent;A=O.parents[1]/'supported-package-source-binding-v1';code=(A/'check.py').read_text().replace("TemporaryDirectory(prefix='supported-source-pure-')","TemporaryDirectory(prefix='supported-source-pure-',dir=REVIEW)")
for name in ['node.stdout','node.stderr','checks.json']:code=code.replace("(P/'"+name+"').write_text","(REVIEW/'author-"+name+"').write_text")
out=io.StringIO();err=io.StringIO();status=0
try:
 with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):exec(compile(code,str(A/'check.py'),'exec'),{'__file__':str(A/'check.py'),'__name__':'independent_exact_replay','REVIEW':O})
except BaseException as e:status=1;err.write(repr(e)+'\n')
(O/'author-replay.stdout').write_text(out.getvalue());(O/'author-replay.stderr').write_text(err.getvalue());(O/'author-replay.json').write_text(json.dumps({'exit_code':status,'author_source_unchanged':True,'changes':'only temporary fixture/report output redirected into owned review','actual_compiled_browser_network':False},indent=2)+'\n');print(out.getvalue(),end='');raise SystemExit(status)
