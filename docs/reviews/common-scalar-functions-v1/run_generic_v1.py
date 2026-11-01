"""Fresh generic witnesses; unchanged independent assessors and frozen old inputs."""
from pathlib import Path
import json,gzip,subprocess,sys,importlib.util,hashlib
p=Path(__file__).parent;r=Path.cwd();src=p/'generic-regression-v2';q=src/'partition/prior-tresca';backend=sys.argv[1];out=p/'generic-results-v1';out.mkdir(exist_ok=True);b=Path('/private/tmp/atlas-common-scalar-functions-v1/generic-'+backend+'-v2')
def imported(name,f):
 s=importlib.util.spec_from_file_location(name,f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def collect(name,target,args=(),stdin=None):
 f=out/(backend+'-'+name+'.jsonl');assert not f.exists();cmd=([str(b/target)] if backend=='native' else ['node',str(b/(target+'.js'))])+list(args)
 with f.open('w') as stdout,(out/(backend+'-'+name+'.stderr')).open('w') as stderr:
  proc=subprocess.run(cmd,input=stdin,text=True,stdout=stdout,stderr=stderr)
 assert proc.returncode==0,(name,proc.returncode);return [json.loads(l) for l in f.read_text().splitlines()]
partition=collect('partition','atlas_partition_analytical');newton=collect('newton','atlas_partition_regression',['newton']);corpus=collect('corpus','atlas_partition_regression',['corpus'],(r/'docs/reviews/bounded-partition-retry-v1/corpus-requests.txt').read_text());history=collect('history','atlas_partition_regression',['history'],(q/'history-requests.txt').read_text());checks=collect('checks','atlas_partition_regression',['checks']);rounding=collect('rounding','atlas_partition_regression',['roundingchecks']);recorder=collect('recorder','atlas_recorded_retry_counter');spectral=collect('spectral','atlas_spectral_multiplicity',stdin=(src/'spectral/requests.txt').read_text())
pa=imported('common_partition',src/'partition/assess_partition.py').assess(partition);na=imported('common_newton',src/'partition/assess-regression.py').assess(newton);ca=imported('common_corpus',q/'assess_corpus.py').assess(corpus,json.loads((q/'corpus-requests.json').read_text())['requests'],json.loads(gzip.decompress((r/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes())),json.loads((q/'corpus-policy.json').read_text()));ha=imported('common_history',q/'assess_history.py').assess(history,json.loads((q/'history-inputs.json').read_text()),r);sa=imported('common_spectral',src/'spectral/assess.py').assess((out/(backend+'-spectral.jsonl')).read_text(),json.loads((src/'spectral/references.json').read_text()))
passed=pa['pass_'] and na['pass_'] and ca['qualification_pass'] and ha['qualification_pass'] and sa['pass'] and all(x['pass'] for x in checks+rounding+recorder)
report=dict(pass_=passed,backend=backend,partition=pa,newton=na,corpus=ca,history=ha,spectral=sa,checks=checks,rounding=rounding,recorder=recorder);f=out/(backend+'-assessment.json');assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n');print(backend,'generic gates',passed,flush=True);sys.exit(0 if passed else 1)
