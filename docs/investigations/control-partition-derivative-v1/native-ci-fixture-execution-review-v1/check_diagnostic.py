"""Read-only exact instrumentation review; no C++ compilation/artifact calls."""
import hashlib,json,re
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'native-fixture-fd-diagnostic-v1';S=Path('/private/tmp/atlas-md1997-native-fixture-fd-diag-v1/source');P=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source');read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('author manifest exact',h(D/'manifest.json')=='add4a0a7a6e49e43e3226644052ae9e26f2ea942f5018de2d237d0e013bf4c2d');m=read(D/'manifest.json');m=m.get('files',m)
for n,v in m.items():ck('packet '+n,h(D/n)==v)
f=read(D/'source-freeze.json')['files'];old=read(C/'native-ci-fixture-composition-v3/source-freeze.json')['files'];ck('exact594names',len(f)==594 and set(f)==set(old));ck('only test_solver differs',{n for n in f if f[n]!=old[n]}=={'tests/test_solver.cpp'})
ck('complete source inventory',set(f)=={p.relative_to(S).as_posix()for p in S.rglob('*')if p.is_file()})
for n,v in f.items():ck('diagnostic source '+n,h(S/n)==v);ck('parent unchanged '+n,h(P/n)==old[n])
text=(S/'tests/test_solver.cpp').read_text();start=text.index('                if(!(std::isfinite(ad)');end=text.index('                require(std::isfinite(ad)',start);addition=text[start:end]
ck('inverse removal exact source',text[:start]+text[end:]==(P/'tests/test_solver.cpp').read_text())
condition=addition.split('if(!(',1)[1].split(')){',1)[0];original=text[end:].split('require(',1)[1].split(',"MD AD/FD',1)[0];ck('diagnostic condition original gate exact',condition==original)
ck('no material mutation statements',not any(x in re.sub(r'"(?:[^"\\]|\\.)*"','',addition) for x in ['evaluate_model','integrate(', 'plus[','minus[','fd[level][i]=','ad=','step=','r[i].d']))
ck('only stderr logging',addition.count('std::cerr')>=7 and 'MD_FD_DIAGNOSTIC' in addition)
p=read(D/'plan.json');ck('one single-target serial build',p['commands'][1][-4:]==['--target','atlas_numerical_tests','--parallel','1']);ck('3commands configure/build/singlecall',len(p['commands'])==3 and len(p['commands'][2])==1);ck('expected rejection1',p['expected_last_exit']==1);ck('unoptimized newselector identity',p['env']=={'PYTHONOPTIMIZE':'0','PYTHONDONTWRITEBYTECODE':'1','ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-source-admissible-v1'})
print(json.dumps({'identity':'independent-native-fixture-fd-diagnostic-v1-review','decision':'accepted-prospective-failure-localization-only','author_manifest':h(D/'manifest.json'),'checks':len(checks),'check_names':checks,'inverse_removal_exact':True,'arithmetic_state_steps_gates_unchanged':True,'source_files':594,'expected_material_exit':1,'compiled_calls':0,'builds':0,'scientific_or_numerical_pass_claim':False},indent=2))
