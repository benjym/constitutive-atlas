from pathlib import Path
import contextlib,io,json
O=Path(__file__).resolve().parent;A=O.parents[1]/'package-final-source-binding-v1'
code=(A/'check.py').read_text().replace('dir=HERE','dir=REVIEW').replace("(HERE/'checks.json').write_text","(REVIEW/'author-replay-checks.json').write_text")
stdout=io.StringIO();stderr=io.StringIO();status=0
try:
 with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):exec(compile(code,str(A/'check.py'),'exec'),{'__file__':str(A/'check.py'),'__name__':'independent_exact_replay','REVIEW':O})
except BaseException as e:
 status=1;stderr.write(repr(e)+'\n')
(O/'author-replay.stdout').write_text(stdout.getvalue());(O/'author-replay.stderr').write_text(stderr.getvalue());(O/'author-replay.json').write_text(json.dumps({'exit_code':status,'author_source_unchanged':True,'changes':'only fixture/report paths redirected into reviewer-owned directory','actual_compiled_browser_network':False},indent=2)+'\n')
print(stdout.getvalue(),end='');raise SystemExit(status)
