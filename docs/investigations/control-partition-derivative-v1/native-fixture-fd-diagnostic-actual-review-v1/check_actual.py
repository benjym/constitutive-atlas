"""Read-only diagnostic archive audit; no artifact calls, no author mains."""
import sys
sys.dont_write_bytecode=True
import datetime,hashlib,json,tarfile,re,math
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'native-fixture-fd-diagnostic-execution-v1';read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('execution manifest exact',sha((D/'manifest.json').read_bytes())=='07170ea87de97c23330b3e6a138e4312ac88acbc4cee650dfb4437cb09d9f8ba')
for n,v in read(D/'manifest.json')['files'].items():ck('public '+n,sha((D/n).read_bytes())==v)
a=read(D/'archive-receipt.json');archive=D/a['archive'];ck('archive size/hash',archive.stat().st_size==a['bytes']and sha(archive.read_bytes())==a['sha256']);blobs={}
with tarfile.open(archive,'r:gz')as tar:
 members=tar.getmembers();ck('exact932regularuniquemembers',len(members)==len(a['members'])==len({x.name for x in members})==932 and all(x.isfile()and not Path(x.name).is_absolute()and '..'not in Path(x.name).parts for x in members));ck('archive exact names',{x.name for x in members}==set(a['members']))
 for x in members:b=tar.extractfile(x).read();ck('member '+x.name,sha(b)==a['members'][x.name]);blobs[x.name]=b
for n in ['freeze.json','run.py']+[f'{i}/{name}' for i in range(3) for name in ['process.json','stdout','stderr']]:ck('public/archive byte link '+n,(D/n).read_bytes()==blobs['execution/'+n])
f=read(C/'native-fixture-fd-diagnostic-v1/source-freeze.json')['files'];ck('source594allretained',len(f)==594 and {n.removeprefix('source/')for n in blobs if n.startswith('source/')}==set(f))
for n,v in f.items():ck('frozen source '+n,sha(blobs['source/'+n])==v)
# Reconfirm exact logging-only delta against frozen original composition.
original=read(C/'native-ci-fixture-composition-v3/source-freeze.json')['files'];ck('onlyfixtureloggingchanged',{n for n in f if f[n]!=original[n]}=={'tests/test_solver.cpp'});text=blobs['source/tests/test_solver.cpp'].decode();start=text.index('                if(!(std::isfinite(ad)');end=text.index('                require(std::isfinite(ad)',start);ck('inverse logging exact original',sha((text[:start]+text[end:]).encode())==original['tests/test_solver.cpp'])
plan=read(C/'native-fixture-fd-diagnostic-v1/plan.json');tool=read(C/'native-ci-fixture-execution-v1/toolchain.json');last=None;rows=[]
for i,argv in enumerate(plan['commands']):
 r=read(D/str(i)/'process.json');ck('exact process '+str(i),r['argv']==argv and r['cwd']==plan['source']and r['env_changes']=={**tool['environment'],**plan['env'],'PATH':tool['PATH']})
 for key in ['stdout','stderr']:ck('raw '+str(i)+key,sha((D/str(i)/key).read_bytes())==r[key+'_sha256'])
 ck('expected outcomes '+str(i),r['returncode']==[0,0,1][i]and r['status']=='observed'and r['source_tool_postcheck']is True)
 begin=datetime.datetime.fromisoformat(r['start']);endtime=datetime.datetime.fromisoformat(r['end']);ck('serial '+str(i),begin<=endtime and(last is None or begin>=last));last=endtime;rows.append({'index':i,'returncode':r['returncode'],'start':r['start'],'end':r['end']})
for n,v in read(D/'freeze.json')['inputs'].items():ck('frozen input '+n,sha(Path(n).read_bytes())==v)
for n,v in tool['files'].items():p=Path(n);ck('tool post '+n,str(p.resolve())==v['realpath']and sha(p.read_bytes())==v['sha256'])
raw=(D/'2/stderr').read_text();line=raw.splitlines()[0];match=re.fullmatch(r'MD_FD_DIAGNOSTIC row=(\d+) level=(\d+) h=([^ ]+) ad=([^ ]+) fd=([^ ]+) rp=([^ ]+) rm=([^ ]+) direction=([^ ]+) state=([^ ]+) scales=(.+)',line);assert match
row,level=map(int,match.group(1,2));values={name:float(match.group(i))for i,name in enumerate(['h','ad','fd','rp','rm'],3)};direction=[float(x)for x in match.group(8).rstrip(',').split(',')];state=[float(x)for x in match.group(9).rstrip(',').split(',')];scales=[float(x)for x in match.group(10).rstrip(',').split(',')];ck('exact firstrow0column8level0',row==level==0 and len(direction)==14 and direction==[float(i==8)for i in range(14)]);ck('finite complete state/scales',len(state)==len(scales)==14 and all(math.isfinite(x)for x in state+scales+list(values.values())));ck('unchanged failure retained',raw.splitlines()[1]=='MD AD/FD residual Jacobian mismatch'and len(raw.splitlines())==2)
ck('actual binade bothendpoints',all(32768<=abs(values[k])<65536 for k in ['rp','rm']));ck('stored arithmetic reproduces actual secant',(values['rp']-values['rm'])/(2*values['h'])==values['fd'])
print(json.dumps({'identity':'independent-md1997-actual-fd-diagnostic-review','checks':len(checks),'check_names':checks,'archive_members':932,'source_files':594,'tool_files':len(tool['files']),'processes':rows,'actual':{'row':row,'column':8,'level':level,**values,'direction':direction,'state':state,'scales':scales},'review_compiled_calls':0,'review_builds':0,'diagnostic_expected_failure_confirmed':True,'positive_numerical_qualification':'FAIL'},indent=2))
